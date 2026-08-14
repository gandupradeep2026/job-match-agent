from services.application_browser import (
    _validate_job_url,
    classify_application_field,
    resolve_effective_field_key,
)


def test_classifies_email():
    assert (
        classify_application_field(
            {
                "label": "Email address",
                "type": "email",
            }
        )
        == "email"
    )


def test_classifies_first_name_german():
    assert (
        classify_application_field(
            {
                "label": "Vorname",
                "type": "text",
            }
        )
        == "first_name"
    )


def test_classifies_resume():
    assert (
        classify_application_field(
            {
                "label": "Upload CV",
                "type": "file",
            }
        )
        == "resume"
    )


def test_classifies_work_authorization():
    assert (
        classify_application_field(
            {
                "label": "Are you authorized to work here?",
                "type": "select",
            }
        )
        == "work_authorization"
    )


def test_unknown_stays_unknown():
    assert (
        classify_application_field(
            {
                "label": "Tell us something interesting",
                "type": "textarea",
            }
        )
        == "unknown"
    )


def test_mapping_override():
    field = {
        "index": 4,
        "field_key": "unknown",
    }

    assert (
        resolve_effective_field_key(
            field,
            {
                "4": "email",
            },
        )
        == "email"
    )


def test_skip_override():
    field = {
        "index": 2,
        "field_key": "email",
    }

    assert (
        resolve_effective_field_key(
            field,
            {
                "2": "__skip__",
            },
        )
        == "skip"
    )


def test_custom_override():
    field = {
        "index": 7,
        "field_key": "unknown",
    }

    assert (
        resolve_effective_field_key(
            field,
            {
                "7": "__custom__",
            },
        )
        == "custom_answer"
    )


def test_url_validation():
    assert (
        _validate_job_url(
            "https://example.com/job"
        )
        == "https://example.com/job"
    )
