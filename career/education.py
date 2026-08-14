from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EducationRecord:
    """One structured education record."""

    id: int | None = None

    institution: str = ""

    degree_en: str = ""
    degree_de: str = ""

    field_of_study_en: str = ""
    field_of_study_de: str = ""

    location: str = ""
    country: str = ""

    start_date: str = ""
    end_date: str = ""
    is_current: bool = False

    grade: str = ""

    thesis_title_en: str = ""
    thesis_title_de: str = ""

    description_en: str = ""
    description_de: str = ""

    achievements_en: list[str] = field(
        default_factory=list
    )
    achievements_de: list[str] = field(
        default_factory=list
    )

    verified: bool = False

    created_at: str = ""
    updated_at: str = ""

    def display_title(self) -> str:
        return (
            self.degree_en.strip()
            or self.degree_de.strip()
            or self.field_of_study_en.strip()
            or self.field_of_study_de.strip()
            or "Education"
        )

    def has_required_fields(self) -> bool:
        return bool(
            self.institution.strip()
            and (
                self.degree_en.strip()
                or self.degree_de.strip()
            )
            and self.start_date.strip()
        )
