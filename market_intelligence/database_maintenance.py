from dataclasses import dataclass
from urllib.parse import urlparse

from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.models import (
    JobMarketRecord,
)


@dataclass
class ExistingJobCopyResult:
    inspected: int = 0
    copied: int = 0
    duplicates: int = 0
    filtered_out: int = 0
    demo_or_test_skipped: int = 0
    non_analysis_skipped: int = 0


class MarketDatabaseMaintenance:
    """
    Utilities used when rebuilding the market database.

    During a production rebuild we want to:

        - recollect external provider jobs
        - preserve genuine jobs analysed in the Job Agent
        - remove demo/test records
        - reapply current collection filters
    """

    DEMO_SOURCES = {
        "demo dataset",
        "trend demo",
    }

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
    def is_demo_or_test_job(
        cls,
        job: JobMarketRecord,
    ) -> bool:
        """
        Detect records intentionally created during development.
        """

        source = cls._normalize(
            job.source
        )

        source_url = (
            job.source_url
            or ""
        ).strip()

        if source in cls.DEMO_SOURCES:
            return True

        if source_url.startswith(
            "demo://"
        ):
            return True

        if source_url.startswith(
            "test://"
        ):
            return True

        # example.com is a reserved documentation/test domain.
        try:
            parsed = urlparse(
                source_url
            )

            hostname = (
                parsed.hostname
                or ""
            ).casefold()

            if (
                hostname == "example.com"
                or hostname.endswith(
                    ".example.com"
                )
            ):
                return True

        except Exception:
            pass

        return False

    @classmethod
    def is_job_agent_record(
        cls,
        job: JobMarketRecord,
    ) -> bool:

        source = cls._normalize(
            job.source
        )

        return source.startswith(
            "job agent"
        )

    @classmethod
    def copy_existing_analysis_jobs(
        cls,
        source_database: JobMarketDatabase,
        target_database: JobMarketDatabase,
        collection_filter: MarketCollectionFilter,
    ) -> ExistingJobCopyResult:
        """
        Copy genuine manually analysed jobs from the old
        database into a new clean database.

        Provider jobs are not copied because they will be
        recollected from their original providers.
        """

        result = ExistingJobCopyResult()

        jobs = (
            source_database.get_all_jobs()
        )

        for job in jobs:

            result.inspected += 1

            if cls.is_demo_or_test_job(
                job
            ):
                result.demo_or_test_skipped += 1
                continue

            if not cls.is_job_agent_record(
                job
            ):
                result.non_analysis_skipped += 1
                continue

            if (
                collection_filter.is_active()
                and not collection_filter.allows(
                    job
                )
            ):
                result.filtered_out += 1
                continue

            job_id = (
                target_database.add_job(
                    job,
                    prevent_duplicates=True,
                )
            )

            if job_id is None:
                result.duplicates += 1

            else:
                result.copied += 1

        return result
