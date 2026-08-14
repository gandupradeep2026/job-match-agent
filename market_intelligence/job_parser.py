import re
from typing import List, Optional

from market_intelligence.classifier import UniversalJobClassifier
from market_intelligence.models import JobMarketRecord
from market_intelligence.skill_extractor import UniversalSkillExtractor


class UniversalJobParser:
    """
    Convert an unstructured job advertisement into a normalized
    JobMarketRecord.

    The parser is profession-agnostic and can process jobs from
    Data Engineering, Software, Automotive, Hospitality, Sales,
    HR, Finance, Logistics, and other domains.
    """

    LANGUAGE_ALIASES = {
        "German": [
            "german",
            "deutsch",
            "deutsche sprache",
            "deutschkenntnisse",
        ],
        "English": [
            "english",
            "englisch",
            "englischkenntnisse",
        ],
        "French": [
            "french",
            "französisch",
            "franzoesisch",
        ],
        "Spanish": [
            "spanish",
            "spanisch",
        ],
        "Italian": [
            "italian",
            "italienisch",
        ],
        "Dutch": [
            "dutch",
            "niederländisch",
            "niederlaendisch",
        ],
        "Polish": [
            "polish",
            "polnisch",
        ],
        "Chinese": [
            "chinese",
            "mandarin",
            "chinesisch",
        ],
        "Japanese": [
            "japanese",
            "japanisch",
        ],
    }

    EMPLOYMENT_PATTERNS = [
        (
            "Working Student",
            [
                "working student",
                "werkstudent",
                "werkstudentin",
            ],
        ),
        (
            "Internship",
            [
                "internship",
                "praktikum",
                "intern position",
            ],
        ),
        (
            "Part-time",
            [
                "part-time",
                "part time",
                "teilzeit",
            ],
        ),
        (
            "Full-time",
            [
                "full-time",
                "full time",
                "vollzeit",
            ],
        ),
        (
            "Freelance",
            [
                "freelance",
                "freelancer",
                "contractor",
                "freiberuflich",
            ],
        ),
    ]

    WORK_MODE_PATTERNS = [
        (
            "Hybrid",
            [
                "hybrid",
                "hybrides arbeiten",
                "hybrid working",
            ],
        ),
        (
            "Remote",
            [
                "remote",
                "work from home",
                "home office",
                "homeoffice",
                "fully remote",
            ],
        ),
        (
            "On-site",
            [
                "on-site",
                "onsite",
                "on site",
                "vor ort",
                "in office",
            ],
        ),
    ]

    EXPERIENCE_PATTERNS = [
        # English: at least 3 years / minimum 3 years
        r"(?:at least|minimum|min\.?)\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",

        # English: 3+ years
        r"(\d+(?:\.\d+)?)\s*\+\s*years?",

        # English: 3-5 years
        r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*\d+(?:\.\d+)?\s*years?",

        # English: 3 years of professional experience
        r"(\d+(?:\.\d+)?)\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",

        # German: mindestens 3 Jahre
        r"(?:mindestens|min\.?)\s*(\d+(?:[.,]\d+)?)\s*jahre",

        # German: 3 Jahre Berufserfahrung
        r"(\d+(?:[.,]\d+)?)\s*jahre\s+(?:berufs)?erfahrung",
    ]

    def __init__(self):
        self.classifier = UniversalJobClassifier()
        self.skill_extractor = UniversalSkillExtractor()

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join((text or "").lower().split())

    @staticmethod
    def _contains(text: str, phrase: str) -> bool:
        text = text.lower()
        phrase = phrase.lower()

        pattern = (
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)"
        )

        return re.search(pattern, text) is not None

    def _extract_languages(
        self,
        job_title: str,
        description: str,
    ) -> List[str]:

        combined = self._normalize(
            f"{job_title} {description}"
        )

        languages = []

        for language, aliases in self.LANGUAGE_ALIASES.items():

            for alias in aliases:
                if self._contains(combined, alias):

                    if language not in languages:
                        languages.append(language)

                    break

        return languages

    def _extract_experience_years(
        self,
        description: str,
    ) -> Optional[float]:

        normalized = self._normalize(description)

        for pattern in self.EXPERIENCE_PATTERNS:

            match = re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            value = match.group(1).replace(",", ".")

            try:
                number = float(value)

                if number.is_integer():
                    return int(number)

                return number

            except ValueError:
                continue

        return None

    def _extract_employment_type(
        self,
        job_title: str,
        description: str,
    ) -> str:

        combined = self._normalize(
            f"{job_title} {description}"
        )

        for employment_type, aliases in self.EMPLOYMENT_PATTERNS:

            for alias in aliases:

                if self._contains(combined, alias):
                    return employment_type

        return ""

    def _extract_work_mode(
        self,
        job_title: str,
        description: str,
    ) -> str:

        combined = self._normalize(
            f"{job_title} {description}"
        )

        for work_mode, aliases in self.WORK_MODE_PATTERNS:

            for alias in aliases:

                if self._contains(combined, alias):
                    return work_mode

        return ""

    def parse(
        self,
        job_title: str,
        description: str,
        company: str = "",
        location: str = "",
        country: str = "",
        source: str = "",
        source_url: str = "",
        posted_date: Optional[str] = None,
    ) -> JobMarketRecord:
        """
        Parse a complete job advertisement.

        Returns:
            JobMarketRecord
        """

        job_title = (job_title or "").strip()
        description = (description or "").strip()

        if not job_title and not description:
            raise ValueError(
                "Either job_title or description must be provided."
            )

        # --------------------------------------------------------------
        # Job classification
        # --------------------------------------------------------------
        classification = self.classifier.classify(
            job_title=job_title,
            description=description,
        )

        # --------------------------------------------------------------
        # Skill extraction
        # --------------------------------------------------------------
        skills = self.skill_extractor.extract(
            text=description,
            job_title=job_title,
        )

        # --------------------------------------------------------------
        # Additional structured metadata
        # --------------------------------------------------------------
        languages = self._extract_languages(
            job_title=job_title,
            description=description,
        )

        experience_years = self._extract_experience_years(
            description=description,
        )

        employment_type = self._extract_employment_type(
            job_title=job_title,
            description=description,
        )

        work_mode = self._extract_work_mode(
            job_title=job_title,
            description=description,
        )

        # --------------------------------------------------------------
        # Build normalized record
        # --------------------------------------------------------------
        return JobMarketRecord(
            job_title=job_title or classification.occupation,
            company=company.strip(),
            location=location.strip(),
            country=country.strip(),

            industry=classification.industry,
            job_family=classification.job_family,
            occupation=classification.occupation,
            seniority=classification.seniority,

            required_skills=skills.required_skills,
            preferred_skills=skills.preferred_skills,

            required_languages=languages,
            experience_years=experience_years,

            employment_type=employment_type,
            work_mode=work_mode,

            description=description,
            source=source.strip(),
            source_url=source_url.strip(),
            posted_date=posted_date,

            parser_version="1.0",
            classification_confidence=classification.confidence,
        )
