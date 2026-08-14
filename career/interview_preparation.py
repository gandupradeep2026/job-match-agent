from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InterviewPreparationRequest:
    language: str
    target_role: str
    company_id: int | None = None

    development_area: str = ""
    improvement_action: str = ""
    improvement_evidence: str = ""


@dataclass
class PreparedAnswer:
    question: str
    answer: str
    source_summary: str = ""
    warnings: list[str] = field(
        default_factory=list
    )


@dataclass
class BehavioralAnswer:
    category: str
    story_title: str
    question: str
    answer: str


@dataclass
class InterviewPreparationPack:
    language: str
    target_role: str
    company_name: str = ""

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

    warnings: list[str] = field(
        default_factory=list
    )
