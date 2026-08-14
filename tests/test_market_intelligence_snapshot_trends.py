from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.market_refresh import (
    MarketRefreshResult,
)
from market_intelligence.models import (
    JobMarketRecord,
)
from market_intelligence.snapshot_trends import (
    SnapshotTrendAnalyzer,
)


def refresh_result(
    number,
):

    return MarketRefreshResult(
        started_at=(
            f"2026-08-{number:02d}"
            "T08:00:00+00:00"
        ),
        completed_at=(
            f"2026-08-{number:02d}"
            "T08:05:00+00:00"
        ),

        jobs_before=0,
        jobs_after=0,

        sources_attempted=1,
        source_errors=0,

        fetched=0,
        inserted=0,
        filtered_out=0,
        duplicates=0,
        failed_jobs=0,

        source_results=[],
    )


def build_history(
    tmp_path,
):

    market = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    # ==============================================
    # SNAPSHOT 1
    # ==============================================

    market.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="A",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "Python",
                "SQL",
            ],
        ),
        prevent_duplicates=False,
    )

    market.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="B",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "SQL",
            ],
        ),
        prevent_duplicates=False,
    )

    history.record_refresh(
        result=refresh_result(1),
        market_database=market,
    )

    # ==============================================
    # SNAPSHOT 2
    # ==============================================

    market.add_job(
        JobMarketRecord(
            job_title="Cloud Data Engineer",
            company="C",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "Python",
                "Apache Airflow",
            ],
        ),
        prevent_duplicates=False,
    )

    market.add_job(
        JobMarketRecord(
            job_title="Analytics Engineer",
            company="D",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "Python",
                "Apache Airflow",
            ],
        ),
        prevent_duplicates=False,
    )

    history.record_refresh(
        result=refresh_result(2),
        market_database=market,
    )

    return history


def test_two_snapshots_exist(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    snapshots = analyzer.snapshots()

    assert len(snapshots) == 2


def test_python_demand_increases(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    result = analyzer.compare_skill(
        skill="Python",
        earlier_run_id=1,
        later_run_id=2,
    )

    assert (
        result.earlier_percentage
        == 50.0
    )

    assert (
        result.later_percentage
        == 75.0
    )

    assert (
        result.percentage_point_change
        == 25.0
    )

    assert (
        result.trend
        == "RISING"
    )


def test_airflow_appears_from_zero(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    result = analyzer.compare_skill(
        skill="Apache Airflow",
        earlier_run_id=1,
        later_run_id=2,
    )

    assert (
        result.earlier_percentage
        == 0.0
    )

    assert (
        result.later_percentage
        == 50.0
    )

    assert (
        result.trend
        == "RISING"
    )


def test_sql_demand_falls(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    result = analyzer.compare_skill(
        skill="SQL",
        earlier_run_id=1,
        later_run_id=2,
    )

    assert (
        result.earlier_percentage
        == 100.0
    )

    assert (
        result.later_percentage
        == 50.0
    )

    assert (
        result.trend
        == "FALLING"
    )


def test_rising_skills(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    rising = analyzer.changing_skills(
        earlier_run_id=1,
        later_run_id=2,
        direction="rising",
    )

    names = [
        item.skill
        for item in rising
    ]

    assert (
        "Apache Airflow"
        in names
    )

    assert "Python" in names


def test_market_growth(
    tmp_path,
):

    history = build_history(
        tmp_path
    )

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    result = analyzer.market_change(
        earlier_run_id=1,
        later_run_id=2,
    )

    assert result.earlier_jobs == 2
    assert result.later_jobs == 4

    assert result.job_change == 2

    assert (
        result.job_change_percentage
        == 100.0
    )

    assert (
        result.company_change
        == 2
    )
