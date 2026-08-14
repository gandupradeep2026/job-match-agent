from dataclasses import dataclass, field
from typing import Dict, List

from market_intelligence.skill_extractor import (
    UniversalSkillExtractor,
)


@dataclass
class CVSkillProfile:
    """
    Normalized skills extracted from a candidate CV.
    """

    skills: List[str] = field(
        default_factory=list
    )

    matched_aliases: Dict[str, str] = field(
        default_factory=dict
    )

    source_text_length: int = 0

    @property
    def skill_count(self) -> int:
        return len(self.skills)


class CVSkillBridge:
    """
    Bridge between the existing Job Agent CV text and
    the Job Market Intelligence system.

    The existing Job Agent already extracts CV text from
    uploaded PDF, DOCX, TXT, OCR, or pasted content.

    This class takes that text and converts it into the
    normalized skill taxonomy used by Market Intelligence.
    """

    def __init__(self):
        self.skill_extractor = (
            UniversalSkillExtractor()
        )

    @staticmethod
    def _clean_text(
        cv_text: str,
    ) -> str:
        return (cv_text or "").strip()

    def extract_skills(
        self,
        cv_text: str,
    ) -> CVSkillProfile:
        """
        Extract normalized skills from CV text.

        Returns an empty profile when CV text is empty.
        """

        cleaned_text = self._clean_text(
            cv_text
        )

        if not cleaned_text:
            return CVSkillProfile()

        extraction = (
            self.skill_extractor.extract(
                text=cleaned_text,
            )
        )

        skills = extraction.all_skills()

        return CVSkillProfile(
            skills=skills,
            matched_aliases=(
                extraction.matched_aliases
            ),
            source_text_length=len(
                cleaned_text
            ),
        )
