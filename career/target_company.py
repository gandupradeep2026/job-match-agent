from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TargetCompany:
    """One structured target-company record."""

    id: int | None = None

    company_name: str = ""
    priority: str = "B — Strong Target"
    status: str = "Researching"

    industry: str = ""

    headquarters: str = ""
    germany_locations: list[str] = field(
        default_factory=list
    )

    target_roles: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    careers_url: str = ""
    company_url: str = ""
    linkedin_url: str = ""

    contact_name: str = ""
    contact_role: str = ""
    contact_email: str = ""
    contact_linkedin: str = ""

    why_company_en: str = ""
    why_company_de: str = ""

    why_fit_en: str = ""
    why_fit_de: str = ""

    next_action_en: str = ""
    next_action_de: str = ""

    notes_en: str = ""
    notes_de: str = ""

    last_researched_date: str = ""

    created_at: str = ""
    updated_at: str = ""

    def display_name(self) -> str:
        return (
            self.company_name.strip()
            or "Target Company"
        )

    def has_required_fields(self) -> bool:
        return bool(
            self.company_name.strip()
        )
