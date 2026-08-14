from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.database_maintenance import (
    MarketDatabaseMaintenance,
)
from market_intelligence.models import (
    JobMarketRecord,
)


def test_demo_source_detected():

    job = JobMarketRecord(
        job_title="Data Engineer",
        source="Demo Dataset",
    )

    assert (
        MarketDatabaseMaintenance
        .is_demo_or_test_job(
            job
        )
    )


def test_demo_url_detected():

    job = JobMarketRecord(
        job_title="Data Engineer",
        source_url="demo://job-1",
    )

    assert (
        MarketDatabaseMaintenance
        .is_demo_or_test_job(
            job
        )
    )


def test_example_domain_detected():

    job = JobMarketRecord(
        job_title="Data Engineer",
        source_url=(
            "https://example.com/jobs/123"
        ),
    )

    assert (
        MarketDatabaseMaintenance
        .is_demo_or_test_job(
            job
        )
    )


def test_real_provider_not_demo():

    job = JobMarketRecord(
        job_title="Data Engineer",
        source="Greenhouse",
        source_url=(
            "https://jobs.company.com/123"
        ),
    )

    assert not (
        MarketDatabaseMaintenance
        .is_demo_or_test_job(
            job
        )
    )


def test_copies_real_analysed_jobs(
    tmp_path,
):

    source_db = JobMarketDatabase(
        tmp_path / "source.db"
    )

    target_db = JobMarketDatabase(
        tmp_path / "target.db"
    )

    source_db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            country="Germany",
            job_family="Data & Analytics",
            source=(
                "Job Agent - Paste as text"
            ),
            source_url=(
                "analysis://real-job"
            ),
        ),
        prevent_duplicates=False,
    )

    result = (
        MarketDatabaseMaintenance
        .copy_existing_analysis_jobs(
            source_database=source_db,
            target_database=target_db,
            collection_filter=(
                MarketCollectionFilter(
                    allowed_countries=[
                        "Germany"
                    ],
                    allowed_job_families=[
                        "Data & Analytics"
                    ],
                )
            ),
        )
    )

    assert result.copied == 1
    assert target_db.count_jobs() == 1


def test_provider_jobs_are_not_copied(
    tmp_path,
):

    source_db = JobMarketDatabase(
        tmp_path / "source.db"
    )

    target_db = JobMarketDatabase(
        tmp_path / "target.db"
    )

    source_db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            country="Germany",
            job_family="Data & Analytics",
            source="Greenhouse",
            source_url=(
                "https://company.com/job/1"
            ),
        ),
        prevent_duplicates=False,
    )

    result = (
        MarketDatabaseMaintenance
        .copy_existing_analysis_jobs(
            source_database=source_db,
            target_database=target_db,
            collection_filter=(
                MarketCollectionFilter()
            ),
        )
    )

    assert (
        result.non_analysis_skipped
        == 1
    )

    assert (
        target_db.count_jobs()
        == 0
    )
