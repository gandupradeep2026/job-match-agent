from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser


parser = UniversalJobParser()


def test_database_is_created(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    assert database_path.exists()
    assert db.count_jobs() == 0


def test_insert_and_read_job(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    job = parser.parse(
        job_title="Junior Data Engineer",
        company="Example GmbH",
        location="Berlin",
        country="Germany",
        source="Company Website",
        source_url="https://example.com/jobs/1",
        description="""
        Python, SQL and Apache Spark are required.
        Docker is nice to have.
        """,
    )

    job_id = db.add_job(job)

    assert job_id is not None
    assert db.count_jobs() == 1

    stored_job = db.get_job(job_id)

    assert stored_job is not None

    assert stored_job.job_title == "Junior Data Engineer"
    assert stored_job.company == "Example GmbH"

    assert "Python" in stored_job.required_skills
    assert "SQL" in stored_job.required_skills
    assert "Apache Spark" in stored_job.required_skills

    assert "Docker" in stored_job.preferred_skills


def test_duplicate_source_url_is_blocked(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    job = parser.parse(
        job_title="Data Engineer",
        description="Python and SQL required.",
        source_url="https://example.com/jobs/duplicate",
    )

    first_id = db.add_job(job)
    second_id = db.add_job(job)

    assert first_id is not None
    assert second_id is None

    assert db.count_jobs() == 1


def test_bulk_insert(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="Python and SQL required.",
            source_url="https://example.com/data",
        ),

        parser.parse(
            job_title="Hotel Receptionist",
            country="Germany",
            description="""
            Customer service and front office
            experience required.
            """,
            source_url="https://example.com/hotel",
        ),

        parser.parse(
            job_title="Automotive Software Engineer",
            country="Germany",
            description="""
            AUTOSAR and CAN bus experience required.
            """,
            source_url="https://example.com/auto",
        ),
    ]

    result = db.add_jobs(jobs)

    assert result["inserted"] == 3
    assert result["duplicates"] == 0

    assert db.count_jobs() == 3


def test_filter_by_job_family(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            description="Python and SQL.",
        ),

        parser.parse(
            job_title="Data Analyst",
            description="SQL and Power BI.",
        ),

        parser.parse(
            job_title="Hotel Receptionist",
            description="Customer service.",
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    data_jobs = db.get_jobs_by_family(
        "Data & Analytics"
    )

    assert len(data_jobs) == 2


def test_filter_by_country(tmp_path):
    database_path = tmp_path / "market.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="Python and SQL.",
        ),

        parser.parse(
            job_title="Data Engineer",
            country="Austria",
            description="Python and SQL.",
        ),

        parser.parse(
            job_title="Receptionist",
            country="Germany",
            description="Customer service.",
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    german_jobs = db.get_jobs_by_country(
        "Germany"
    )

    assert len(german_jobs) == 2
