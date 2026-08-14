from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.market_refresh import (
    MarketRefreshResult,
    SourceRefreshResult,
)
from market_intelligence.models import (
    JobMarketRecord,
)


def build_refresh_result():

    return MarketRefreshResult(
        started_at=(
            "2026-08-14T08:00:00+00:00"
        ),
        completed_at=(
            "2026-08-14T08:05:00+00:00"
        ),

        jobs_before=10,
        jobs_after=12,

        sources_attempted=2,
        source_errors=0,

        fetched=20,
        inserted=2,
        filtered_out=15,
        duplicates=3,
        failed_jobs=0,

        source_results=[
            SourceRefreshResult(
                company="Company A",
                provider="greenhouse",
                fetched=10,
                inserted=1,
                filtered_out=8,
                duplicates=1,
                failed=0,
            ),
            SourceRefreshResult(
                company="Company B",
                provider="lever",
                fetched=10,
                inserted=1,
                filtered_out=7,
                duplicates=2,
                failed=0,
            ),
        ],
    )


def build_market_database(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="Company A",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "Python",
                "SQL",
            ],
            preferred_skills=[
                "Docker",
            ],
        ),
        prevent_duplicates=False,
    )

    db.add_job(
        JobMarketRecord(
            job_title=(
                "Analytics Engineer"
            ),
            company="Company B",
            country="Germany",
            job_family="Data & Analytics",
            required_skills=[
                "Python",
                "dbt",
            ],
        ),
        prevent_duplicates=False,
    )

    return db


def test_records_refresh(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    refresh_id = (
        history.record_refresh(
            result=(
                build_refresh_result()
            ),
            market_database=market,
        )
    )

    assert refresh_id == 1
    assert history.count_refreshes() == 1


def test_market_snapshot_counts_jobs(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    history.record_refresh(
        result=build_refresh_result(),
        market_database=market,
    )

    latest = history.latest_refresh()

    assert latest is not None

    assert (
        latest["snapshot_jobs"]
        == 2
    )

    assert (
        latest["companies_count"]
        == 2
    )


def test_python_snapshot_is_100_percent(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    history.record_refresh(
        result=build_refresh_result(),
        market_database=market,
    )

    rows = history.skill_history(
        "Python"
    )

    assert len(rows) == 1

    assert (
        rows[0]["job_count"]
        == 2
    )

    assert (
        rows[0][
            "demand_percentage"
        ]
        == 100.0
    )


def test_sql_snapshot_is_50_percent(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    history.record_refresh(
        result=build_refresh_result(),
        market_database=market,
    )

    rows = history.skill_history(
        "SQL"
    )

    assert (
        rows[0][
            "demand_percentage"
        ]
        == 50.0
    )


def test_source_results_are_saved(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    refresh_id = (
        history.record_refresh(
            result=(
                build_refresh_result()
            ),
            market_database=market,
        )
    )

    sources = history.source_results(
        refresh_id
    )

    assert len(sources) == 2

    assert {
        source["company"]
        for source in sources
    } == {
        "Company A",
        "Company B",
    }


def test_filter_is_applied_to_snapshot(
    tmp_path,
):

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    market = build_market_database(
        tmp_path
    )

    market.add_job(
        JobMarketRecord(
            job_title=(
                "Hotel Receptionist"
            ),
            company="Hotel GmbH",
            country="Germany",
            job_family="Hospitality",
            required_skills=[
                "Customer Service",
            ],
        ),
        prevent_duplicates=False,
    )

    policy = MarketCollectionFilter(
        allowed_countries=[
            "Germany"
        ],
        allowed_job_families=[
            "Data & Analytics"
        ],
    )

    history.record_refresh(
        result=build_refresh_result(),
        market_database=market,
        collection_filter=policy,
    )

    latest = history.latest_refresh()

    assert (
        latest["snapshot_jobs"]
        == 2
    )

    assert (
        "Customer Service"
        not in history.available_skills()
    )
