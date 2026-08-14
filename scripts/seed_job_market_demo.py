from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser


def main():
    db = JobMarketDatabase()
    parser = UniversalJobParser()

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            company="DemoTech GmbH",
            location="Berlin",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-001",
            description="""
            We are looking for a Data Engineer.

            Python, SQL, Apache Spark and Apache Airflow are required.
            Docker and Terraform are nice to have.

            German and English are required.
            Full-time hybrid position.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            company="CloudData GmbH",
            location="Munich",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-002",
            description="""
            Python, SQL and BigQuery are required.

            Experience with Google Cloud Platform is required.

            Apache Airflow and dbt are preferred.

            English required.
            Full-time hybrid position.
            """,
        ),

        parser.parse(
            job_title="Cloud Data Engineer",
            company="DataCloud AG",
            location="Frankfurt",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-003",
            description="""
            Strong Python and SQL knowledge required.

            Google Cloud Platform, BigQuery,
            Terraform and Docker experience required.

            Apache Kafka would be a plus.

            Full-time remote position.
            """,
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Streaming Solutions GmbH",
            location="Hamburg",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-004",
            description="""
            Python, SQL, Apache Spark and Apache Kafka required.

            Apache Airflow and Docker experience required.

            Kubernetes is nice to have.

            Full-time hybrid role.
            """,
        ),

        parser.parse(
            job_title="Analytics Engineer",
            company="Analytics Labs GmbH",
            location="Berlin",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-005",
            description="""
            SQL, dbt and BigQuery experience required.

            Python is required.

            Docker and Git are preferred.

            English required.
            Full-time remote position.
            """,
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Enterprise Data GmbH",
            location="Cologne",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-006",
            description="""
            Python, SQL, Apache Spark and Databricks required.

            Apache Airflow and Terraform are required.

            Apache Kafka is desirable.

            Full-time hybrid position.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            company="Modern Data GmbH",
            location="Leipzig",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-007",
            description="""
            SQL and Python required.

            Experience with PostgreSQL and ETL required.

            dbt and Apache Airflow would be a plus.

            German and English required.

            Full-time on-site position.
            """,
        ),

        parser.parse(
            job_title="Data Engineer",
            company="Pipeline Systems GmbH",
            location="Dresden",
            country="Germany",
            source="Demo Dataset",
            source_url="demo://data-engineer-008",
            description="""
            Python, SQL, Apache Spark and ETL required.

            Docker and Apache Kafka required.

            Terraform and Kubernetes are nice to have.

            Full-time hybrid position.
            """,
        ),
    ]

    result = db.add_jobs(
        jobs,
        prevent_duplicates=True,
    )

    print("\nDEMO JOB IMPORT")
    print("=" * 50)

    print("Inserted:", result["inserted"])
    print("Duplicates:", result["duplicates"])
    print("Total jobs in database:", db.count_jobs())


if __name__ == "__main__":
    main()
