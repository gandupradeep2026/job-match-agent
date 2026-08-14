from market_intelligence.metadata_quality import (
    JobMetadataNormalizer,
)


def test_us_location_overrides_description_mentioning_germany():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="Washington DC; Denver, CO",
        description="Global company with teams in Germany and Europe.",
    )
    assert result == "United States"


def test_san_francisco_is_not_mislabeled_as_germany():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="San Francisco, CA",
        description="We also operate in Germany.",
    )
    assert result == "United States"


def test_london_only_is_united_kingdom():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="London",
        description="International company operating in Germany.",
    )
    assert result == "United Kingdom"


def test_multilocation_including_germany_is_valid_germany():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="Berlin, Germany; Haarlem, Netherlands; London, UK",
        description="International role.",
    )
    assert result == "Germany"


def test_remote_multicountry_including_germany_is_valid_germany():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="Germany /Spain / Romania (Remote)",
        description="Remote role.",
    )
    assert result == "Germany"


def test_generic_remote_location_can_use_description_fallback():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="Remote",
        description="This position is available in Germany.",
    )
    assert result == "Germany"


def test_concrete_unknown_location_does_not_use_description_fallback():
    result = JobMetadataNormalizer.infer_country(
        explicit_country="",
        location="Some Concrete City",
        description="Our company has offices in Germany.",
    )
    assert result == ""
