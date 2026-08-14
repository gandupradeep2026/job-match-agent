from market_intelligence.cv_market_comparator import CVMarketComparator
from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser


parser = UniversalJobParser()


def build_market_database(tmp_path):
    database_path = tmp_path / "cv_market.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="""
            Python, SQL and Apache Spark are required.
            Docker is nice to have.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            country="Germany",
            description="""
            Python, SQL, BigQuery and Airflow are required.
            Docker is nice to have.
            """,
        ),

        parser.parse(
            job_title="Cloud Data Engineer",
            country="Germany",
            description="""
            Python, SQL, Google Cloud Platform,
            BigQuery and Terraform are required.
            """,
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    return db


def test_candidate_matches_common_skills(tmp_path):
    db = build_market_database(tmp_path)

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    matched_names = [
        item.skill
        for item in result.matched_market_skills
    ]

    assert "Python" in matched_names
    assert "SQL" in matched_names
    assert "BigQuery" in matched_names

    assert result.total_jobs_analyzed == 3


def test_candidate_missing_skills_are_detected(tmp_path):
    db = build_market_database(tmp_path)

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    missing_names = [
        item.skill
        for item in result.missing_market_skills
    ]

    assert "BigQuery" in missing_names
    assert "Apache Airflow" in missing_names
    assert "Terraform" in missing_names


def test_missing_skills_are_ranked_by_market_demand(tmp_path):
    db = build_market_database(tmp_path)

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    missing = result.missing_market_skills

    # SQL exists in all three jobs, so it should be
    # the highest-demand missing skill.
    assert missing[0].skill == "SQL"
    assert missing[0].market_percentage == 100.0


def test_market_coverage_is_calculated(tmp_path):
    db = build_market_database(tmp_path)

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    assert result.market_coverage_percentage > 0
    assert result.market_coverage_percentage <= 100


def test_country_filter_changes_market_scope(tmp_path):
    database_path = tmp_path / "countries.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="Python, SQL and BigQuery.",
        ),

        parser.parse(
            job_title="Data Engineer",
            country="Austria",
            description="Python, SQL and Snowflake.",
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        country="Germany",
    )

    missing_names = [
        item.skill
        for item in result.missing_market_skills
    ]

    assert "BigQuery" in missing_names
    assert "Snowflake" not in missing_names

    assert result.total_jobs_analyzed == 1


def test_empty_market_returns_zero_coverage(tmp_path):
    database_path = tmp_path / "empty.db"

    db = JobMarketDatabase(database_path)

    comparator = CVMarketComparator(db)

    result = comparator.compare(
        candidate_skills=[
            "Python",
            "SQL",
        ],
    )

    assert result.total_jobs_analyzed == 0
    assert result.market_coverage_percentage == 0.0

    assert result.matched_market_skills == []
    assert result.missing_market_skills == []
