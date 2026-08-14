import re

from market_intelligence.context_skill_extractor import (
    ContextAwareJobSkillExtractor,
)
from market_intelligence.models import (
    JobMarketRecord,
)


class JobMetadataNormalizer:
    """
    Normalize and improve parsed job-market records.

    Responsibilities:

        1. Normalize explicit country names/codes.
        2. Infer missing country from location.
        3. Correct seniority using the job title.
        4. Re-extract skills using context-aware extraction.
    """

    # ======================================================
    # COUNTRY NORMALIZATION
    # ======================================================

    COUNTRY_ALIASES = {
        "de": "Germany",
        "deu": "Germany",
        "germany": "Germany",
        "deutschland": "Germany",

        "at": "Austria",
        "aut": "Austria",
        "austria": "Austria",
        "österreich": "Austria",

        "ch": "Switzerland",
        "che": "Switzerland",
        "switzerland": "Switzerland",
        "schweiz": "Switzerland",

        "fr": "France",
        "fra": "France",
        "france": "France",
        "frankreich": "France",

        "nl": "Netherlands",
        "nld": "Netherlands",
        "netherlands": "Netherlands",
        "niederlande": "Netherlands",

        "be": "Belgium",
        "bel": "Belgium",
        "belgium": "Belgium",
        "belgien": "Belgium",

        "es": "Spain",
        "esp": "Spain",
        "spain": "Spain",
        "spanien": "Spain",

        "it": "Italy",
        "ita": "Italy",
        "italy": "Italy",
        "italien": "Italy",

        "pl": "Poland",
        "pol": "Poland",
        "poland": "Poland",
        "polen": "Poland",

        "se": "Sweden",
        "swe": "Sweden",
        "sweden": "Sweden",
        "schweden": "Sweden",

        "no": "Norway",
        "nor": "Norway",
        "norway": "Norway",
        "norwegen": "Norway",

        "dk": "Denmark",
        "dnk": "Denmark",
        "denmark": "Denmark",
        "dänemark": "Denmark",

        "fi": "Finland",
        "fin": "Finland",
        "finland": "Finland",
        "finnland": "Finland",

        "ie": "Ireland",
        "irl": "Ireland",
        "ireland": "Ireland",
        "irland": "Ireland",

        "gb": "United Kingdom",
        "uk": "United Kingdom",
        "gbr": "United Kingdom",
        "united kingdom": "United Kingdom",
        "great britain": "United Kingdom",

        "us": "United States",
        "usa": "United States",
        "united states": "United States",

        "ca": "Canada",
        "can": "Canada",
        "canada": "Canada",

        "in": "India",
        "ind": "India",
        "india": "India",
    }

    COUNTRY_PATTERNS = [
        (
            r"\b(germany|deutschland)\b",
            "Germany",
        ),
        (
            r"\b(austria|österreich)\b",
            "Austria",
        ),
        (
            r"\b(switzerland|schweiz)\b",
            "Switzerland",
        ),
        (
            r"\b(france|frankreich)\b",
            "France",
        ),
        (
            r"\b(netherlands|niederlande)\b",
            "Netherlands",
        ),
        (
            r"\b(belgium|belgien)\b",
            "Belgium",
        ),
        (
            r"\b(spain|spanien)\b",
            "Spain",
        ),
        (
            r"\b(italy|italien)\b",
            "Italy",
        ),
        (
            r"\b(poland|polen)\b",
            "Poland",
        ),
        (
            r"\b(sweden|schweden)\b",
            "Sweden",
        ),
        (
            r"\b(norway|norwegen)\b",
            "Norway",
        ),
        (
            r"\b(denmark|dänemark)\b",
            "Denmark",
        ),
        (
            r"\b(finland|finnland)\b",
            "Finland",
        ),
        (
            r"\b(ireland|irland)\b",
            "Ireland",
        ),
        (
            r"\b(united kingdom|great britain)\b",
            "United Kingdom",
        ),
        (
            r"\b(united states|usa)\b",
            "United States",
        ),
        (
            r"\bcanada\b",
            "Canada",
        ),
        (
            r"\bindia\b",
            "India",
        ),
    ]

    # ======================================================
    # GERMAN LOCATION HINTS
    # ======================================================

    GERMANY_LOCATION_PATTERNS = [
        # Country abbreviation commonly used by job boards.
        r"(?:^|[\s,;/()\-])de(?:$|[\s,;/()\-])",

        # Major German employment locations.
        r"\bberlin\b",
        r"\bhamburg\b",
        r"\bmunich\b",
        r"\bmünchen\b",
        r"\bfrankfurt\b",
        r"\bfrankfurt am main\b",
        r"\bcologne\b",
        r"\bköln\b",
        r"\bdüsseldorf\b",
        r"\bdusseldorf\b",
        r"\bstuttgart\b",
        r"\bleipzig\b",
        r"\bdresden\b",
        r"\bhannover\b",
        r"\bhanover\b",
        r"\bnuremberg\b",
        r"\bnürnberg\b",
        r"\bkarlsruhe\b",
        r"\bbonn\b",
        r"\bbremen\b",
        r"\bdortmund\b",
        r"\bessen\b",
        r"\bmannheim\b",
        r"\bheidelberg\b",
        r"\bmagdeburg\b",
        r"\bpotsdam\b",
        r"\bchemnitz\b",
        r"\baachen\b",
        r"\bfreiburg\b",
        r"\bmainz\b",
        r"\bwiesbaden\b",
        r"\bmünster\b",
        r"\bmunster\b",
        r"\berlangen\b",
        r"\bdarmstadt\b",
        r"\bregensburg\b",
    ]

    # ======================================================
    # SENIORITY
    # ======================================================

    MANAGEMENT_PATTERNS = [
        r"\bhead of\b",
        r"\bdirector\b",
        r"\bvice president\b",
        r"\bvp\b",
        r"\bchief\b",
    ]

    SENIOR_PATTERNS = [
        r"\bsenior\b",
        r"\bsr\.?\b",
        r"\blead\b",
        r"\bprincipal\b",
        r"\bstaff\b",
    ]

    ENTRY_PATTERNS = [
        r"\bjunior\b",
        r"\bjr\.?\b",
        r"\bgraduate\b",
        r"\btrainee\b",
        r"\bentry[\s-]?level\b",
    ]

    INTERNSHIP_PATTERNS = [
        r"\bintern\b",
        r"\binternship\b",
        r"\bworking student\b",
        r"\bwerkstudent\b",
    ]

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    @staticmethod
    def _clean(
        value: str,
    ) -> str:

        return " ".join(
            (value or "")
            .strip()
            .split()
        )

    @staticmethod
    def _normalize_key(
        value: str,
    ) -> str:

        return " ".join(
            (value or "")
            .casefold()
            .strip()
            .split()
        )

    # ======================================================
    # COUNTRY
    # ======================================================

    @classmethod
    def normalize_explicit_country(
        cls,
        country: str,
    ) -> str:

        cleaned = cls._clean(
            country
        )

        if not cleaned:
            return ""

        key = cls._normalize_key(
            cleaned
        )

        return cls.COUNTRY_ALIASES.get(
            key,
            cleaned,
        )

    @classmethod
    def infer_country(
        cls,
        explicit_country: str = "",
        location: str = "",
        description: str = "",
    ) -> str:
        """
        Determine canonical country.

        Priority:

            1. Explicit provider country/code
            2. Country name in location
            3. Recognized German city / DE marker
            4. Country name in description

        City inference is intentionally conservative and
        currently focuses on Germany because that is the
        active market being collected.
        """

        explicit = (
            cls.normalize_explicit_country(
                explicit_country
            )
        )

        if explicit:
            return explicit

        location_text = (
            location or ""
        ).casefold()

        # --------------------------------------------------
        # Explicit country name inside location
        # --------------------------------------------------
        for pattern, country in (
            cls.COUNTRY_PATTERNS
        ):
            if re.search(
                pattern,
                location_text,
                flags=re.IGNORECASE,
            ):
                return country

        # --------------------------------------------------
        # German city / DE abbreviation
        # --------------------------------------------------
        for pattern in (
            cls.GERMANY_LOCATION_PATTERNS
        ):
            if re.search(
                pattern,
                location_text,
                flags=re.IGNORECASE,
            ):
                return "Germany"

        # --------------------------------------------------
        # Description fallback
        # --------------------------------------------------
        description_text = (
            description or ""
        ).casefold()

        for pattern, country in (
            cls.COUNTRY_PATTERNS
        ):
            if re.search(
                pattern,
                description_text,
                flags=re.IGNORECASE,
            ):
                return country

        return ""

    # ======================================================
    # SENIORITY
    # ======================================================

    @staticmethod
    def _matches_any(
        text: str,
        patterns,
    ) -> bool:

        return any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )

    @classmethod
    def resolve_seniority(
        cls,
        job_title: str,
        current_seniority: str = "",
    ) -> str:

        title = (
            job_title or ""
        ).strip()

        if cls._matches_any(
            title,
            cls.MANAGEMENT_PATTERNS,
        ):
            return "Management"

        if cls._matches_any(
            title,
            cls.SENIOR_PATTERNS,
        ):
            return "Senior"

        if cls._matches_any(
            title,
            cls.ENTRY_PATTERNS,
        ):
            return "Entry-level"

        if cls._matches_any(
            title,
            cls.INTERNSHIP_PATTERNS,
        ):
            return "Internship"

        cleaned_current = cls._clean(
            current_seniority
        )

        return (
            cleaned_current
            or "Not specified"
        )

    # ======================================================
    # SKILL QUALITY
    # ======================================================

    @classmethod
    def normalize_skills(
        cls,
        job: JobMarketRecord,
    ) -> JobMarketRecord:

        description = (
            job.description or ""
        ).strip()

        if not description:
            return job

        extractor = (
            ContextAwareJobSkillExtractor()
        )

        extraction = extractor.extract(
            text=description,
            job_family=job.job_family,
        )

        job.required_skills = (
            extraction.required_skills
        )

        job.preferred_skills = (
            extraction.preferred_skills
        )

        return job

    # ======================================================
    # COMPLETE RECORD
    # ======================================================

    @classmethod
    def normalize_record(
        cls,
        job: JobMarketRecord,
    ) -> JobMarketRecord:

        job.country = cls.infer_country(
            explicit_country=(
                job.country
            ),
            location=(
                job.location
            ),
            description=(
                job.description
            ),
        )

        job.seniority = (
            cls.resolve_seniority(
                job_title=(
                    job.job_title
                ),
                current_seniority=(
                    job.seniority
                ),
            )
        )

        job = cls.normalize_skills(
            job
        )

        return job