from services.local_ai_service import (
    generate_cover_letter,
)


def build_complete_cover_letter(
    cover_letter_result: dict,
    candidate_name: str,
) -> str:
    """
    Convert the structured AI response into one complete letter.
    """

    sections = []

    subject = cover_letter_result.get(
        "subject",
        "",
    ).strip()

    greeting = cover_letter_result.get(
        "greeting",
        "",
    ).strip()

    opening = cover_letter_result.get(
        "opening",
        "",
    ).strip()

    motivation = cover_letter_result.get(
        "motivation",
        "",
    ).strip()

    qualification_match = cover_letter_result.get(
        "qualification_match",
        "",
    ).strip()

    closing = cover_letter_result.get(
        "closing",
        "",
    ).strip()

    sign_off = cover_letter_result.get(
        "sign_off",
        "",
    ).strip()

    if subject:
        sections.append(subject)

    if greeting:
        sections.append(greeting)

    body_paragraphs = [
        opening,
        motivation,
        qualification_match,
        closing,
    ]

    sections.extend(
        paragraph
        for paragraph in body_paragraphs
        if paragraph
    )

    if sign_off:
        signature = sign_off

        if candidate_name.strip():
            signature = (
                f"{signature}\n"
                f"{candidate_name.strip()}"
            )

        sections.append(signature)

    return "\n\n".join(sections)


def create_cover_letter(
    cv_text: str,
    job_text: str,
    job_details: dict,
    language: str,
    candidate_name: str,
) -> dict:
    """
    Generate and format a tailored cover letter.
    """

    result = generate_cover_letter(
        cv_text=cv_text,
        job_text=job_text,
        job_details=job_details,
        language=language,
        candidate_name=candidate_name,
    )

    complete_text = build_complete_cover_letter(
        cover_letter_result=result,
        candidate_name=candidate_name,
    )

    return {
        "structured_result": result,
        "complete_text": complete_text,
        "warnings": result.get(
            "warnings",
            [],
        ),
    }