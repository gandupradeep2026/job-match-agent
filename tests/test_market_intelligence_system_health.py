from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.models import (
    JobMarketRecord,
)
from market_intelligence.system_health import (
    MarketSystemHealthService,
)


class FakeRegistry:

    def __init__(
        self,
        count=2,
    ):
        self.count = count

    def enabled_sources(
        self,
    ):
        return [
            object()
            for _ in range(
                self.count
            )
        ]


def test_empty_database_is_critical(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    service = MarketSystemHealthService(
        database=db,
        history=history,
        registry=FakeRegistry(),
    )

    report = service.evaluate()

    assert (
        report.overall_status
        == "CRITICAL"
    )


def test_database_with_jobs_is_not_critical(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    for index in range(5):

        db.add_job(
            JobMarketRecord(
                job_title=(
                    "Data Engineer"
                ),
                company=(
                    f"Company {index}"
                ),
                country="Germany",
                job_family=(
                    "Data & Analytics"
                ),
            ),
            prevent_duplicates=False,
        )

    service = MarketSystemHealthService(
        database=db,
        history=history,
        registry=FakeRegistry(),
    )

    report = service.evaluate()

    database_check = next(
        check
        for check in report.checks
        if check.name
        == "Production database"
    )

    assert (
        database_check.status
        == "HEALTHY"
    )


def test_no_sources_is_critical(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="Company",
        ),
        prevent_duplicates=False,
    )

    service = MarketSystemHealthService(
        database=db,
        history=history,
        registry=FakeRegistry(
            count=0
        ),
    )

    report = service.evaluate()

    source_check = next(
        check
        for check in report.checks
        if check.name
        == "Source configuration"
    )

    assert (
        source_check.status
        == "CRITICAL"
    )


def test_low_company_diversity_warning(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="Only Company",
        ),
        prevent_duplicates=False,
    )

    service = MarketSystemHealthService(
        database=db,
        history=history,
        registry=FakeRegistry(),
    )

    report = service.evaluate()

    diversity = next(
        check
        for check in report.checks
        if check.name
        == "Employer diversity"
    )

    assert (
        diversity.status
        == "WARNING"
    )


def test_report_contains_metrics(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "market.db"
    )

    history = MarketRefreshHistory(
        tmp_path / "history.db"
    )

    db.add_job(
        JobMarketRecord(
            job_title="Data Engineer",
            company="Company A",
        ),
        prevent_duplicates=False,
    )

    service = MarketSystemHealthService(
        database=db,
        history=history,
        registry=FakeRegistry(
            count=23
        ),
    )

    report = service.evaluate()

    assert report.production_jobs == 1
    assert report.companies == 1
    assert report.enabled_sources == 23
