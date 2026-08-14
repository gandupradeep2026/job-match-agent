from market_intelligence.metadata_quality import (
    JobMetadataNormalizer,
)
from market_intelligence.models import (
    JobMarketRecord,
)


def test_country_from_location():

    country = (
        JobMetadataNormalizer
        .infer_country(
            location=(
                "Berlin, Germany"
            )
        )
    )

    assert country == "Germany"


def test_country_from_german_location():

    country = (
        JobMetadataNormalizer
        .infer_country(
            location=(
                "Deutschland, remote"
            )
        )
    )

    assert country == "Germany"


def test_explicit_country_wins():

    country = (
        JobMetadataNormalizer
        .infer_country(
            explicit_country="Austria",
            location="Berlin, Germany",
        )
    )

    assert country == "Austria"


def test_senior_title_overrides_bad_result():

    seniority = (
        JobMetadataNormalizer
        .resolve_seniority(
            job_title=(
                "Senior Data Engineer"
            ),
            current_seniority=(
                "Entry-level"
            ),
        )
    )

    assert seniority == "Senior"


def test_staff_engineer_is_senior():

    seniority = (
        JobMetadataNormalizer
        .resolve_seniority(
            job_title=(
                "Staff Engineer - Data & AI"
            ),
            current_seniority=(
                "Not specified"
            ),
        )
    )

    assert seniority == "Senior"


def test_junior_engineer_is_entry_level():

    seniority = (
        JobMetadataNormalizer
        .resolve_seniority(
            job_title=(
                "Junior Data Engineer"
            )
        )
    )

    assert (
        seniority
        == "Entry-level"
    )


def test_normalizes_complete_record():

    job = JobMarketRecord(
        job_title=(
            "Senior Data Engineer"
        ),
        location=(
            "Berlin, Germany"
        ),
        country="",
        seniority=(
            "Entry-level"
        ),
    )

    result = (
        JobMetadataNormalizer
        .normalize_record(
            job
        )
    )

    assert (
        result.country
        == "Germany"
    )

    assert (
        result.seniority
        == "Senior"
    )
