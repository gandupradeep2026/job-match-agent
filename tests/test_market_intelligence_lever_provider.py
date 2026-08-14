from urllib.parse import parse_qs, urlparse

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.external_job_collector import (
    ExternalJobCollector,
)
from market_intelligence.providers.lever import (
    LeverProvider,
)


def fake_lever_fetch(
    url,
):

    parsed = urlparse(
        url
    )

    query = parse_qs(
        parsed.query
    )

    skip = int(
        query.get(
            "skip",
            ["0"],
        )[0]
    )

    if skip > 0:
        return []

    return [
        {
            "id": "lever-001",
            "text": (
                "Data Engineer"
            ),
            "categories": {
                "location": (
                    "Berlin"
                ),
                "commitment": (
                    "Full-time"
                ),
                "team": (
                    "Engineering"
                ),
            },
            "country": "DE",
            "descriptionPlain": (
                "We are looking for "
                "a Data Engineer."
            ),
            "lists": [
                {
                    "text": (
                        "Requirements"
                    ),
                    "content": (
                        "<li>Python</li>"
                        "<li>SQL</li>"
                        "<li>Apache Airflow</li>"
                    ),
                }
            ],
            "additionalPlain": (
                "Docker is preferred."
            ),
            "hostedUrl": (
                "https://jobs.lever.co/"
                "testcompany/lever-001"
            ),
            "applyUrl": (
                "https://jobs.lever.co/"
                "testcompany/lever-001/apply"
            ),
            "workplaceType": (
                "hybrid"
            ),
        },
        {
            "id": "lever-002",
            "text": (
                "Cloud Engineer"
            ),
            "categories": {
                "location": (
                    "Munich"
                ),
            },
            "country": "DE",
            "descriptionPlain": (
                "AWS, Docker and "
                "Terraform required."
            ),
            "lists": [],
            "additionalPlain": "",
            "hostedUrl": (
                "https://jobs.lever.co/"
                "testcompany/lever-002"
            ),
            "workplaceType": (
                "remote"
            ),
        },
    ]


def test_lever_fetches_jobs():

    provider = LeverProvider(
        site="testcompany",
        company_name=(
            "Test Company GmbH"
        ),
        fetch_json=(
            fake_lever_fetch
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
        == "Berlin"
    )

    assert (
        first.country
        == "Germany"
    )


def test_lever_description_contains_lists():

    provider = LeverProvider(
        site="testcompany",
        fetch_json=(
            fake_lever_fetch
        ),
    )

    jobs = provider.fetch_jobs()

    description = (
        jobs[0].description
    )

    assert (
        "Data Engineer"
        in description
    )

    assert (
        "Requirements"
        in description
    )

    assert "Python" in description
    assert "SQL" in description

    assert (
        "Apache Airflow"
        in description
    )

    assert (
        "Docker is preferred."
        in description
    )


def test_lever_country_code_is_normalized():

    provider = LeverProvider(
        site="testcompany",
        fetch_json=(
            fake_lever_fetch
        ),
    )

    jobs = provider.fetch_jobs()

    assert all(
        job.country == "Germany"
        for job in jobs
    )


def test_lever_eu_instance():

    captured_urls = []

    def capture(
        url,
    ):
        captured_urls.append(
            url
        )

        return []

    provider = LeverProvider(
        site="testcompany",
        instance="eu",
        fetch_json=capture,
    )

    provider.fetch_jobs()

    assert (
        captured_urls[0].startswith(
            "https://api.eu.lever.co/"
        )
    )


def test_lever_collector_saves_jobs(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "lever.db"
    )

    provider = LeverProvider(
        site="testcompany",
        company_name=(
            "Test Company GmbH"
        ),
        fetch_json=(
            fake_lever_fetch
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


def test_lever_duplicate_protection(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "lever.db"
    )

    provider = LeverProvider(
        site="testcompany",
        fetch_json=(
            fake_lever_fetch
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
