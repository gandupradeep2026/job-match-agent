from dataclasses import dataclass, field
from typing import List, Optional

from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.job_parser import (
    UniversalJobParser,
)
from market_intelligence.metadata_quality import (
    JobMetadataNormalizer,
)
from market_intelligence.providers.base import (
    JobSourceProvider,
)


@dataclass
class CollectionResult:
    provider: str

    fetched: int = 0
    inserted: int = 0
    duplicates: int = 0
    filtered_out: int = 0
    failed: int = 0

    errors: List[str] = field(
        default_factory=list
    )


class ExternalJobCollector:
    """
    Convert external provider jobs into normalized
    JobMarketRecord objects and persist them.

    Pipeline:

        Provider
            ↓
        UniversalJobParser
            ↓
        Metadata normalization
            ↓
        Collection filter
            ↓
        Duplicate protection
            ↓
        SQLite
    """

    def __init__(
        self,
        database: Optional[
            JobMarketDatabase
        ] = None,
    ):
        self.database = (
            database
            if database is not None
            else JobMarketDatabase()
        )

        self.parser = (
            UniversalJobParser()
        )

    def collect(
        self,
        provider: JobSourceProvider,
        collection_filter: Optional[
            MarketCollectionFilter
        ] = None,
    ) -> CollectionResult:

        provider_jobs = (
            provider.fetch_jobs()
        )

        result = CollectionResult(
            provider=(
                provider.provider_name
            ),
            fetched=len(
                provider_jobs
            ),
        )

        for provider_job in provider_jobs:

            try:

                if not (
                    provider_job.description
                    or ""
                ).strip():

                    result.failed += 1

                    result.errors.append(
                        (
                            f"{provider_job.job_title}: "
                            "job description is empty."
                        )
                    )

                    continue

                # ==========================================
                # PARSE
                # ==========================================
                record = self.parser.parse(
                    job_title=(
                        provider_job.job_title
                    ),
                    description=(
                        provider_job.description
                    ),
                    company=(
                        provider_job.company
                    ),
                    location=(
                        provider_job.location
                    ),
                    country=(
                        provider_job.country
                    ),
                    source=(
                        provider_job.source
                    ),
                    source_url=(
                        provider_job.source_url
                    ),
                    posted_date=(
                        provider_job.posted_date
                    ),
                )

                # ==========================================
                # METADATA QUALITY
                # ==========================================
                record = (
                    JobMetadataNormalizer
                    .normalize_record(
                        record
                    )
                )

                # ==========================================
                # FILTER
                # ==========================================
                if (
                    collection_filter
                    is not None
                    and collection_filter.is_active()
                    and not collection_filter.allows(
                        record
                    )
                ):
                    result.filtered_out += 1
                    continue

                # ==========================================
                # DATABASE
                # ==========================================
                job_id = (
                    self.database.add_job(
                        record,
                        prevent_duplicates=True,
                    )
                )

                if job_id is None:
                    result.duplicates += 1

                else:
                    result.inserted += 1

            except Exception as error:

                result.failed += 1

                result.errors.append(
                    (
                        f"{provider_job.job_title}: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
                )

        return result