from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser
from market_intelligence.statistics import MarketStatisticsEngine


parser = UniversalJobParser()


def build_test_database(tmp_path):
    database_path = tmp_path / "statistics.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            company="Company A",
            location="Berlin",
            country="Germany",
            description="""
            Python, SQL and Apache Spark are required.
            Docker is nice to have.
            German and English required.
            Full-time hybrid position.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            company="Company B",
            location="Munich",
            country="Germany",
            description="""
            Python, SQL and BigQuery are required.
            Airflow is nice to have.
            English required.
            Full-time remote position.
            """,
        ),

        parser.parse(
            job_title="Hotel Receptionist",
            company="Hotel C",
            location="Berlin",
            country="Germany",
            description="""
            Customer service and front office experience required.
            German and English required.
            Part-time on-site position.
            """,
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    return db


def test_market_summary(tmp_path):
    db = build_test_database(tmp_path)

    engine = MarketStatisticsEngine(db)

    result = engine.summary()

    assert result["total_jobs"] == 3
    assert result["unique_companies"] == 3
    assert result["unique_locations"] == 2
    assert result["unique_job_families"] == 2


def test_top_skills(tmp_path):
    db = build_test_database(tmp_path)

    engine = MarketStatisticsEngine(db)

    skills = engine.top_skills()

    skill_map = {
        item["name"]: item
        for item in skills
    }

    assert skill_map["Python"]["count"] == 2
    assert skill_map["SQL"]["count"] == 2

    assert skill_map["Python"]["percentage"] == 66.67


def test_required_only_skills(tmp_path):
    db = build_test_database(tmp_path)

    engine = MarketStatisticsEngine(db)

    skills = engine.top_skills(
        required_only=True
    )

    names = [
        item["name"]
        for item in skills
    ]

    assert "Python" in names
    assert "SQL" in names

    assert "Docker" not in names
    assert "Apache Airflow" not in names


def test_job_family_statistics(tmp_path):
    db = build_test_database(tmp_path)

    engine = MarketStatisticsEngine(db)

    families = engine.top_job_families()

    result = {
        item["name"]: item
        for item in families
    }

    assert result["Data & Analytics"]["count"] == 2
    assert result["Hospitality"]["count"] == 1

    assert result["Data & Analytics"]["percentage"] == 66.67


def test_country_filter(tmp_path):
    database_path = tmp_path / "countries.db"

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
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    engine = MarketStatisticsEngine(db)

    result = engine.summary(
        country="Germany"
    )

    assert result["total_jobs"] == 1


def test_language_statistics(tmp_path):
    db = build_test_database(tmp_path)

    engine = MarketStatisticsEngine(db)

    languages = engine.languages()

    language_map = {
        item["name"]: item
        for item in languages
    }

    assert language_map["English"]["count"] == 3
    assert language_map["English"]["percentage"] == 100.0

    assert language_map["German"]["count"] == 2
    assert language_map["German"]["percentage"] == 66.67
