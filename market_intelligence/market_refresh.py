from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.source_registry import (
    JobSourceRegistry,
)


@dataclass
class SourceRefreshResult:
    company: str
    provider: str

    fetched: int = 0
    inserted: int = 0
    filtered_out: int = 0
    duplicates: int = 0
    failed: int = 0

    source_error: str = ""

    @property
    def healthy(self) -> bool:
        return not bool(
            self.source_error
        )


@dataclass
class MarketRefreshResult:
    started_at: str
    completed_at: str

    jobs_before: int
    jobs_after: int

    sources_attempted: int
    source_errors: int

    fetched: int
    inserted: int
    filtered_out: int
    duplicates: int
    failed_jobs: int

    source_results: List[
        SourceRefreshResult
    ] = field(
        default_factory=list
    )

    @property
    def new_jobs(self) -> int:
        return (
            self.jobs_after
            - self.jobs_before
        )


class MarketRefreshService:
    """
    Refresh the production Job Market Intelligence database
    using every enabled provider from job_sources.json.

    This is the application-level service used by:

        - command-line workflows
        - Streamlit refresh controls
        - future scheduled refreshes
    """

    def __init__(
        self,
        database: Optional[
            JobMarketDatabase
        ] = None,
        config_path: str = (
            "config/job_sources.json"
        ),
    ):
        self.database = (
            database
            if database is not None
            else JobMarketDatabase()
        )

        self.registry = (
            JobSourceRegistry(
                config_path
            )
        )

        self.collector = (
            ExternalJobCollector(
                database=self.database
            )
        )

    @staticmethod
    def _now_iso() -> str:
        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )

    @staticmethod
    def _source_label(
        source,
    ) -> str:

        return (
            source.company
            or source.board
            or source.site
            or source.provider
        )

    def refresh(
        self,
    ) -> MarketRefreshResult:
        """
        Run every enabled source.

        A failure in one provider does not stop the remaining
        providers from being processed.
        """

        started_at = (
            self._now_iso()
        )

        jobs_before = (
            self.database.count_jobs()
        )

        sources = (
            self.registry.enabled_sources()
        )

        collection_filter = (
            self.registry
            .load_collection_filter()
        )

        source_results = []

        total_fetched = 0
        total_inserted = 0
        total_filtered = 0
        total_duplicates = 0
        total_failed = 0
        total_source_errors = 0

        for source in sources:

            company = (
                self._source_label(
                    source
                )
            )

            try:
                provider = (
                    self.registry
                    .build_provider(
                        source
                    )
                )

                result = (
                    self.collector.collect(
                        provider=provider,
                        collection_filter=(
                            collection_filter
                        ),
                    )
                )

                source_result = (
                    SourceRefreshResult(
                        company=company,
                        provider=(
                            source.provider
                        ),
                        fetched=(
                            result.fetched
                        ),
                        inserted=(
                            result.inserted
                        ),
                        filtered_out=(
                            result.filtered_out
                        ),
                        duplicates=(
                            result.duplicates
                        ),
                        failed=(
                            result.failed
                        ),
                    )
                )

                total_fetched += (
                    result.fetched
                )

                total_inserted += (
                    result.inserted
                )

                total_filtered += (
                    result.filtered_out
                )

                total_duplicates += (
                    result.duplicates
                )

                total_failed += (
                    result.failed
                )

            except Exception as error:

                total_source_errors += 1

                source_result = (
                    SourceRefreshResult(
                        company=company,
                        provider=(
                            source.provider
                        ),
                        source_error=(
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                    )
                )

            source_results.append(
                source_result
            )

        jobs_after = (
            self.database.count_jobs()
        )

        completed_at = (
            self._now_iso()
        )

        return MarketRefreshResult(
            started_at=started_at,
            completed_at=completed_at,

            jobs_before=jobs_before,
            jobs_after=jobs_after,

            sources_attempted=len(
                sources
            ),

            source_errors=(
                total_source_errors
            ),

            fetched=total_fetched,
            inserted=total_inserted,
            filtered_out=(
                total_filtered
            ),
            duplicates=(
                total_duplicates
            ),
            failed_jobs=(
                total_failed
            ),

            source_results=(
                source_results
            ),
        )
