from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AchievementRecord:
    """One structured, verifiable career achievement."""

    id: int | None = None

    title_en: str = ""
    title_de: str = ""

    category: str = ""
    source_type: str = ""
    source_name: str = ""

    achievement_date: str = ""

    description_en: str = ""
    description_de: str = ""

    result_en: str = ""
    result_de: str = ""

    metric_value: str = ""

    competencies: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    evidence_url: str = ""

    verified: bool = False

    created_at: str = ""
    updated_at: str = ""

    def display_title(self) -> str:
        return (
            self.title_en.strip()
            or self.title_de.strip()
            or "Achievement"
        )

    def has_required_fields(self) -> bool:
        return bool(
            (
                self.title_en.strip()
                or self.title_de.strip()
            )
            and self.achievement_date.strip()
        )
