from market_intelligence.models import JobMarketRecord
from market_intelligence.technology_filter import (
    available_technologies,
    filter_jobs_by_technology,
    job_has_technology,
)


def _job(
    title,
    required=None,
    preferred=None,
):
    return JobMarketRecord(
        job_title=title,
        country="Germany",
        required_skills=required or [],
        preferred_skills=preferred or [],
    )


def test_available_technologies_are_unique():
    jobs = [
        _job(
            "Data Engineer",
            required=[
                "Python",
                "Google Cloud Platform",
            ],
        ),
        _job(
            "Senior Data Engineer",
            required=[
                "Google Cloud Platform",
                "SQL",
            ],
        ),
    ]

    result = available_technologies(
        jobs
    )

    assert result.count(
        "Google Cloud Platform"
    ) == 1

    assert "Python" in result
    assert "SQL" in result


def test_priority_cloud_skills_appear_near_top():
    jobs = [
        _job(
            "Data Engineer",
            required=[
                "Teamwork",
                "SQL",
                "Google Cloud Platform",
                "BigQuery",
            ],
        ),
    ]

    result = available_technologies(
        jobs
    )

    assert result.index(
        "Google Cloud Platform"
    ) < result.index(
        "Teamwork"
    )

    assert result.index(
        "BigQuery"
    ) < result.index(
        "Teamwork"
    )


def test_job_has_selected_technology_case_insensitive():
    job = _job(
        "Cloud Data Engineer",
        required=[
            "Google Cloud Platform",
        ],
    )

    assert job_has_technology(
        job,
        "google cloud platform",
    )


def test_filter_jobs_by_gcp():
    gcp_job = _job(
        "Data Engineer",
        required=[
            "Python",
            "Google Cloud Platform",
        ],
    )

    aws_job = _job(
        "Data Engineer",
        required=[
            "Python",
            "AWS",
        ],
    )

    result = filter_jobs_by_technology(
        [gcp_job, aws_job],
        "Google Cloud Platform",
    )

    assert result == [
        gcp_job
    ]


def test_empty_technology_keeps_all_jobs():
    jobs = [
        _job(
            "Data Engineer",
            required=["SQL"],
        ),
        _job(
            "Software Engineer",
            required=["Python"],
        ),
    ]

    assert filter_jobs_by_technology(
        jobs,
        None,
    ) == jobs
