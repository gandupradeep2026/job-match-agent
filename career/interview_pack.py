from __future__ import annotations

from dataclasses import dataclass, field

from career.interview_preparation import (
    BehavioralAnswer,
    PreparedAnswer,
)


@dataclass
class CompleteInterviewPack:
    language: str
    target_role: str
    company_name: str = ""

    elevator_pitch_30: str = ""
    elevator_pitch_60: str = ""
    elevator_pitch_90: str = ""

    tell_me_about_yourself: PreparedAnswer | None = None
    why_this_role: PreparedAnswer | None = None
    why_this_company: PreparedAnswer | None = None
    strengths: PreparedAnswer | None = None
    weakness: PreparedAnswer | None = None

    behavioral_answers: list[BehavioralAnswer] = field(
        default_factory=list
    )

    technical_focus: list[str] = field(
        default_factory=list
    )

    employer_questions: list[str] = field(
        default_factory=list
    )

    preparation_checklist: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )
