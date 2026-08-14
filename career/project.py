from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProjectRecord:
    """One structured career or portfolio project."""

    id: int | None = None

    name_en: str = ""
    name_de: str = ""

    project_type: str = ""

    role_en: str = ""
    role_de: str = ""

    start_date: str = ""
    end_date: str = ""
    is_current: bool = False

    description_en: str = ""
    description_de: str = ""

    responsibilities_en: list[str] = field(
        default_factory=list
    )
    responsibilities_de: list[str] = field(
        default_factory=list
    )

    achievements_en: list[str] = field(
        default_factory=list
    )
    achievements_de: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    skills: list[str] = field(
        default_factory=list
    )

    repository_url: str = ""
    demo_url: str = ""

    verified: bool = False

    created_at: str = ""
    updated_at: str = ""

    def display_title(self) -> str:
        return (
            self.name_en.strip()
            or self.name_de.strip()
            or "Project"
        )

    def has_required_fields(self) -> bool:
        return bool(
            (
                self.name_en.strip()
                or self.name_de.strip()
            )
            and self.start_date.strip()
        )
