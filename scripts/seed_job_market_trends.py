from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser


def main():

    db = JobMarketDatabase()
    parser = UniversalJobParser()

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            company="Trend Demo A",
            location="Berlin",
            country="Germany",
            posted_date="2026-05-10",
            source="Trend Demo",
            source_url="demo://trend-001",
            description="""
            Python, SQL and Apache Spark required.
            """
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Trend Demo B",
            location="Munich",
            country="Germany",
            posted_date="2026-05-20",
            source="Trend Demo",
            source_url="demo://trend-002",
            description="""
            Python and SQL required.
            """
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Trend Demo C",
            location="Berlin",
            country="Germany",
            posted_date="2026-06-10",
            source="Trend Demo",
            source_url="demo://trend-003",
            description="""
            Python, SQL, Apache Spark
            and Apache Airflow required.
            """
        ),

        parser.parse(
            job_title="Cloud Data Engineer",
            company="Trend Demo D",
            location="Frankfurt",
            country="Germany",
            posted_date="2026-06-20",
            source="Trend Demo",
            source_url="demo://trend-004",
            description="""
            Python, SQL, BigQuery
            and Apache Airflow required.
            """
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Trend Demo E",
            location="Hamburg",
            country="Germany",
            posted_date="2026-07-10",
            source="Trend Demo",
            source_url="demo://trend-005",
            description="""
            Python, SQL, Apache Airflow,
            Apache Kafka and Terraform required.
            """
        ),

        parser.parse(
            job_title="Analytics Engineer",
            company="Trend Demo F",
            location="Berlin",
            country="Germany",
            posted_date="2026-07-20",
            source="Trend Demo",
            source_url="demo://trend-006",
            description="""
            Python, SQL, dbt,
            BigQuery and Apache Airflow required.
            """
        ),
    ]

    result = db.add_jobs(
        jobs,
        prevent_duplicates=True,
    )

    print("\nTREND DEMO IMPORT")
    print("=" * 50)

    print(
        "Inserted:",
        result["inserted"]
    )

    print(
        "Duplicates:",
        result["duplicates"]
    )

    print(
        "Total jobs:",
        db.count_jobs()
    )


if __name__ == "__main__":
    main()
