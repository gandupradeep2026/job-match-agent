from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_refresh import (
    MarketRefreshService,
)


class FakeSource:
    def __init__(
        self,
        provider,
        company,
    ):
        self.provider = provider
        self.company = company
        self.board = ""
        self.site = ""


class FakeCollectionFilter:
    pass


class FakeProvider:
    def __init__(
        self,
        name,
    ):
        self.provider_name = name


class FakeCollectionResult:
    def __init__(
        self,
        fetched=0,
        inserted=0,
        filtered_out=0,
        duplicates=0,
        failed=0,
    ):
        self.fetched = fetched
        self.inserted = inserted
        self.filtered_out = (
            filtered_out
        )
        self.duplicates = duplicates
        self.failed = failed


class FakeRegistry:
    def __init__(
        self,
        sources,
    ):
        self.sources = sources

    def enabled_sources(
        self,
    ):
        return self.sources

    def load_collection_filter(
        self,
    ):
        return FakeCollectionFilter()

    def build_provider(
        self,
        source,
    ):
        return FakeProvider(
            source.provider
        )


class FakeCollector:
    def __init__(
        self,
        results,
    ):
        self.results = list(
            results
        )

    def collect(
        self,
        provider,
        collection_filter,
    ):
        return self.results.pop(
            0
        )


def test_refresh_aggregates_sources(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "refresh.db"
    )

    service = MarketRefreshService(
        database=db
    )

    service.registry = FakeRegistry(
        [
            FakeSource(
                "greenhouse",
                "Company A",
            ),
            FakeSource(
                "lever",
                "Company B",
            ),
        ]
    )

    service.collector = FakeCollector(
        [
            FakeCollectionResult(
                fetched=10,
                inserted=2,
                filtered_out=7,
                duplicates=1,
                failed=0,
            ),
            FakeCollectionResult(
                fetched=5,
                inserted=1,
                filtered_out=3,
                duplicates=1,
                failed=0,
            ),
        ]
    )

    result = service.refresh()

    assert (
        result.sources_attempted
        == 2
    )

    assert result.fetched == 15
    assert result.inserted == 3
    assert result.filtered_out == 10
    assert result.duplicates == 2
    assert result.failed_jobs == 0

    assert len(
        result.source_results
    ) == 2


def test_source_result_is_healthy():

    from market_intelligence.market_refresh import (
        SourceRefreshResult,
    )

    result = SourceRefreshResult(
        company="Company",
        provider="greenhouse",
    )

    assert result.healthy is True


def test_source_error_is_unhealthy():

    from market_intelligence.market_refresh import (
        SourceRefreshResult,
    )

    result = SourceRefreshResult(
        company="Company",
        provider="greenhouse",
        source_error=(
            "HTTPError: 404"
        ),
    )

    assert result.healthy is False


def test_refresh_timestamps_exist(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "refresh.db"
    )

    service = MarketRefreshService(
        database=db
    )

    service.registry = FakeRegistry(
        []
    )

    service.collector = FakeCollector(
        []
    )

    result = service.refresh()

    assert result.started_at
    assert result.completed_at


def test_empty_registry_is_valid(
    tmp_path,
):

    db = JobMarketDatabase(
        tmp_path / "refresh.db"
    )

    service = MarketRefreshService(
        database=db
    )

    service.registry = FakeRegistry(
        []
    )

    service.collector = FakeCollector(
        []
    )

    result = service.refresh()

    assert (
        result.sources_attempted
        == 0
    )

    assert result.fetched == 0
    assert result.inserted == 0
    assert result.source_errors == 0
