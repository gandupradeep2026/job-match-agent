from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CareerApplicationLink:
    """Career-preparation metadata attached to one tracked application."""

    application_id: int

    target_company_id: int | None = None
    career_target_role: str = ""

    preparation_stage: str = "Not Started"

    tailored_cv_ready: bool = False
    interview_pack_ready: bool = False

    interview_pack_language: str = ""

    career_next_action: str = ""
    career_notes: str = ""

    last_career_sync_at: str = ""

    def is_linked_to_company(self) -> bool:
        return (
            self.target_company_id
            is not None
        )

    def is_interview_ready(self) -> bool:
        return bool(
            self.interview_pack_ready
            and self.preparation_stage
            in {
                "Interview Prep",
                "Interview Ready",
            }
        )
