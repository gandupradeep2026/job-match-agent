import argparse
from dataclasses import dataclass
from typing import List

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.source_registry import (
    JobSourceConfig,
    JobSourceRegistry,
)


@dataclass
class SourceRunResult:
    company: str
    provider: str

    fetched: int = 0
    inserted: int = 0
    duplicates: int = 0
    filtered_out: int = 0
    failed: int = 0

    error: str = ""


def _source_label(
    source: JobSourceConfig,
) -> str:

    if source.company:
        return source.company

    if source.provider == "greenhouse":
        return source.board

    if source.provider == "lever":
        return source.site

    return source.provider


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Collect jobs from every enabled "
            "market source."
        )
    )

    parser.add_argument(
        "--config",
        default=(
            "config/job_sources.json"
        ),
    )

    args = parser.parse_args()

    registry = JobSourceRegistry(
        args.config
    )

    sources = (
        registry.enabled_sources()
    )

    collection_filter = (
        registry.load_collection_filter()
    )

    database = JobMarketDatabase()

    collector = ExternalJobCollector(
        database=database
    )

    print()
    print(
        "MULTI-SOURCE JOB COLLECTION"
    )
    print("=" * 70)

    print(
        "Configured enabled sources:",
        len(sources),
    )

    print(
        "Jobs before collection:",
        database.count_jobs(),
    )

    print()
    print("COLLECTION FILTER")
    print("-" * 70)

    print(
        "Countries:",
        (
            ", ".join(
                collection_filter.allowed_countries
            )
            or "ALL"
        ),
    )

    print(
        "Job families:",
        (
            ", ".join(
                collection_filter.allowed_job_families
            )
            or "ALL"
        ),
    )

    print(
        "Title keywords:",
        (
            ", ".join(
                collection_filter.title_keywords
            )
            or "ANY"
        ),
    )

    print()

    run_results: List[
        SourceRunResult
    ] = []

    for index, source in enumerate(
        sources,
        start=1,
    ):

        label = _source_label(
            source
        )

        print(
            f"[{index}/{len(sources)}] "
            f"{label} "
            f"({source.provider})"
        )

        try:

            provider = (
                registry.build_provider(
                    source
                )
            )

            result = collector.collect(
                provider=provider,
                collection_filter=(
                    collection_filter
                ),
            )

            run_result = (
                SourceRunResult(
                    company=label,
                    provider=(
                        source.provider
                    ),
                    fetched=(
                        result.fetched
                    ),
                    inserted=(
                        result.inserted
                    ),
                    duplicates=(
                        result.duplicates
                    ),
                    filtered_out=(
                        result.filtered_out
                    ),
                    failed=(
                        result.failed
                    ),
                )
            )

            run_results.append(
                run_result
            )

            print(
                "   Fetched:",
                result.fetched,
            )

            print(
                "   Inserted:",
                result.inserted,
            )

            print(
                "   Filtered out:",
                result.filtered_out,
            )

            print(
                "   Duplicates:",
                result.duplicates,
            )

            print(
                "   Failed:",
                result.failed,
            )

        except Exception as error:

            run_result = (
                SourceRunResult(
                    company=label,
                    provider=(
                        source.provider
                    ),
                    error=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                )
            )

            run_results.append(
                run_result
            )

            print(
                "   ERROR:",
                run_result.error,
            )

        print()

    total_fetched = sum(
        item.fetched
        for item in run_results
    )

    total_inserted = sum(
        item.inserted
        for item in run_results
    )

    total_filtered = sum(
        item.filtered_out
        for item in run_results
    )

    total_duplicates = sum(
        item.duplicates
        for item in run_results
    )

    total_failed = sum(
        item.failed
        for item in run_results
    )

    source_errors = [
        item
        for item in run_results
        if item.error
    ]

    print("=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)

    print(
        "Sources attempted:",
        len(run_results),
    )

    print(
        "Sources with errors:",
        len(source_errors),
    )

    print(
        "Fetched:",
        total_fetched,
    )

    print(
        "Inserted:",
        total_inserted,
    )

    print(
        "Filtered out:",
        total_filtered,
    )

    print(
        "Duplicates:",
        total_duplicates,
    )

    print(
        "Job failures:",
        total_failed,
    )

    print(
        "Total jobs in database:",
        database.count_jobs(),
    )

    if source_errors:

        print()
        print("SOURCE ERRORS")
        print("-" * 70)

        for item in source_errors:

            print(
                f"{item.company} "
                f"({item.provider}): "
                f"{item.error}"
            )


if __name__ == "__main__":
    main()