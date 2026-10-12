from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import json

from src.meeting_assistant import MeetingAssistant

app = FastAPI(title="AI Meeting Assistant API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(transcript: str = Form(...), prompt_version: int = Form(3)):
    if not transcript.strip():
        return JSONResponse({"error": "Transcript is empty."}, status_code=400)
    try:
        assistant = MeetingAssistant()
        result = assistant.process(transcript, prompt_version=prompt_version)
        return JSONResponse(json.loads(result.model_dump_json()))
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Analysis failed: {e}"}, status_code=500)
