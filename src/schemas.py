from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ActionStatus(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"
    blocked = "Blocked"


class Priority(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class ActionItem(BaseModel):
    task: str = Field(description="Clear description of the task to be done")
    owner: str = Field(description="Person responsible for the action")
    deadline: Optional[str] = Field(None, description="Due date or timeframe")
    status: ActionStatus = Field(default=ActionStatus.pending)
    priority: Priority = Field(default=Priority.medium)


class Decision(BaseModel):
    decision: str = Field(description="What was decided")
    rationale: Optional[str] = Field(None, description="Why this decision was made")
    decided_by: Optional[str] = Field(None, description="Who made the decision")


class OpenQuestion(BaseModel):
    question: str = Field(description="Unresolved question from the meeting")
    raised_by: Optional[str] = Field(None, description="Who raised the question")
    context: Optional[str] = Field(None, description="Context around the question")


class FollowUpItem(BaseModel):
    item: str = Field(description="Topic or item requiring follow-up")
    assigned_to: Optional[str] = Field(None, description="Person responsible for follow-up")
    target_date: Optional[str] = Field(None, description="When follow-up should happen")


class Attendee(BaseModel):
    name: str
    role: Optional[str] = None


class MeetingOutput(BaseModel):
    meeting_title: str = Field(description="Title or subject of the meeting")
    date: Optional[str] = Field(None, description="Date of the meeting if mentioned")
    duration: Optional[str] = Field(None, description="Duration of the meeting if mentioned")
    attendees: List[Attendee] = Field(default_factory=list)
    summary: str = Field(description="Concise 3-5 sentence summary of the meeting")
    key_decisions: List[Decision] = Field(default_factory=list, description="Concrete decisions made")
    action_items: List[ActionItem] = Field(default_factory=list, description="Tasks assigned to specific people")
    open_questions: List[OpenQuestion] = Field(default_factory=list, description="Unresolved questions")
    follow_up_items: List[FollowUpItem] = Field(default_factory=list, description="Items needing follow-up")
    discussion_topics: List[str] = Field(default_factory=list, description="Topics discussed but no decision/action")
    sentiment: Optional[str] = Field(None, description="Overall meeting tone: productive/neutral/tense")
