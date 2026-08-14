from market_intelligence.metadata_quality import (
    JobMetadataNormalizer,
)


def test_explicit_de_country_code():

    result = (
        JobMetadataNormalizer
        .infer_country(
            explicit_country="DE"
        )
    )

    assert result == "Germany"


def test_berlin_location():

    result = (
        JobMetadataNormalizer
        .infer_country(
            location="Berlin"
        )
    )

    assert result == "Germany"


def test_remote_berlin_location():

    result = (
        JobMetadataNormalizer
        .infer_country(
            location="Remote / Berlin"
        )
    )

    assert result == "Germany"


def test_munich_de_and_berlin_de():

    result = (
        JobMetadataNormalizer
        .infer_country(
            location=(
                "Munich (DE) / Berlin (DE)"
            )
        )
    )

    assert result == "Germany"


def test_german_city_with_remote():

    result = (
        JobMetadataNormalizer
        .infer_country(
            location=(
                "Hamburg / Remote"
            )
        )
    )

    assert result == "Germany"


def test_explicit_country_still_wins():

    result = (
        JobMetadataNormalizer
        .infer_country(
            explicit_country="Austria",
            location="Berlin",
        )
    )

    assert result == "Austria"


def test_unknown_location_remains_unknown():

    result = (
        JobMetadataNormalizer
        .infer_country(
            location="Remote"
        )
    )

    assert result == ""
