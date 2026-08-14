from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StarStory:
    """One reusable bilingual STAR interview story."""

    id: int | None = None

    title_en: str = ""
    title_de: str = ""

    category: str = ""
    source_type: str = ""
    source_name: str = ""

    situation_en: str = ""
    situation_de: str = ""

    task_en: str = ""
    task_de: str = ""

    action_en: str = ""
    action_de: str = ""

    result_en: str = ""
    result_de: str = ""

    lesson_en: str = ""
    lesson_de: str = ""

    metric_value: str = ""

    competencies: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    question_tags: list[str] = field(
        default_factory=list
    )

    verified: bool = False

    created_at: str = ""
    updated_at: str = ""

    def display_title(self) -> str:
        return (
            self.title_en.strip()
            or self.title_de.strip()
            or "STAR Story"
        )

    def has_required_fields(self) -> bool:
        """
        A usable story needs:
        - at least one title;
        - Situation, Task, Action and Result in at least one language.
        """

        has_title = bool(
            self.title_en.strip()
            or self.title_de.strip()
        )

        english_complete = all(
            [
                self.situation_en.strip(),
                self.task_en.strip(),
                self.action_en.strip(),
                self.result_en.strip(),
            ]
        )

        german_complete = all(
            [
                self.situation_de.strip(),
                self.task_de.strip(),
                self.action_de.strip(),
                self.result_de.strip(),
            ]
        )

        return bool(
            has_title
            and (
                english_complete
                or german_complete
            )
        )
