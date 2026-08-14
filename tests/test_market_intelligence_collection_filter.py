from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.models import (
    JobMarketRecord,
)


def build_job(
    title="Data Engineer",
    country="Germany",
    family="Data & Analytics",
):

    return JobMarketRecord(
        job_title=title,
        country=country,
        job_family=family,
    )


def test_country_filter():

    policy = MarketCollectionFilter(
        allowed_countries=[
            "Germany"
        ]
    )

    assert policy.allows(
        build_job(
            country="Germany"
        )
    )

    assert not policy.allows(
        build_job(
            country="Austria"
        )
    )


def test_job_family_filter():

    policy = MarketCollectionFilter(
        allowed_job_families=[
            "Data & Analytics"
        ]
    )

    assert policy.allows(
        build_job(
            family="Data & Analytics"
        )
    )

    assert not policy.allows(
        build_job(
            family="Hospitality"
        )
    )


def test_title_keyword_filter():

    policy = MarketCollectionFilter(
        title_keywords=[
            "data"
        ]
    )

    assert policy.allows(
        build_job(
            title="Cloud Data Engineer"
        )
    )

    assert not policy.allows(
        build_job(
            title="Software Engineer"
        )
    )


def test_excluded_keyword():

    policy = MarketCollectionFilter(
        excluded_title_keywords=[
            "senior"
        ]
    )

    assert not policy.allows(
        build_job(
            title="Senior Data Engineer"
        )
    )

    assert policy.allows(
        build_job(
            title="Junior Data Engineer"
        )
    )


def test_combined_filter():

    policy = MarketCollectionFilter(
        allowed_countries=[
            "Germany"
        ],
        allowed_job_families=[
            "Data & Analytics"
        ],
    )

    assert policy.allows(
        build_job()
    )

    assert not policy.allows(
        build_job(
            country="Austria"
        )
    )


def test_empty_filter_allows_everything():

    policy = MarketCollectionFilter()

    assert (
        policy.is_active()
        is False
    )

    assert policy.allows(
        build_job(
            title="Hotel Receptionist",
            country="Austria",
            family="Hospitality",
        )
    )
