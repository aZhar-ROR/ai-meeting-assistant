import os
import json
import re
import time
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv

from src.schemas import MeetingOutput
from src.prompts import get_prompt

load_dotenv()

MAX_RETRIES = 4
RETRY_DELAY = 5  # seconds, doubled each attempt


class MeetingAssistant:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.8-flash"):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not set. Add it to .env or pass api_key=")
        self.client = genai.Client(api_key=key)
        self.model_name = model

    def _extract_json(self, text: str) -> dict:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if match:
            text = match.group(1)
        return json.loads(text)

    def _call_with_retry(self, prompt: str) -> str:
        delay = RETRY_DELAY
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=4096,
                    ),
                )
                return response.text
            except ClientError as e:
                code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
                if code in (429, 503) and attempt < MAX_RETRIES:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise

    def process(self, transcript: str, prompt_version: int = 3) -> MeetingOutput:
        prompt = get_prompt(version=prompt_version, transcript=transcript)
        text = self._call_with_retry(prompt)
        raw = self._extract_json(text)
        return MeetingOutput(**raw)

    def process_file(self, path: str, prompt_version: int = 3) -> MeetingOutput:
        """Load a transcript file and process it."""
        transcript = Path(path).read_text(encoding="utf-8")
        return self.process(transcript, prompt_version=prompt_version)

    def format_output(self, result: MeetingOutput) -> str:
        """Format MeetingOutput as a readable text report."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"MEETING REPORT: {result.meeting_title}")
        lines.append("=" * 60)

        if result.date:
            lines.append(f"Date: {result.date}")
        if result.duration:
            lines.append(f"Duration: {result.duration}")
        if result.attendees:
            names = ", ".join(
                f"{a.name}" + (f" ({a.role})" if a.role else "") for a in result.attendees
            )
            lines.append(f"Attendees: {names}")
        if result.sentiment:
            lines.append(f"Tone: {result.sentiment.capitalize()}")

        lines.append("\nSUMMARY")
        lines.append("-" * 40)
        lines.append(result.summary)

        if result.key_decisions:
            lines.append("\nKEY DECISIONS")
            lines.append("-" * 40)
            for i, d in enumerate(result.key_decisions, 1):
                lines.append(f"{i}. {d.decision}")
                if d.rationale:
                    lines.append(f"   Rationale: {d.rationale}")
                if d.decided_by:
                    lines.append(f"   Decided by: {d.decided_by}")

        if result.action_items:
            lines.append("\nACTION ITEMS")
            lines.append("-" * 40)
            for i, item in enumerate(result.action_items, 1):
                lines.append(f"\nAction Item #{i}:")
                lines.append(f"  Task:     {item.task}")
                lines.append(f"  Owner:    {item.owner}")
                lines.append(f"  Deadline: {item.deadline or 'TBD'}")
                lines.append(f"  Priority: {item.priority.value}")
                lines.append(f"  Status:   {item.status.value}")

        if result.open_questions:
            lines.append("\nOPEN QUESTIONS")
            lines.append("-" * 40)
            for i, q in enumerate(result.open_questions, 1):
                lines.append(f"{i}. {q.question}")
                if q.raised_by:
                    lines.append(f"   Raised by: {q.raised_by}")
                if q.context:
                    lines.append(f"   Context: {q.context}")

        if result.follow_up_items:
            lines.append("\nFOLLOW-UP ITEMS")
            lines.append("-" * 40)
            for i, f in enumerate(result.follow_up_items, 1):
                lines.append(f"{i}. {f.item}")
                if f.assigned_to:
                    lines.append(f"   Assigned to: {f.assigned_to}")
                if f.target_date:
                    lines.append(f"   Target date: {f.target_date}")

        if result.discussion_topics:
            lines.append("\nDISCUSSION TOPICS (No Action/Decision)")
            lines.append("-" * 40)
            for t in result.discussion_topics:
                lines.append(f"  • {t}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def save_output(self, result: MeetingOutput, output_dir: str = "outputs") -> dict:
        """Save results as both JSON and formatted text."""
        Path(output_dir).mkdir(exist_ok=True)
        safe_name = re.sub(r"[^\w\s-]", "", result.meeting_title).strip().replace(" ", "_").lower()

        json_path = Path(output_dir) / f"{safe_name}.json"
        txt_path = Path(output_dir) / f"{safe_name}.txt"

        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        txt_path.write_text(self.format_output(result), encoding="utf-8")

        return {"json": str(json_path), "txt": str(txt_path)}
