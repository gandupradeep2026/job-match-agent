from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.models import JobMarketRecord


def _germany_filter():
    return MarketCollectionFilter(
        allowed_countries=["Germany"],
    )


def _job(location: str):
    return JobMarketRecord(
        job_title="Test Job",
        country="Germany",
        location=location,
    )


def test_rejects_us_only_location_mislabeled_as_germany():
    assert not _germany_filter().allows(
        _job("Washington DC; Denver, CO")
    )


def test_rejects_london_only_location_mislabeled_as_germany():
    assert not _germany_filter().allows(
        _job("London")
    )


def test_keeps_multilocation_job_when_germany_is_in_location():
    assert _germany_filter().allows(
        _job(
            "Berlin, Germany; Haarlem, Netherlands; London, UK"
        )
    )


def test_keeps_remote_multicountry_job_when_germany_is_listed():
    assert _germany_filter().allows(
        _job("Germany /Spain / Romania (Remote)")
    )


def test_keeps_normal_german_location():
    assert _germany_filter().allows(
        _job("Magdeburg, Saxony-Anhalt, Germany")
    )
