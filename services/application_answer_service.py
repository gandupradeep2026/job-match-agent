from __future__ import annotations

import json

from ollama import chat

from services.local_ai_service import (
    get_ollama_model,
)


def _clean_text(
    value: str,
    limit: int,
) -> str:
    cleaned = (
        value
        or ""
    ).strip()

    if len(cleaned) > limit:
        return cleaned[:limit]

    return cleaned


def generate_application_answer(
    question: str,
    applicant_profile: dict,
    cv_text: str = "",
    job_text: str = "",
    company: str = "",
    job_title: str = "",
) -> str:
    """
    Generate one cautious application-answer suggestion
    using the configured local Ollama model.

    The model is instructed not to invent factual claims.
    """

    cleaned_question = _clean_text(
        question,
        2000,
    )

    if not cleaned_question:
        raise ValueError(
            "The application question is empty."
        )

    safe_profile = {
        key: value
        for key, value
        in (
            applicant_profile
            or {}
        ).items()
        if (
            value not in {
                None,
                "",
            }
            and key != "resume"
        )
    }

    profile_json = json.dumps(
        safe_profile,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    cleaned_cv = _clean_text(
        cv_text,
        12000,
    )

    cleaned_job = _clean_text(
        job_text,
        12000,
    )

    cleaned_company = _clean_text(
        company,
        500,
    )

    cleaned_job_title = _clean_text(
        job_title,
        500,
    )

    prompt = f"""
You are helping a candidate draft one job-application answer.

Question:
{cleaned_question}

Company:
{cleaned_company}

Job title:
{cleaned_job_title}

Applicant profile:
{profile_json}

CV evidence:
{cleaned_cv}

Job-description evidence:
{cleaned_job}

Critical rules:

1. Never invent experience, skills, qualifications, dates,
   employers, certifications, language levels, salary history,
   work authorization, visa status, achievements or numbers.
2. For factual questions such as work authorization, visa status,
   salary expectation, notice period, availability, years of
   experience or language level:
   - use only information explicitly present above;
   - if the answer is not supported, return exactly:
     NEEDS_USER_INPUT: followed by a short explanation.
3. For motivation or open-ended questions, write a concise,
   professional answer grounded in the supplied CV, profile and
   job description.
4. Do not pretend the candidate has a requirement that is not
   evidenced.
5. Do not include markdown headings, bullet lists or quotation
   marks unless the question clearly requires them.
6. Keep the answer suitable for pasting directly into an
   application form.
7. Prefer 2 to 5 sentences unless a shorter factual answer is
   appropriate.

Return only the proposed answer.
""".strip()

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={
            "temperature": 0.2,
        },
    )

    response_text = (
        response.message.content
        or ""
    ).strip()

    if not response_text:
        raise ValueError(
            "The local AI returned an empty answer."
        )

    return response_text
