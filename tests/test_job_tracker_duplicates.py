from services.job_tracker import (
    calculate_duplicate_confidence,
    normalize_comparison_text,
    normalize_job_url,
)


def test_normalize_comparison_text() -> None:
    result = normalize_comparison_text(
        "  Fachinformatiker  für   Systemintegration! "
    )

    assert result == (
        "fachinformatiker für systemintegration"
    )


def test_normalize_comparison_text_empty() -> None:
    assert normalize_comparison_text("") == ""
    assert normalize_comparison_text(None) == ""


def test_normalize_job_url_removes_www_query_and_fragment() -> None:
    result = normalize_job_url(
        (
            "https://www.example.com/jobs/123/"
            "?utm_source=linkedin#details"
        )
    )

    assert result == (
        "https://example.com/jobs/123"
    )


def test_normalize_job_url_adds_https() -> None:
    result = normalize_job_url(
        "example.com/jobs/123"
    )

    assert result == (
        "https://example.com/jobs/123"
    )


def test_duplicate_confidence_high_for_same_url() -> None:
    existing_application = {
        "company": "Example GmbH",
        "job_title": (
            "Fachinformatiker für Systemintegration"
        ),
        "location": "Berlin",
        "job_url": (
            "https://www.example.com/jobs/123"
            "?utm_source=linkedin"
        ),
    }

    result = calculate_duplicate_confidence(
        existing_application=(
            existing_application
        ),
        company="Different Company",
        job_title="Different Role",
        location="Munich",
        job_url=(
            "https://example.com/jobs/123"
        ),
    )

    assert result["is_duplicate"] is True
    assert result["confidence"] == "high"
    assert "Same job URL" in result["reasons"]


def test_duplicate_confidence_high_for_same_details() -> None:
    existing_application = {
        "company": "TechNova GmbH",
        "job_title": "IT Support Specialist",
        "location": "Hamburg",
        "job_url": "",
    }

    result = calculate_duplicate_confidence(
        existing_application=(
            existing_application
        ),
        company="technova gmbh",
        job_title="IT Support Specialist",
        location="Hamburg",
        job_url="",
    )

    assert result["is_duplicate"] is True
    assert result["confidence"] == "high"
    assert "Same company" in result["reasons"]
    assert "Same job title" in result["reasons"]
    assert "Same location" in result["reasons"]


def test_duplicate_confidence_medium_for_same_company_and_title() -> None:
    existing_application = {
        "company": "TechNova GmbH",
        "job_title": "IT Support Specialist",
        "location": "Berlin",
        "job_url": "",
    }

    result = calculate_duplicate_confidence(
        existing_application=(
            existing_application
        ),
        company="TechNova GmbH",
        job_title="IT Support Specialist",
        location="Munich",
        job_url="",
    )

    assert result["is_duplicate"] is True
    assert result["confidence"] == "medium"


def test_duplicate_confidence_none_for_different_job() -> None:
    existing_application = {
        "company": "TechNova GmbH",
        "job_title": "IT Support Specialist",
        "location": "Berlin",
        "job_url": "",
    }

    result = calculate_duplicate_confidence(
        existing_application=(
            existing_application
        ),
        company="CloudWorks AG",
        job_title="Python Developer",
        location="Cologne",
        job_url="",
    )

    assert result["is_duplicate"] is False
    assert result["confidence"] == "none"