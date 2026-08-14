import argparse

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.providers.greenhouse import (
    GreenhouseProvider,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Collect public jobs from a "
            "Greenhouse job board."
        )
    )

    parser.add_argument(
        "--board",
        required=True,
        help=(
            "Greenhouse board token."
        ),
    )

    parser.add_argument(
        "--company",
        default="",
        help=(
            "Optional company name override."
        ),
    )

    args = parser.parse_args()

    database = (
        JobMarketDatabase()
    )

    provider = (
        GreenhouseProvider(
            board_token=args.board,
            company_name=args.company,
        )
    )

    collector = (
        ExternalJobCollector(
            database=database
        )
    )

    print()
    print(
        "GREENHOUSE JOB COLLECTION"
    )
    print("=" * 60)

    print(
        "Board:",
        args.board,
    )

    result = collector.collect(
        provider
    )

    print()
    print(
        "Provider:",
        result.provider,
    )

    print(
        "Fetched:",
        result.fetched,
    )

    print(
        "Inserted:",
        result.inserted,
    )

    print(
        "Duplicates:",
        result.duplicates,
    )

    print(
        "Failed:",
        result.failed,
    )

    print(
        "Total jobs in database:",
        database.count_jobs(),
    )

    if result.errors:

        print()
        print("ERRORS")
        print("-" * 60)

        for error in result.errors:
            print(
                "-",
                error,
            )


if __name__ == "__main__":
    main()
