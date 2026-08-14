from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser
from market_intelligence.trend_analysis import MarketTrendAnalyzer


parser = UniversalJobParser()


def build_trend_database(tmp_path):

    db = JobMarketDatabase(
        tmp_path / "trends.db"
    )

    jobs = [
        # January
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            posted_date="2026-01-10",
            description="""
            Python and SQL required.
            """,
        ),

        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            posted_date="2026-01-20",
            description="""
            Python and BigQuery required.
            """,
        ),

        # February
        parser.parse(
            job_title="Data Engineer",
            country="Germany",
            posted_date="2026-02-05",
            description="""
            Python, SQL and Airflow required.
            """,
        ),

        parser.parse(
            job_title="Junior Data Engineer",
            country="Germany",
            posted_date="2026-02-15",
            description="""
            Python and Apache Airflow required.
            """,
        ),

        # March
        parser.parse(
            job_title="Cloud Data Engineer",
            country="Germany",
            posted_date="2026-03-10",
            description="""
            Python, SQL, Apache Airflow
            and Terraform required.
            """,
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    return db


def test_available_periods(tmp_path):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    periods = analyzer.available_periods(
        job_family="Data & Analytics",
        country="Germany",
    )

    assert periods == [
        "2026-01",
        "2026-02",
        "2026-03",
    ]


def test_job_volume_by_month(tmp_path):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    volume = analyzer.job_volume_by_month(
        country="Germany"
    )

    result = {
        item["period"]: item["job_count"]
        for item in volume
    }

    assert result["2026-01"] == 2
    assert result["2026-02"] == 2
    assert result["2026-03"] == 1


def test_python_skill_trend(tmp_path):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    trend = analyzer.skill_trend(
        skill="Python",
        country="Germany",
    )

    assert len(trend) == 3

    assert (
        trend[0].demand_percentage
        == 100.0
    )

    assert (
        trend[1].demand_percentage
        == 100.0
    )


def test_airflow_demand_increases(tmp_path):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    comparison = (
        analyzer.compare_skill_periods(
            skill="Airflow",
            earlier_period="2026-01",
            later_period="2026-02",
            country="Germany",
        )
    )

    assert (
        comparison.earlier_percentage
        == 0.0
    )

    assert (
        comparison.later_percentage
        == 100.0
    )

    assert (
        comparison.percentage_point_change
        == 100.0
    )

    assert comparison.trend == "RISING"


def test_aliases_work_in_trend_analysis(
    tmp_path,
):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    comparison = (
        analyzer.compare_skill_periods(
            skill="Airflow",
            earlier_period="2026-01",
            later_period="2026-02",
        )
    )

    assert (
        comparison.skill
        == "Apache Airflow"
    )


def test_top_rising_skills(tmp_path):

    db = build_trend_database(tmp_path)

    analyzer = MarketTrendAnalyzer(db)

    rising = analyzer.top_changing_skills(
        earlier_period="2026-01",
        later_period="2026-02",
        direction="rising",
    )

    names = [
        item.skill
        for item in rising
    ]

    assert "Apache Airflow" in names

    airflow = next(
        item
        for item in rising
        if item.skill == "Apache Airflow"
    )

    assert (
        airflow.percentage_point_change
        == 100.0
    )
