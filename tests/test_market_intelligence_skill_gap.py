from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser
from market_intelligence.skill_gap import SkillGapPrioritizer


parser = UniversalJobParser()


def build_skill_gap_database(tmp_path):
    database_path = tmp_path / "skill_gap.db"

    db = JobMarketDatabase(database_path)

    jobs = [
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="""
            Python, SQL, Apache Spark and Airflow are required.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            country="Germany",
            description="""
            Python, SQL, BigQuery and Airflow are required.
            """,
        ),

        parser.parse(
            job_title="Cloud Data Engineer",
            country="Germany",
            description="""
            Python, SQL, BigQuery, Terraform and Docker are required.
            """,
        ),

        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            description="""
            Python, SQL, Apache Kafka and Docker are required.
            """,
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    return db


def test_skill_gap_detects_missing_skills(tmp_path):
    db = build_skill_gap_database(tmp_path)

    prioritizer = SkillGapPrioritizer(db)

    result = prioritizer.analyze(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    names = [
        item.skill
        for item in result.recommendations
    ]

    assert "Apache Airflow" in names
    assert "BigQuery" in names
    assert "Docker" in names


def test_high_demand_skill_gets_higher_priority(tmp_path):
    db = build_skill_gap_database(tmp_path)

    prioritizer = SkillGapPrioritizer(db)

    result = prioritizer.analyze(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    recommendation_map = {
        item.skill: item
        for item in result.recommendations
    }

    assert (
        recommendation_map["Apache Airflow"].market_percentage
        == 50.0
    )

    assert (
        recommendation_map["Apache Airflow"].priority
        == "CRITICAL"
    )


def test_priority_order_is_descending(tmp_path):
    db = build_skill_gap_database(tmp_path)

    prioritizer = SkillGapPrioritizer(db)

    result = prioritizer.analyze(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    scores = [
        item.priority_score
        for item in result.recommendations
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_existing_skill_is_not_recommended(tmp_path):
    db = build_skill_gap_database(tmp_path)

    prioritizer = SkillGapPrioritizer(db)

    result = prioritizer.analyze(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
        ],
        job_family="Data & Analytics",
        country="Germany",
    )

    names = [
        item.skill
        for item in result.recommendations
    ]

    assert "BigQuery" not in names


def test_empty_market_returns_no_recommendations(tmp_path):
    database_path = tmp_path / "empty.db"

    db = JobMarketDatabase(database_path)

    prioritizer = SkillGapPrioritizer(db)

    result = prioritizer.analyze(
        candidate_skills=[
            "Python",
            "SQL",
        ]
    )

    assert result.total_jobs_analyzed == 0
    assert result.recommendations == []
    assert result.market_coverage_percentage == 0.0
