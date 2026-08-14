import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from market_intelligence.skill_extractor import (
    UniversalSkillExtractor,
)


@dataclass
class ContextSkillExtractionResult:
    """
    Skill extraction result after considering
    job-description structure and context.
    """

    required_skills: List[str] = field(
        default_factory=list
    )

    preferred_skills: List[str] = field(
        default_factory=list
    )

    matched_aliases: Dict[str, str] = field(
        default_factory=dict
    )

    ignored_context_skills: List[str] = field(
        default_factory=list
    )

    def all_skills(
        self,
    ) -> List[str]:

        result = []
        seen = set()

        for skill in (
            self.required_skills
            + self.preferred_skills
        ):
            key = skill.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(skill)

        return result


class ContextAwareJobSkillExtractor:
    """
    Context-aware skill extraction for job descriptions.

    Unlike the baseline UniversalSkillExtractor, this class
    considers where a skill appears.

    Examples:

        "Experience with Python and SQL"
            -> required skills

        "Airflow would be a plus"
            -> preferred skill

        "Collaborate with Sales and Logistics teams"
            -> Sales / Logistics are NOT automatically
               treated as candidate requirements

        "WHAT WE OFFER"
            -> ignored for skill requirements
    """

    REQUIRED_SECTION = "required"
    PREFERRED_SECTION = "preferred"
    RESPONSIBILITY_SECTION = "responsibilities"
    BOILERPLATE_SECTION = "boilerplate"
    NEUTRAL_SECTION = "neutral"

    # ======================================================
    # SECTION HEADINGS
    # ======================================================

    REQUIRED_HEADINGS = {
        "requirements",
        "requirement",
        "required skills",
        "required qualifications",
        "qualifications",
        "your qualifications",
        "your profile",
        "what you bring",
        "what you bring to the table",
        "what we are looking for",
        "what we're looking for",
        "must have",
        "must haves",
        "experience required",
        "anforderungen",
        "dein profil",
        "ihr profil",
        "was du mitbringst",
        "was sie mitbringen",
        "qualifikationen",
        "voraussetzungen",
    }

    PREFERRED_HEADINGS = {
        "preferred",
        "preferred skills",
        "preferred qualifications",
        "nice to have",
        "nice-to-have",
        "nice to haves",
        "bonus",
        "bonus points",
        "good to have",
        "would be a plus",
        "optional",
        "wünschenswert",
        "von vorteil",
        "idealerweise",
        "zusätzliche qualifikationen",
    }

    RESPONSIBILITY_HEADINGS = {
        "responsibilities",
        "responsibility",
        "your responsibilities",
        "your role",
        "the role",
        "what you will do",
        "what you'll do",
        "what you do",
        "your tasks",
        "tasks",
        "duties",
        "day to day",
        "day-to-day",
        "aufgaben",
        "deine aufgaben",
        "ihre aufgaben",
        "was du tun wirst",
        "was sie erwartet",
        "deine rolle",
        "ihre rolle",
    }

    BOILERPLATE_HEADINGS = {
        "about us",
        "about the company",
        "about company",
        "company",
        "who we are",
        "our company",
        "our mission",
        "our culture",
        "culture",
        "benefits",
        "our benefits",
        "what we offer",
        "what we provide",
        "why join us",
        "perks",
        "equal opportunity",
        "equal opportunities",
        "diversity",
        "diversity and inclusion",
        "privacy",
        "data privacy",
        "über uns",
        "unternehmen",
        "unser unternehmen",
        "was wir bieten",
        "benefits und vorteile",
        "deine benefits",
        "ihre benefits",
        "warum wir",
    }

    # ======================================================
    # REQUIREMENT CUES
    # ======================================================

    REQUIREMENT_CUES = (
        "experience with",
        "experience in",
        "experience using",
        "knowledge of",
        "knowledge in",
        "proficiency in",
        "proficient in",
        "expertise in",
        "expertise with",
        "strong knowledge",
        "strong experience",
        "hands-on",
        "hands on",
        "familiarity with",
        "familiar with",
        "understanding of",
        "skills in",
        "required",
        "requirement",
        "must have",
        "you have",
        "you bring",
        "ability to",
        "kompetenz",
        "kenntnisse",
        "erfahrung mit",
        "erfahrung in",
        "erfahrung im",
        "erfahrung bei",
        "gute kenntnisse",
        "sehr gute kenntnisse",
        "fundierte kenntnisse",
        "voraussetzung",
        "erforderlich",
    )

    PREFERRED_CUES = (
        "nice to have",
        "nice-to-have",
        "preferred",
        "would be a plus",
        "is a plus",
        "plus",
        "advantage",
        "optional",
        "bonus",
        "desirable",
        "good to have",
        "von vorteil",
        "wünschenswert",
        "idealerweise",
        "optional",
    )

    # ======================================================
    # ORGANIZATIONAL CONTEXT
    # ======================================================

    ORGANIZATIONAL_CONTEXT_SKILLS = {
        "Sales",
        "Logistics",
        "Recruitment",
        "Talent Acquisition",
        "Accounting",
        "Customer Service",
        "Business Development",
        "Account Management",
    }

    ORGANIZATIONAL_CONTEXT_CUES = (
        "team",
        "teams",
        "department",
        "departments",
        "stakeholder",
        "stakeholders",
        "colleagues",
        "organisation",
        "organization",
        "functions",
        "business units",
        "partner with",
        "collaborate with",
        "working with",
        "work with",
        "support the",
        "stakeholdern",
        "abteilung",
        "abteilungen",
        "team zusammen",
        "zusammenarbeit mit",
    )

    # If the vacancy itself belongs to one of these families,
    # the corresponding organizational skill should not be
    # suppressed merely because it occurs in responsibilities.
    FAMILY_CORE_SKILLS = {
        "sales": {
            "Sales",
            "Business Development",
            "Account Management",
        },
        "logistics & supply chain": {
            "Logistics",
            "Supply Chain Management",
            "Warehouse Management",
            "Inventory Management",
            "Procurement",
        },
        "human resources": {
            "Recruitment",
            "Talent Acquisition",
            "HRIS",
            "Payroll",
        },
        "customer support": {
            "Customer Service",
        },
        "finance & accounting": {
            "Accounting",
            "Financial Reporting",
            "Accounts Payable",
            "Accounts Receivable",
            "Controlling",
        },
    }

    def __init__(
        self,
    ):
        self.base_extractor = (
            UniversalSkillExtractor()
        )

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:

        return " ".join(
            (value or "")
            .casefold()
            .strip()
            .split()
        )

    @classmethod
    def _clean_heading(
        cls,
        value: str,
    ) -> str:

        cleaned = (
            value or ""
        ).strip()

        cleaned = re.sub(
            r"^[\-\*\u2022#\s]+",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"[:：]\s*$",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return cleaned.casefold()

    @classmethod
    def _heading_type(
        cls,
        line: str,
    ) -> str | None:

        heading = cls._clean_heading(
            line
        )

        if not heading:
            return None

        # Headings are normally short. This prevents a normal
        # sentence beginning with "Requirements..." from being
        # misclassified as a heading.
        if len(heading) > 80:
            return None

        if heading in cls.REQUIRED_HEADINGS:
            return cls.REQUIRED_SECTION

        if heading in cls.PREFERRED_HEADINGS:
            return cls.PREFERRED_SECTION

        if heading in cls.RESPONSIBILITY_HEADINGS:
            return cls.RESPONSIBILITY_SECTION

        if heading in cls.BOILERPLATE_HEADINGS:
            return cls.BOILERPLATE_SECTION

        return None

    # ======================================================
    # SECTION SPLITTING
    # ======================================================

    @classmethod
    def _split_sections(
        cls,
        text: str,
    ) -> List[Tuple[str, str]]:

        lines = (
            text or ""
        ).replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        ).split(
            "\n"
        )

        sections: List[
            Tuple[str, str]
        ] = []

        current_type = (
            cls.NEUTRAL_SECTION
        )

        current_lines: List[str] = []

        def flush() -> None:

            if not current_lines:
                return

            section_text = "\n".join(
                current_lines
            ).strip()

            if section_text:
                sections.append(
                    (
                        current_type,
                        section_text,
                    )
                )

            current_lines.clear()

        for raw_line in lines:

            line = (
                raw_line or ""
            ).strip()

            if not line:
                continue

            detected_type = (
                cls._heading_type(
                    line
                )
            )

            if detected_type:

                flush()

                current_type = (
                    detected_type
                )

                continue

            current_lines.append(
                line
            )

        flush()

        return sections

    # ======================================================
    # SENTENCE SPLITTING
    # ======================================================

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> List[str]:

        if not text:
            return []

        pieces = re.split(
            r"(?<=[.!?;])\s+|\n+",
            text,
        )

        return [
            piece.strip(
                " \t-*•"
            )
            for piece in pieces
            if piece.strip(
                " \t-*•"
            )
        ]

    # ======================================================
    # CONTEXT
    # ======================================================

    @classmethod
    def _contains_requirement_cue(
        cls,
        text: str,
    ) -> bool:

        normalized = cls._normalize(
            text
        )

        return any(
            cue in normalized
            for cue in cls.REQUIREMENT_CUES
        )

    @classmethod
    def _contains_preferred_cue(
        cls,
        text: str,
    ) -> bool:

        normalized = cls._normalize(
            text
        )

        return any(
            cue in normalized
            for cue in cls.PREFERRED_CUES
        )

    @classmethod
    def _looks_like_organizational_context(
        cls,
        text: str,
    ) -> bool:

        normalized = cls._normalize(
            text
        )

        return any(
            cue in normalized
            for cue
            in cls.ORGANIZATIONAL_CONTEXT_CUES
        )

    @classmethod
    def _is_core_for_family(
        cls,
        skill: str,
        job_family: str,
    ) -> bool:

        family = cls._normalize(
            job_family
        )

        core_skills = (
            cls.FAMILY_CORE_SKILLS.get(
                family,
                set(),
            )
        )

        return skill in core_skills

    @classmethod
    def _should_suppress_skill(
        cls,
        skill: str,
        sentence: str,
        section_type: str,
        job_family: str,
    ) -> bool:
        """
        Suppress organizational-domain words when they
        describe teams, departments, stakeholders or
        collaboration rather than candidate capabilities.

        Example for a Data & Analytics role:

            Collaborate with Sales and Logistics teams.

        Sales and Logistics are organizational references,
        not required candidate skills.

        The same terms remain valid for their own job
        families or when explicitly stated as requirements.
        """

        if (
            skill
            not in cls.ORGANIZATIONAL_CONTEXT_SKILLS
        ):
            return False

        # A domain skill is valid when it belongs to the
        # vacancy's own job family.
        if cls._is_core_for_family(
            skill=skill,
            job_family=job_family,
        ):
            return False

        # Explicit requirement sections take precedence.
        if section_type == (
            cls.REQUIRED_SECTION
        ):
            return False

        # Explicit wording such as "experience in Sales"
        # also takes precedence.
        if cls._contains_requirement_cue(
            sentence
        ):
            return False

        # Generic organizational-domain terms appearing
        # inside responsibility text are normally references
        # to collaborators or business functions rather than
        # candidate requirements.
        if section_type == (
            cls.RESPONSIBILITY_SECTION
        ):
            return True

        # The same applies when organizational cues are
        # present in neutral text.
        if cls._looks_like_organizational_context(
            sentence
        ):
            return True

        return False

    # ======================================================
    # ADD SKILLS
    # ======================================================

    @staticmethod
    def _append_unique(
        destination: List[str],
        skill: str,
    ) -> None:

        normalized = (
            skill or ""
        ).casefold()

        if any(
            existing.casefold()
            == normalized
            for existing
            in destination
        ):
            return

        destination.append(
            skill
        )

    # ======================================================
    # MAIN EXTRACTION
    # ======================================================

    def extract(
        self,
        text: str,
        job_family: str = "",
    ) -> ContextSkillExtractionResult:

        cleaned_text = (
            text or ""
        ).strip()

        if not cleaned_text:
            return (
                ContextSkillExtractionResult()
            )

        result = (
            ContextSkillExtractionResult()
        )

        sections = (
            self._split_sections(
                cleaned_text
            )
        )

        # If no usable section was produced, treat the whole
        # document as neutral.
        if not sections:
            sections = [
                (
                    self.NEUTRAL_SECTION,
                    cleaned_text,
                )
            ]

        for (
            section_type,
            section_text,
        ) in sections:

            # Company descriptions, benefits, diversity
            # statements etc. should not define candidate
            # requirements.
            if section_type == (
                self.BOILERPLATE_SECTION
            ):
                continue

            sentences = (
                self._split_sentences(
                    section_text
                )
            )

            if not sentences:
                sentences = [
                    section_text
                ]

            for sentence in sentences:

                extraction = (
                    self.base_extractor.extract(
                        text=sentence
                    )
                )

                for alias, canonical in (
                    extraction.matched_aliases.items()
                ):
                    result.matched_aliases[
                        alias
                    ] = canonical

                skills = (
                    extraction.all_skills()
                )

                if not skills:
                    continue

                sentence_is_preferred = (
                    section_type
                    == self.PREFERRED_SECTION
                    or self._contains_preferred_cue(
                        sentence
                    )
                )

                for skill in skills:

                    if self._should_suppress_skill(
                        skill=skill,
                        sentence=sentence,
                        section_type=(
                            section_type
                        ),
                        job_family=(
                            job_family
                        ),
                    ):
                        self._append_unique(
                            result.ignored_context_skills,
                            skill,
                        )

                        continue

                    if sentence_is_preferred:

                        # Required wins if the skill already
                        # appeared in an explicit requirement.
                        if not any(
                            existing.casefold()
                            == skill.casefold()
                            for existing
                            in result.required_skills
                        ):
                            self._append_unique(
                                result.preferred_skills,
                                skill,
                            )

                    else:

                        self._append_unique(
                            result.required_skills,
                            skill,
                        )

                        # Required overrides preferred.
                        result.preferred_skills = [
                            existing
                            for existing
                            in result.preferred_skills
                            if (
                                existing.casefold()
                                != skill.casefold()
                            )
                        ]

        return result
