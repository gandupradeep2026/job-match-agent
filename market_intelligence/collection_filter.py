from dataclasses import dataclass, field
from typing import List

from market_intelligence.models import JobMarketRecord
from market_intelligence.metadata_quality import JobMetadataNormalizer


@dataclass
class MarketCollectionFilter:
    """
    Configurable filtering policy for collected market jobs.

    Empty lists mean:
        no restriction for that field.

    Examples:

        allowed_countries=["Germany"]

        allowed_job_families=[
            "Data & Analytics"
        ]

        title_keywords=[
            "data",
            "analytics",
        ]
    """

    allowed_countries: List[str] = field(
        default_factory=list
    )

    allowed_job_families: List[str] = field(
        default_factory=list
    )

    title_keywords: List[str] = field(
        default_factory=list
    )

    excluded_title_keywords: List[str] = field(
        default_factory=list
    )

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
    def _normalized_set(
        cls,
        values: List[str],
    ) -> set[str]:

        return {
            cls._normalize(value)
            for value in values
            if cls._normalize(value)
        }

    def allows(
        self,
        job: JobMarketRecord,
    ) -> bool:
        """
        Return True if a parsed job should be stored.
        """

        # ==================================================
        # COUNTRY
        # ==================================================
        allowed_countries = (
            self._normalized_set(
                self.allowed_countries
            )
        )

        if allowed_countries:

            job_country = self._normalize(
                job.country
            )

            if (
                not job_country
                or job_country
                not in allowed_countries
            ):
                return False

            # Germany market guard:
            # reject jobs labeled Germany when their concrete
            # location resolves only to another country.
            if (
                job_country == "germany"
                and "germany" in allowed_countries
            ):
                location_country = (
                    JobMetadataNormalizer
                    ._infer_country_from_location(
                        job.location
                    )
                )

                normalized_location_country = (
                    self._normalize(
                        location_country
                    )
                )

                if (
                    normalized_location_country
                    and normalized_location_country
                    != "germany"
                ):
                    return False

        # ==================================================
        # JOB FAMILY
        # ==================================================
        allowed_families = (
            self._normalized_set(
                self.allowed_job_families
            )
        )

        if allowed_families:

            job_family = self._normalize(
                job.job_family
            )

            if (
                not job_family
                or job_family
                not in allowed_families
            ):
                return False

        # ==================================================
        # TITLE
        # ==================================================
        title = self._normalize(
            job.job_title
        )

        excluded_keywords = [
            self._normalize(keyword)
            for keyword
            in self.excluded_title_keywords
            if self._normalize(keyword)
        ]

        if any(
            keyword in title
            for keyword in excluded_keywords
        ):
            return False

        required_keywords = [
            self._normalize(keyword)
            for keyword in self.title_keywords
            if self._normalize(keyword)
        ]

        if required_keywords:

            if not any(
                keyword in title
                for keyword
                in required_keywords
            ):
                return False

        return True

    def is_active(
        self,
    ) -> bool:

        return bool(
            self.allowed_countries
            or self.allowed_job_families
            or self.title_keywords
            or self.excluded_title_keywords
        )
