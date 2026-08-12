from services.cv_section_improver import (
    ALLOWED_SECTIONS,
    create_section_improvement,
)


def test_allowed_sections() -> None:
    assert "Professional Summary" in ALLOWED_SECTIONS
    assert "Skills" in ALLOWED_SECTIONS
    assert "Experience" in ALLOWED_SECTIONS
    assert "Projects" in ALLOWED_SECTIONS


def test_invalid_section_rejected() -> None:
    try:
        create_section_improvement(
            cv_text="A valid CV with enough content.",
            job_text="A valid job description.",
            section_name="Unknown",
            section_text="Some section text.",
            language="English",
        )
    except ValueError as error:
        assert "Unsupported CV section" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for unsupported section."
        )
