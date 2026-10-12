# AI Meeting Assistant

An AI system powered by **Google Gemini** that converts raw meeting transcripts into structured, actionable intelligence — distinguishing between things that were *discussed* vs things that were *decided* or *assigned*.

---

## Features

- **Meeting Summary** — concise 3–5 sentence executive summary
- **Key Decisions** — only concrete agreed-upon resolutions (not discussions)
- **Action Items** — with owner, deadline, priority, and status
- **Open Questions** — unresolved questions raised during the meeting
- **Follow-up Items** — topics needing revisitation
- **Discussion Topics** — things talked about with no outcome
- **Attendee Extraction** — names and roles
- **Sentiment Analysis** — overall meeting tone
- **Structured JSON output** validated with Pydantic
- **Evaluation scoring** — automated quality assessment
- **3 prompt iterations** — showing evolution of the extraction prompt

---

## Project Structure

```
ai-meeting-assistant/
├── main.py                    # Entry point
├── requirements.txt
├── .env.example
├── src/
│   ├── meeting_assistant.py   # Core Gemini integration
│   ├── schemas.py             # Pydantic output schemas
│   ├── prompts.py             # 3 prompt iterations
│   └── evaluator.py          # Automated evaluation
├── transcripts/
│   ├── transcript_1_product_review.txt
│   ├── transcript_2_sprint_planning.txt
│   ├── transcript_3_quarterly_business_review.txt
│   ├── transcript_4_hiring_panel.txt
│   └── transcript_5_incident_postmortem.txt
├── outputs/                   # Generated JSON + TXT reports
└── tests/
    └── test_meeting_assistant.py
```

---

## Setup

### 1. Clone and install

```bash
cd ai-meeting-assistant
pip install -r requirements.txt
```

### 2. Configure your Gemini API key

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

Get your key at: [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Usage

### Process all 5 transcripts

```bash
python main.py
```

### Process a single transcript

```bash
python main.py --file transcripts/transcript_1_product_review.txt
```

### Compare all 3 prompt versions on the same transcript

```bash
python main.py --compare-prompts
```

### Use a different Gemini model

```bash
python main.py --model gemini-1.5-pro
```

---

## Example Output

```
============================================================
MEETING REPORT: Q4 Product Review
============================================================
Date: October 10, 2026
Attendees: Priya (Product Manager), Rahul (Engineering Lead), Sara (Design)
Tone: Productive

SUMMARY
----------------------------------------
The Q4 product review covered the dashboard redesign progress, mobile app
performance issues, and launch planning. The team agreed to cut the advanced
filter feature from Q4 scope and set October 24th as the final build deadline.
Key open issue is whether the mobile memory problem will be resolved before launch.

KEY DECISIONS
----------------------------------------
1. Final build deadline is October 24th
2. Advanced filter feature deferred to Q1
   Rationale: Not feasible within the Q4 timeline without scope cut

ACTION ITEMS
----------------------------------------

Action Item #1:
  Task:     Fix spacing issues in card components per Figma specs
  Owner:    Aditya
  Deadline: Wednesday
  Priority: Medium
  Status:   Pending

Action Item #2:
  Task:     Prepare Q4 sales report
  Owner:    Rahul
  Deadline: Friday
  Priority: High
  Status:   Pending
...

OPEN QUESTIONS
----------------------------------------
1. Should the launch be delayed if the mobile memory issue isn't resolved?
   Context: Affects 30% of users on older Android devices
```

---

## Output Schema

Defined in [`src/schemas.py`](src/schemas.py) using Pydantic:

```python
class MeetingOutput(BaseModel):
    meeting_title: str
    date: Optional[str]
    duration: Optional[str]
    attendees: List[Attendee]
    summary: str
    key_decisions: List[Decision]
    action_items: List[ActionItem]      # task, owner, deadline, priority, status
    open_questions: List[OpenQuestion]
    follow_up_items: List[FollowUpItem]
    discussion_topics: List[str]
    sentiment: Optional[str]
```

Results are saved as both `.json` (machine-readable) and `.txt` (human-readable) in `outputs/`.

---

## Prompt Iterations

Three progressively refined prompts are in [`src/prompts.py`](src/prompts.py):

| Version | Key improvement |
|---------|----------------|
| V1 | Basic extraction — simple JSON request |
| V2 | Added explicit distinction: discussed vs decided vs assigned |
| V3 | Full production prompt — detailed rules per field, CRITICAL DISTINCTIONS section, extraction rules, JSON schema in prompt |

Run `python main.py --compare-prompts` to see the quality difference across versions on the same transcript.

---

## Evaluation

Each run is automatically scored across four dimensions:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Completeness | 30% | Are summary, title, decisions, and action items populated? |
| Action Item Quality | 35% | Do action items have a named owner and deadline? |
| Decision Specificity | 20% | Are decisions substantive (not one-word)? |
| Question Resolution | 15% | Ratio of resolved to open items |

Run tests:

```bash
pytest tests/ -v
```

---

## The Core Challenge: Discussed vs Decided

The system explicitly distinguishes:

| Category | Trigger phrases | Destination |
|----------|----------------|-------------|
| Discussion Topic | "we talked about", "we mentioned", "someone brought up" | `discussion_topics` |
| Key Decision | "we decided", "we agreed", "let's go with", "it was concluded" | `key_decisions` |
| Action Item | Named person + specific task + explicit assignment | `action_items` |
| Open Question | Question raised with no answer | `open_questions` |

This prevents common mistakes like treating every topic as an action item or every suggestion as a decision.

---

## Transcripts Included

| # | File | Meeting Type |
|---|------|-------------|
| 1 | `transcript_1_product_review.txt` | Product review with launch planning |
| 2 | `transcript_2_sprint_planning.txt` | Agile sprint planning |
| 3 | `transcript_3_quarterly_business_review.txt` | Executive QBR with financials |
| 4 | `transcript_4_hiring_panel.txt` | Candidate debrief and hiring decision |
| 5 | `transcript_5_incident_postmortem.txt` | Production incident postmortem |
