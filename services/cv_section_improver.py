from services.local_ai_service import (
    improve_cv_section,
)


ALLOWED_SECTIONS = {
    "Professional Summary",
    "Skills",
    "Experience",
    "Projects",
}


def create_section_improvement(
    cv_text: str,
    job_text: str,
    section_name: str,
    section_text: str,
    language: str,
) -> dict:
    """
    Validate inputs and improve one CV section.
    """

    if section_name not in ALLOWED_SECTIONS:
        raise ValueError(
            "Unsupported CV section."
        )

    result = improve_cv_section(
        cv_text=cv_text,
        job_text=job_text,
        section_name=section_name,
        section_text=section_text,
        language=language,
    )

    return {
        "section_name": result.get(
            "section_name",
            section_name,
        ),
        "original_text": result.get(
            "original_text",
            section_text,
        ),
        "improved_text": result.get(
            "improved_text",
            "",
        ),
        "explanation": result.get(
            "explanation",
            "",
        ),
        "changes_made": result.get(
            "changes_made",
            [],
        ),
        "warnings": result.get(
            "warnings",
            [],
        ),
    }
