from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.job_ingestion_bridge import (
    AnalysedJobMarketIngestor,
)


def build_ingestor(tmp_path):

    db = JobMarketDatabase(
        tmp_path / "ingestion.db"
    )

    ingestor = (
        AnalysedJobMarketIngestor(
            database=db
        )
    )

    return db, ingestor


def test_ingests_analysed_job(
    tmp_path,
):

    db, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    result = ingestor.ingest(
        job_text="""
        We are looking for a Data Engineer.

        Python, SQL, Apache Spark and
        BigQuery are required.

        Docker is preferred.
        """,
        extracted_job_details={
            "job_title": "Data Engineer",
            "company": "Test GmbH",
            "location": "Berlin",
            "country": "Germany",
        },
        imported_job_url=(
            "https://example.com/jobs/123"
        ),
        source_method=(
            "Import public job URL"
        ),
    )

    assert result.inserted is True
    assert result.duplicate is False

    assert db.count_jobs() == 1

    job = db.get_job(
        result.job_id
    )

    assert job is not None

    assert (
        job.job_title
        == "Data Engineer"
    )

    assert (
        job.company
        == "Test GmbH"
    )

    assert (
        job.country
        == "Germany"
    )

    assert "Python" in (
        job.required_skills
    )

    assert "SQL" in (
        job.required_skills
    )


def test_real_url_duplicate_is_blocked(
    tmp_path,
):

    db, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    arguments = {
        "job_text": (
            "Python and SQL required."
        ),
        "extracted_job_details": {
            "job_title": (
                "Data Engineer"
            ),
            "company": "Example GmbH",
        },
        "imported_job_url": (
            "https://example.com/job/1"
        ),
    }

    first = ingestor.ingest(
        **arguments
    )

    second = ingestor.ingest(
        **arguments
    )

    assert first.inserted is True

    assert second.inserted is False
    assert second.duplicate is True

    assert db.count_jobs() == 1


def test_pasted_job_duplicate_is_blocked(
    tmp_path,
):

    db, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    job_text = """
    Cloud Data Engineer

    Python, SQL, BigQuery and
    Google Cloud Platform required.
    """

    details = {
        "job_title": (
            "Cloud Data Engineer"
        ),
        "company": (
            "Cloud GmbH"
        ),
    }

    first = ingestor.ingest(
        job_text=job_text,
        extracted_job_details=details,
        source_method="Paste as text",
    )

    second = ingestor.ingest(
        job_text=job_text,
        extracted_job_details=details,
        source_method="Paste as text",
    )

    assert first.inserted is True

    assert second.inserted is False
    assert second.duplicate is True

    assert db.count_jobs() == 1


def test_internal_fingerprint_is_created(
    tmp_path,
):

    _, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    record = (
        ingestor.build_market_record(
            job_text=(
                "Python and SQL required."
            ),
            extracted_job_details={
                "job_title": (
                    "Data Engineer"
                ),
            },
        )
    )

    assert (
        record.source_url.startswith(
            "analysis://"
        )
    )


def test_preserves_posted_date(
    tmp_path,
):

    db, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    result = ingestor.ingest(
        job_text=(
            "Python and SQL required."
        ),
        extracted_job_details={
            "job_title": (
                "Data Engineer"
            ),
            "posted_date": (
                "2026-08-10"
            ),
        },
    )

    job = db.get_job(
        result.job_id
    )

    assert (
        job.posted_date
        == "2026-08-10"
    )


def test_empty_job_text_is_rejected(
    tmp_path,
):

    _, ingestor = (
        build_ingestor(
            tmp_path
        )
    )

    try:
        ingestor.ingest(
            job_text=""
        )

        assert False

    except ValueError as error:
        assert (
            "Job text is required"
            in str(error)
        )
