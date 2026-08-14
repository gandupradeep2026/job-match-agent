from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.providers.greenhouse import (
    GreenhouseProvider,
)


def fake_greenhouse_fetch(
    url,
):

    if url.endswith(
        "/testcompany"
    ):
        return {
            "name": "Test Company GmbH"
        }

    if (
        "/jobs?content=true"
        in url
    ):
        return {
            "jobs": [
                {
                    "id": 1001,
                    "title": (
                        "Data Engineer"
                    ),
                    "location": {
                        "name": (
                            "Berlin, Germany"
                        )
                    },
                    "absolute_url": (
                        "https://example.com/jobs/1001"
                    ),
                    "content": (
                        "<p>Python and SQL are "
                        "required.</p>"
                        "<p>Apache Airflow is "
                        "preferred.</p>"
                    ),
                },
                {
                    "id": 1002,
                    "title": (
                        "Cloud Engineer"
                    ),
                    "location": {
                        "name": (
                            "Munich, Germany"
                        )
                    },
                    "absolute_url": (
                        "https://example.com/jobs/1002"
                    ),
                    "content": (
                        "<p>AWS, Docker and "
                        "Terraform required.</p>"
                    ),
                },
            ]
        }

    raise AssertionError(
        f"Unexpected URL: {url}"
    )


def test_greenhouse_fetches_jobs():

    provider = GreenhouseProvider(
        board_token="testcompany",
        fetch_json=(
            fake_greenhouse_fetch
        ),
    )

    jobs = provider.fetch_jobs()

    assert len(jobs) == 2

    first = jobs[0]

    assert (
        first.job_title
        == "Data Engineer"
    )

    assert (
        first.company
        == "Test Company GmbH"
    )

    assert (
        first.location
        == "Berlin, Germany"
    )

    assert (
        first.country
        == "Germany"
    )


def test_greenhouse_html_is_cleaned():

    provider = GreenhouseProvider(
        board_token="testcompany",
        fetch_json=(
            fake_greenhouse_fetch
        ),
    )

    jobs = provider.fetch_jobs()

    description = (
        jobs[0].description
    )

    assert "<p>" not in description

    assert (
        "Python and SQL are required."
        in description
    )

    assert (
        "Apache Airflow is preferred."
        in description
    )


def test_greenhouse_company_can_be_given():

    provider = GreenhouseProvider(
        board_token="testcompany",
        company_name=(
            "Manual Company"
        ),
        fetch_json=(
            fake_greenhouse_fetch
        ),
    )

    jobs = provider.fetch_jobs()

    assert all(
        job.company
        == "Manual Company"
        for job in jobs
    )


def test_collector_saves_jobs(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "greenhouse.db"
    )

    provider = GreenhouseProvider(
        board_token="testcompany",
        fetch_json=(
            fake_greenhouse_fetch
        ),
    )

    collector = (
        ExternalJobCollector(
            database=db
        )
    )

    result = collector.collect(
        provider
    )

    assert result.fetched == 2
    assert result.inserted == 2
    assert result.duplicates == 0
    assert result.failed == 0

    assert db.count_jobs() == 2


def test_collector_blocks_duplicates(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "greenhouse.db"
    )

    provider = GreenhouseProvider(
        board_token="testcompany",
        fetch_json=(
            fake_greenhouse_fetch
        ),
    )

    collector = (
        ExternalJobCollector(
            database=db
        )
    )

    first = collector.collect(
        provider
    )

    second = collector.collect(
        provider
    )

    assert first.inserted == 2

    assert second.inserted == 0
    assert second.duplicates == 2

    assert db.count_jobs() == 2
