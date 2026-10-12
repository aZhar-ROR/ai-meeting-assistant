"""
Evaluation module — scores extracted meeting data for completeness and quality.
"""
from dataclasses import dataclass, field
from typing import List
from src.schemas import MeetingOutput


@dataclass
class EvaluationResult:
    transcript_name: str
    completeness_score: float        # 0-1: did we fill the key fields?
    action_item_quality: float       # 0-1: do action items have owner + deadline?
    decision_specificity: float      # 0-1: are decisions non-trivial?
    question_resolution: float       # 0-1: ratio of open vs resolved items
    overall_score: float = field(init=False)
    notes: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.overall_score = round(
            (self.completeness_score * 0.3
             + self.action_item_quality * 0.35
             + self.decision_specificity * 0.2
             + self.question_resolution * 0.15),
            3,
        )


def evaluate(result: MeetingOutput, name: str = "unnamed") -> EvaluationResult:
    notes = []

    # Completeness: are major fields populated?
    populated = sum([
        bool(result.meeting_title),
        bool(result.summary),
        bool(result.key_decisions),
        bool(result.action_items),
        len(result.summary.split()) >= 20,   # summary has substance
    ])
    completeness = populated / 5

    # Action item quality: owner + deadline present
    if result.action_items:
        quality_hits = sum(
            1 for a in result.action_items
            if a.owner and a.owner.lower() not in ("tbd", "unknown", "n/a", "")
        )
        deadline_hits = sum(
            1 for a in result.action_items
            if a.deadline and a.deadline.upper() != "TBD"
        )
        ai_quality = (quality_hits + deadline_hits) / (2 * len(result.action_items))
        if quality_hits < len(result.action_items):
            notes.append(f"{len(result.action_items) - quality_hits} action item(s) missing an owner")
    else:
        ai_quality = 0.5  # neutral if no action items (not always bad)
        notes.append("No action items detected")

    # Decision specificity: non-trivial decisions (>5 words each)
    if result.key_decisions:
        specific = sum(1 for d in result.key_decisions if len(d.decision.split()) > 5)
        decision_score = specific / len(result.key_decisions)
        if decision_score < 1:
            notes.append("Some decisions are too brief/vague")
    else:
        decision_score = 0.4
        notes.append("No key decisions detected")

    # Question resolution ratio — fewer open questions relative to decisions is better
    total_items = len(result.action_items) + len(result.key_decisions) + len(result.open_questions)
    if total_items > 0:
        resolution = 1 - (len(result.open_questions) / total_items)
    else:
        resolution = 0.5

    return EvaluationResult(
        transcript_name=name,
        completeness_score=round(completeness, 3),
        action_item_quality=round(ai_quality, 3),
        decision_specificity=round(decision_score, 3),
        question_resolution=round(resolution, 3),
        notes=notes,
    )


def print_evaluation(ev: EvaluationResult) -> None:
    print(f"\n{'=' * 50}")
    print(f"EVALUATION: {ev.transcript_name}")
    print(f"{'=' * 50}")
    print(f"  Completeness:         {ev.completeness_score:.0%}")
    print(f"  Action Item Quality:  {ev.action_item_quality:.0%}")
    print(f"  Decision Specificity: {ev.decision_specificity:.0%}")
    print(f"  Question Resolution:  {ev.question_resolution:.0%}")
    print(f"  ──────────────────────────────")
    print(f"  OVERALL SCORE:        {ev.overall_score:.0%}")
    if ev.notes:
        print(f"  Notes:")
        for n in ev.notes:
            print(f"    ⚠ {n}")
    print()
