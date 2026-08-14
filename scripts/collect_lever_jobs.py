import argparse

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.providers.lever import (
    LeverProvider,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Collect public jobs from "
            "a Lever careers site."
        )
    )

    parser.add_argument(
        "--site",
        required=True,
        help=(
            "Lever company site identifier."
        ),
    )

    parser.add_argument(
        "--company",
        default="",
        help=(
            "Optional company-name override."
        ),
    )

    parser.add_argument(
        "--instance",
        choices=[
            "global",
            "eu",
        ],
        default="global",
        help=(
            "Lever API instance."
        ),
    )

    args = parser.parse_args()

    database = (
        JobMarketDatabase()
    )

    provider = LeverProvider(
        site=args.site,
        company_name=(
            args.company
        ),
        instance=(
            args.instance
        ),
    )

    collector = (
        ExternalJobCollector(
            database=database
        )
    )

    print()
    print(
        "LEVER JOB COLLECTION"
    )

    print("=" * 60)

    print(
        "Site:",
        args.site,
    )

    print(
        "Instance:",
        args.instance,
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
