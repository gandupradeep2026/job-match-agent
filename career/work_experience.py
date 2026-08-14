from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkExperience:
    """One structured employment record."""

    id: int | None = None
    employer: str = ""
    job_title_en: str = ""
    job_title_de: str = ""
    location: str = ""
    country: str = ""
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    employment_type: str = ""
    description_en: str = ""
    description_de: str = ""
    achievements_en: list[str] = field(default_factory=list)
    achievements_de: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    verified: bool = False
    created_at: str = ""
    updated_at: str = ""

    def display_title(self) -> str:
        return (
            self.job_title_en.strip()
            or self.job_title_de.strip()
            or "Work Experience"
        )

    def has_required_fields(self) -> bool:
        return bool(
            self.employer.strip()
            and (
                self.job_title_en.strip()
                or self.job_title_de.strip()
            )
            and self.start_date.strip()
        )
