import argparse
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.database_maintenance import (
    MarketDatabaseMaintenance,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.source_registry import (
    JobSourceRegistry,
)


def create_sqlite_backup(
    source_path: Path,
    backup_path: Path,
) -> None:
    """
    Create a consistent SQLite backup using SQLite's
    native backup mechanism.
    """

    backup_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_connection = (
        sqlite3.connect(
            str(source_path)
        )
    )

    backup_connection = (
        sqlite3.connect(
            str(backup_path)
        )
    )

    try:
        source_connection.backup(
            backup_connection
        )

    finally:
        backup_connection.close()
        source_connection.close()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Safely rebuild the Job Market "
            "Intelligence database."
        )
    )

    parser.add_argument(
        "--config",
        default=(
            "config/job_sources.json"
        ),
    )

    parser.add_argument(
        "--database",
        default=(
            "database/job_market.db"
        ),
    )

    parser.add_argument(
        "--candidate",
        default=(
            "database/job_market_candidate.db"
        ),
    )

    parser.add_argument(
        "--activate",
        action="store_true",
        help=(
            "Backup the existing database "
            "and activate the rebuilt database."
        ),
    )

    parser.add_argument(
        "--no-preserve-analysis",
        action="store_true",
        help=(
            "Do not copy genuine jobs previously "
            "analysed through the Job Agent."
        ),
    )

    args = parser.parse_args()

    database_path = Path(
        args.database
    )

    candidate_path = Path(
        args.candidate
    )

    candidate_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ======================================================
    # START CLEAN CANDIDATE DATABASE
    # ======================================================
    if candidate_path.exists():
        candidate_path.unlink()

    candidate_database = (
        JobMarketDatabase(
            candidate_path
        )
    )

    registry = JobSourceRegistry(
        args.config
    )

    sources = (
        registry.enabled_sources()
    )

    collection_filter = (
        registry.load_collection_filter()
    )

    print()
    print(
        "SAFE MARKET DATABASE REBUILD"
    )
    print("=" * 72)

    print(
        "Current database:",
        database_path,
    )

    print(
        "Candidate database:",
        candidate_path,
    )

    print(
        "Enabled sources:",
        len(sources),
    )

    print()
    print("FILTER")
    print("-" * 72)

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

    # ======================================================
    # PRESERVE MANUALLY ANALYSED REAL JOBS
    # ======================================================
    if (
        database_path.exists()
        and not args.no_preserve_analysis
    ):

        print()
        print(
            "PRESERVING ANALYSED JOBS"
        )
        print("-" * 72)

        old_database = (
            JobMarketDatabase(
                database_path
            )
        )

        copy_result = (
            MarketDatabaseMaintenance
            .copy_existing_analysis_jobs(
                source_database=(
                    old_database
                ),
                target_database=(
                    candidate_database
                ),
                collection_filter=(
                    collection_filter
                ),
            )
        )

        print(
            "Existing jobs inspected:",
            copy_result.inspected,
        )

        print(
            "Analysed jobs preserved:",
            copy_result.copied,
        )

        print(
            "Demo/test skipped:",
            copy_result.demo_or_test_skipped,
        )

        print(
            "Filtered analysed jobs:",
            copy_result.filtered_out,
        )

        print(
            "Provider/non-analysis skipped:",
            copy_result.non_analysis_skipped,
        )

    # ======================================================
    # RECOLLECT EXTERNAL SOURCES
    # ======================================================
    collector = ExternalJobCollector(
        database=candidate_database
    )

    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    total_filtered = 0
    total_failed = 0

    source_errors = []

    print()
    print(
        "RECOLLECTING EXTERNAL SOURCES"
    )
    print("-" * 72)

    for index, source in enumerate(
        sources,
        start=1,
    ):

        label = (
            source.company
            or source.board
            or source.site
            or source.provider
        )

        print()
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

            total_fetched += (
                result.fetched
            )

            total_inserted += (
                result.inserted
            )

            total_duplicates += (
                result.duplicates
            )

            total_filtered += (
                result.filtered_out
            )

            total_failed += (
                result.failed
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

            message = (
                f"{label}: "
                f"{type(error).__name__}: "
                f"{error}"
            )

            source_errors.append(
                message
            )

            print(
                "   SOURCE ERROR:",
                message,
            )

    candidate_count = (
        candidate_database.count_jobs()
    )

    # ======================================================
    # SUMMARY
    # ======================================================
    print()
    print("=" * 72)
    print(
        "REBUILD SUMMARY"
    )
    print("=" * 72)

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
        "Failed jobs:",
        total_failed,
    )

    print(
        "Source errors:",
        len(source_errors),
    )

    print(
        "Candidate database jobs:",
        candidate_count,
    )

    # ======================================================
    # SAFETY CHECKS
    # ======================================================
    if source_errors:

        print()
        print(
            "Candidate database was created, "
            "but activation is blocked because "
            "one or more sources failed."
        )

        for error in source_errors:
            print(
                "-",
                error,
            )

        return

    if candidate_count <= 0:

        print()
        print(
            "Activation blocked: candidate "
            "database contains no jobs."
        )

        return

    # ======================================================
    # PREVIEW ONLY
    # ======================================================
    if not args.activate:

        print()
        print(
            "PREVIEW COMPLETE"
        )

        print(
            "The current job_market.db "
            "was NOT changed."
        )

        print()
        print(
            "Inspect the candidate database first."
        )

        print(
            "When satisfied, rerun with:"
        )

        print()
        print(
            "python -m scripts.rebuild_market_database "
            "--activate"
        )

        return

    # ======================================================
    # ACTIVATE
    # ======================================================
    print()
    print(
        "ACTIVATING CLEAN DATABASE"
    )
    print("-" * 72)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = Path(
        "database/backups"
    ) / (
        f"job_market_"
        f"{timestamp}.db"
    )

    if database_path.exists():

        create_sqlite_backup(
            source_path=(
                database_path
            ),
            backup_path=(
                backup_path
            ),
        )

        print(
            "Backup created:",
            backup_path,
        )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================================
    # WINDOWS-SAFE SQLITE ACTIVATION
    # ==================================================
    #
    # Do not use os.replace() here.
    #
    # Windows can prevent an SQLite file from being renamed
    # while a connection still has the file open. Instead,
    # copy the complete candidate SQLite database into the
    # production database using SQLite's native backup API.
    #
    # Both connections are explicitly closed before we
    # continue.
    # ==================================================

    candidate_connection = sqlite3.connect(
        str(candidate_path)
    )

    production_connection = sqlite3.connect(
        str(database_path)
    )

    try:
        candidate_connection.backup(
            production_connection
        )

    finally:
        production_connection.close()
        candidate_connection.close()

    print(
        "Clean database activated:",
        database_path,
    )

    production_database = (
        JobMarketDatabase(
            database_path
        )
    )

    print(
        "Production jobs:",
        production_database.count_jobs(),
    )

    print()
    print(
        "DATABASE REBUILD COMPLETED SUCCESSFULLY"
    )


if __name__ == "__main__":
    main()
