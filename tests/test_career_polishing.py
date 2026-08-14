import json
from types import SimpleNamespace

from career.polishing import (
    CareerPolishRequest,
)
import services.career_polishing_service as service


def _fake_response(
    payload: dict,
):
    return SimpleNamespace(
        message=SimpleNamespace(
            content=json.dumps(
                payload
            )
        )
    )


def test_prompt_contains_truth_lock():
    request = CareerPolishRequest(
        source_text=(
            "I worked with Python."
        ),
        language="English",
        content_type=(
            "Interview Answer"
        ),
        style=(
            "Natural Professional"
        ),
    )

    prompt = (
        service
        .build_career_polish_prompt(
            request
        )
    )

    assert (
        "TRUTH LOCK"
        in prompt
    )

    assert (
        "Do not add any new employer"
        in prompt
    )


def test_empty_source_fails():
    try:
        service.polish_career_text(
            CareerPolishRequest(
                source_text="",
                language="English",
                content_type="Other",
                style=(
                    "Natural Professional"
                ),
            )
        )

    except ValueError as error:
        assert (
            "Source text is empty"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_invalid_language_fails():
    try:
        service.polish_career_text(
            CareerPolishRequest(
                source_text="Test",
                language="French",
                content_type="Other",
                style=(
                    "Natural Professional"
                ),
            )
        )

    except ValueError as error:
        assert (
            "English or Deutsch"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_successful_polish(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": (
                    "I have practical experience with Python."
                ),
                "changes_made": [
                    "Improved flow."
                ],
                "warnings": [],
            }
        ),
    )

    result = service.polish_career_text(
        CareerPolishRequest(
            source_text=(
                "I have experience with Python."
            ),
            language="English",
            content_type=(
                "Interview Answer"
            ),
            style=(
                "Natural Professional"
            ),
        )
    )

    assert (
        result.safety_passed
        is True
    )

    assert (
        "practical experience"
        in result.polished_text
    )


def test_new_numeric_claim_is_blocked(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": (
                    "I improved the process by 30%."
                ),
                "changes_made": [],
                "warnings": [],
            }
        ),
    )

    source = (
        "I improved the process."
    )

    result = service.polish_career_text(
        CareerPolishRequest(
            source_text=source,
            language="English",
            content_type="STAR Story",
            style=(
                "Natural Professional"
            ),
        )
    )

    assert (
        result.safety_passed
        is False
    )

    assert (
        result.polished_text
        == source
    )

    assert any(
        "numeric claims"
        in warning
        for warning in (
            result.warnings
        )
    )


def test_existing_number_is_allowed(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": (
                    "I achieved a 30% improvement."
                ),
                "changes_made": [],
                "warnings": [],
            }
        ),
    )

    result = service.polish_career_text(
        CareerPolishRequest(
            source_text=(
                "I improved the process by 30%."
            ),
            language="English",
            content_type="STAR Story",
            style=(
                "Concise Professional"
            ),
        )
    )

    assert (
        result.safety_passed
        is True
    )


def test_new_email_is_blocked(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": (
                    "Contact me at new@example.com."
                ),
                "changes_made": [],
                "warnings": [],
            }
        ),
    )

    result = service.polish_career_text(
        CareerPolishRequest(
            source_text=(
                "Please contact me."
            ),
            language="English",
            content_type="Other",
            style=(
                "Natural Professional"
            ),
        )
    )

    assert (
        result.safety_passed
        is False
    )


def test_new_url_is_blocked(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": (
                    "See https://example.com for details."
                ),
                "changes_made": [],
                "warnings": [],
            }
        ),
    )

    result = service.polish_career_text(
        CareerPolishRequest(
            source_text=(
                "See my portfolio for details."
            ),
            language="English",
            content_type="Other",
            style=(
                "Natural Professional"
            ),
        )
    )

    assert (
        result.safety_passed
        is False
    )


def test_empty_ai_text_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "get_ollama_model",
        lambda: "test-model",
    )

    monkeypatch.setattr(
        service,
        "chat",
        lambda **kwargs: _fake_response(
            {
                "polished_text": "",
                "changes_made": [],
                "warnings": [],
            }
        ),
    )

    try:
        service.polish_career_text(
            CareerPolishRequest(
                source_text="Verified text.",
                language="English",
                content_type="Other",
                style=(
                    "Natural Professional"
                ),
            )
        )

    except ValueError as error:
        assert (
            "empty polished text"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )
