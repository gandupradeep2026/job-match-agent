import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser
from market_intelligence.models import JobMarketRecord
from market_intelligence.metadata_quality import (
JobMetadataNormalizer,
)

@dataclass
class JobIngestionResult:
    """
    Result of importing one analysed job into
    the Job Market Intelligence database.
    """

    inserted: bool

    job_id: Optional[int] = None

    duplicate: bool = False

    job_title: str = ""

    company: str = ""

    source_url: str = ""

    message: str = ""


class AnalysedJobMarketIngestor:
    """
    Bridge between the existing Job Match Agent
    analysis workflow and Job Market Intelligence.

    Input:
        - full analysed job-description text
        - extracted job metadata
        - optional imported URL
        - input/source method

    Output:
        - normalized JobMarketRecord
        - automatically persisted in job_market.db
        - duplicate protected
    """

    def __init__(
        self,
        database: Optional[JobMarketDatabase] = None,
    ):
        self.database = (
            database
            if database is not None
            else JobMarketDatabase()
        )

        self.parser = UniversalJobParser()

    # ======================================================
    # BASIC HELPERS
    # ======================================================
    @staticmethod
    def _clean(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return str(value).strip()

    @classmethod
    def _first_non_empty(
        cls,
        *values,
    ) -> str:
        for value in values:
            cleaned = cls._clean(
                value
            )

            if cleaned:
                return cleaned

        return ""

    # ======================================================
    # METADATA EXTRACTION
    # ======================================================
    def _extract_job_title(
        self,
        details: Dict[str, Any],
    ) -> str:
        return self._first_non_empty(
            details.get("job_title"),
            details.get("title"),
            details.get("position"),
            details.get("role"),
        )

    def _extract_company(
        self,
        details: Dict[str, Any],
    ) -> str:
        return self._first_non_empty(
            details.get("company"),
            details.get("company_name"),
            details.get("employer"),
            details.get("organization"),
        )

    def _extract_location(
        self,
        details: Dict[str, Any],
    ) -> str:
        return self._first_non_empty(
            details.get("location"),
            details.get("job_location"),
            details.get("city"),
        )

    def _extract_country(
        self,
        details: Dict[str, Any],
    ) -> str:
        return self._first_non_empty(
            details.get("country"),
            details.get("job_country"),
        )

    def _extract_posted_date(
        self,
        details: Dict[str, Any],
    ) -> Optional[str]:
        value = self._first_non_empty(
            details.get("posted_date"),
            details.get("date_posted"),
            details.get("publication_date"),
            details.get("published_date"),
        )

        return value or None

    # ======================================================
    # DUPLICATE IDENTITY
    # ======================================================
    @staticmethod
    def _build_content_fingerprint(
        job_text: str,
        job_title: str,
        company: str,
    ) -> str:
        """
        Generate a deterministic fingerprint when
        no public job URL exists.

        This prevents the same manually pasted job
        from being added repeatedly.
        """

        normalized_text = " ".join(
            (job_text or "")
            .lower()
            .split()
        )

        normalized_title = " ".join(
            (job_title or "")
            .lower()
            .split()
        )

        normalized_company = " ".join(
            (company or "")
            .lower()
            .split()
        )

        fingerprint_input = "|".join(
            [
                normalized_title,
                normalized_company,
                normalized_text,
            ]
        )

        digest = hashlib.sha256(
            fingerprint_input.encode(
                "utf-8"
            )
        ).hexdigest()

        return digest

    def _resolve_source_url(
        self,
        imported_job_url: str,
        details: Dict[str, Any],
        job_text: str,
        job_title: str,
        company: str,
    ) -> str:
        """
        Prefer the real URL.

        If no URL exists, create a stable internal identity
        URL so SQLite duplicate detection still works.
        """

        real_url = self._first_non_empty(
            imported_job_url,
            details.get("job_url"),
            details.get("source_url"),
            details.get("url"),
        )

        if real_url:
            return real_url

        fingerprint = (
            self._build_content_fingerprint(
                job_text=job_text,
                job_title=job_title,
                company=company,
            )
        )

        return (
            "analysis://"
            + fingerprint
        )

    # ======================================================
    # SOURCE LABEL
    # ======================================================
    @staticmethod
    def _build_source_name(
        source_method: str,
        source_url: str,
    ) -> str:

        method = (
            source_method
            or ""
        ).strip()

        if source_url.startswith(
            (
                "http://",
                "https://",
            )
        ):
            if method:
                return (
                    f"Job Agent - {method}"
                )

            return (
                "Job Agent - Public URL"
            )

        if method:
            return (
                f"Job Agent - {method}"
            )

        return (
            "Job Agent - Analysis"
        )

    # ======================================================
    # BUILD MARKET RECORD
    # ======================================================
    def build_market_record(
        self,
        job_text: str,
        extracted_job_details: Optional[
            Dict[str, Any]
        ] = None,
        imported_job_url: str = "",
        source_method: str = "",
    ) -> JobMarketRecord:

        cleaned_job_text = (
            job_text or ""
        ).strip()

        if not cleaned_job_text:
            raise ValueError(
                "Job text is required for "
                "market ingestion."
            )

        details = (
            extracted_job_details
            or {}
        )

        job_title = (
            self._extract_job_title(
                details
            )
        )

        company = (
            self._extract_company(
                details
            )
        )

        location = (
            self._extract_location(
                details
            )
        )

        country = (
            self._extract_country(
                details
            )
        )

        posted_date = (
            self._extract_posted_date(
                details
            )
        )

        source_url = (
            self._resolve_source_url(
                imported_job_url=(
                    imported_job_url
                ),
                details=details,
                job_text=cleaned_job_text,
                job_title=job_title,
                company=company,
            )
        )

        source = (
            self._build_source_name(
                source_method=(
                    source_method
                ),
                source_url=source_url,
            )
        )

        record = self.parser.parse(
            job_title=job_title,
            description=cleaned_job_text,
            company=company,
            location=location,
            country=country,
            source=source,
            source_url=source_url,
            posted_date=posted_date,
        )
        record = (
            JobMetadataNormalizer
            .normalize_record(
                record
            )
        )
        return record

    # ======================================================
    # INGEST ONE JOB
    # ======================================================
    def ingest(
        self,
        job_text: str,
        extracted_job_details: Optional[
            Dict[str, Any]
        ] = None,
        imported_job_url: str = "",
        source_method: str = "",
    ) -> JobIngestionResult:

        record = self.build_market_record(
            job_text=job_text,
            extracted_job_details=(
                extracted_job_details
            ),
            imported_job_url=(
                imported_job_url
            ),
            source_method=(
                source_method
            ),
        )

        job_id = self.database.add_job(
            record,
            prevent_duplicates=True,
        )

        if job_id is None:
            return JobIngestionResult(
                inserted=False,
                duplicate=True,
                job_id=None,
                job_title=record.job_title,
                company=record.company,
                source_url=(
                    record.source_url
                ),
                message=(
                    "Job already exists in the "
                    "market database."
                ),
            )

        return JobIngestionResult(
            inserted=True,
            duplicate=False,
            job_id=job_id,
            job_title=record.job_title,
            company=record.company,
            source_url=record.source_url,
            message=(
                "Job added to the market "
                "database successfully."
            ),
        )
