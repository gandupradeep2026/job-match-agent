from market_intelligence.metadata_quality import (
    JobMetadataNormalizer,
)
from market_intelligence.models import (
    JobMarketRecord,
)


def test_data_engineer_removes_team_false_positives():

    job = JobMarketRecord(
        job_title=(
            "(Senior) Data Engineer"
        ),
        job_family=(
            "Data & Analytics"
        ),
        description="""
        RESPONSIBILITIES

        Develop data pipelines with Python
        and SQL.

        Collaborate closely with Sales and
        Logistics teams.

        REQUIREMENTS

        Strong experience with Python, SQL,
        dbt, Databricks, AWS, Terraform
        and Git.

        PREFERRED QUALIFICATIONS

        Kubernetes and Apache Airflow
        would be a plus.

        WHAT WE OFFER

        Agile international environment.
        """,
    )

    result = (
        JobMetadataNormalizer
        .normalize_record(
            job
        )
    )

    assert (
        result.seniority
        == "Senior"
    )

    assert "Python" in (
        result.required_skills
    )

    assert "SQL" in (
        result.required_skills
    )

    assert "dbt" in (
        result.required_skills
    )

    assert "Databricks" in (
        result.required_skills
    )

    assert "AWS" in (
        result.required_skills
    )

    assert "Terraform" in (
        result.required_skills
    )

    assert "Git" in (
        result.required_skills
    )

    assert "Sales" not in (
        result.required_skills
    )

    assert "Logistics" not in (
        result.required_skills
    )

    assert "Kubernetes" in (
        result.preferred_skills
    )

    assert "Apache Airflow" in (
        result.preferred_skills
    )
