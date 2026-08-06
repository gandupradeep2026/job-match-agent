import json
from typing import Any

from services.local_ai_service import (
    get_ollama_model,
)

import ollama


DEFAULT_INTERVIEW_RESULT = {
    "english": {
        "hr_and_motivation": [],
        "technical": [],
        "role_specific": [],
        "missing_skill_questions": [],
        "questions_for_employer": [],
    },
    "german": {
        "hr_and_motivation": [],
        "technical": [],
        "role_specific": [],
        "missing_skill_questions": [],
        "questions_for_employer": [],
    },
    "preparation_tips": [],
    "warnings": [],
}


def clean_json_response(
    response_text: str,
) -> str:
    """
    Remove common Markdown code fences from AI output.
    """

    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[
            len("```json"):
        ].strip()

    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[
            len("```"):
        ].strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[
            :-3
        ].strip()

    return cleaned_text


def validate_question_list(
    value: Any,
    maximum_items: int = 8,
) -> list[str]:
    """
    Return a clean list of interview questions.
    """

    if not isinstance(
        value,
        list,
    ):
        return []

    cleaned_questions = []

    for item in value:
        if not isinstance(
            item,
            str,
        ):
            continue

        cleaned_item = item.strip()

        if not cleaned_item:
            continue

        if cleaned_item not in cleaned_questions:
            cleaned_questions.append(
                cleaned_item
            )

        if (
            len(cleaned_questions)
            >= maximum_items
        ):
            break

    return cleaned_questions


def validate_interview_section(
    section: Any,
) -> dict[str, list[str]]:
    """
    Validate one language section.
    """

    if not isinstance(
        section,
        dict,
    ):
        section = {}

    return {
        "hr_and_motivation": (
            validate_question_list(
                section.get(
                    "hr_and_motivation",
                    [],
                )
            )
        ),
        "technical": (
            validate_question_list(
                section.get(
                    "technical",
                    [],
                )
            )
        ),
        "role_specific": (
            validate_question_list(
                section.get(
                    "role_specific",
                    [],
                )
            )
        ),
        "missing_skill_questions": (
            validate_question_list(
                section.get(
                    "missing_skill_questions",
                    [],
                )
            )
        ),
        "questions_for_employer": (
            validate_question_list(
                section.get(
                    "questions_for_employer",
                    [],
                )
            )
        ),
    }


def validate_interview_result(
    parsed_result: Any,
) -> dict[str, Any]:
    """
    Validate and normalize the AI response.
    """

    if not isinstance(
        parsed_result,
        dict,
    ):
        return DEFAULT_INTERVIEW_RESULT.copy()

    return {
        "english": (
            validate_interview_section(
                parsed_result.get(
                    "english",
                    {},
                )
            )
        ),
        "german": (
            validate_interview_section(
                parsed_result.get(
                    "german",
                    {},
                )
            )
        ),
        "preparation_tips": (
            validate_question_list(
                parsed_result.get(
                    "preparation_tips",
                    [],
                ),
                maximum_items=10,
            )
        ),
        "warnings": (
            validate_question_list(
                parsed_result.get(
                    "warnings",
                    [],
                ),
                maximum_items=5,
            )
        ),
    }


def build_interview_prompt(
    cv_text: str,
    job_text: str,
    extracted_job_details: dict,
    match_result: dict,
    category_match_result: dict,
    german_recruiter_report: dict,
) -> str:
    """
    Build the structured bilingual interview prompt.
    """

    missing_keywords = match_result.get(
        "missing_keywords",
        [],
    )

    priority_improvements = (
        german_recruiter_report.get(
            "priority_improvements",
            [],
        )
    )

    extracted_details_json = json.dumps(
        extracted_job_details,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    category_result_json = json.dumps(
        category_match_result,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    missing_keywords_json = json.dumps(
        missing_keywords,
        ensure_ascii=False,
        indent=2,
    )

    priority_improvements_json = json.dumps(
        priority_improvements,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are an experienced German recruiter and IT interview coach.

Create a bilingual interview-preparation set in English and German.

Use only information supported by the CV and job description.
Do not invent experience, qualifications, projects, technologies,
certificates, achievements, language levels or responsibilities.

The questions must be realistic for the target role.

Generate these groups in both languages:

1. HR and motivation
2. Technical
3. Role-specific
4. Missing-skill clarification
5. Questions the candidate should ask the employer

Requirements:

- Generate 5 to 8 questions per group when enough information exists.
- German questions should sound natural and professional.
- English and German questions should cover similar topics,
  but do not translate them mechanically word for word.
- For missing-skill questions, ask how the candidate would handle
  gaps honestly. Do not encourage false claims.
- Include practical preparation tips.
- Include warnings when a candidate should not claim unsupported experience.
- Return valid JSON only.
- Do not use Markdown.
- Do not include explanations outside the JSON.

Return exactly this structure:

{{
  "english": {{
    "hr_and_motivation": [],
    "technical": [],
    "role_specific": [],
    "missing_skill_questions": [],
    "questions_for_employer": []
  }},
  "german": {{
    "hr_and_motivation": [],
    "technical": [],
    "role_specific": [],
    "missing_skill_questions": [],
    "questions_for_employer": []
  }},
  "preparation_tips": [],
  "warnings": []
}}

EXTRACTED JOB DETAILS:
{extracted_details_json}

CATEGORY MATCH RESULT:
{category_result_json}

MISSING KEYWORDS:
{missing_keywords_json}

RECRUITER PRIORITY IMPROVEMENTS:
{priority_improvements_json}

CV:
{cv_text}

JOB DESCRIPTION:
{job_text}
""".strip()


def generate_interview_questions(
    cv_text: str,
    job_text: str,
    extracted_job_details: dict,
    match_result: dict,
    category_match_result: dict,
    german_recruiter_report: dict,
) -> dict[str, Any]:
    """
    Generate bilingual interview questions using Ollama.
    """

    cleaned_cv_text = cv_text.strip()
    cleaned_job_text = job_text.strip()

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    if not cleaned_job_text:
        raise ValueError(
            "The job-description text is empty."
        )

    prompt = build_interview_prompt(
        cv_text=cleaned_cv_text,
        job_text=cleaned_job_text,
        extracted_job_details=(
            extracted_job_details
        ),
        match_result=match_result,
        category_match_result=(
            category_match_result
        ),
        german_recruiter_report=(
            german_recruiter_report
        ),
    )

    try:
        response = ollama.chat(
            model=get_ollama_model(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise bilingual "
                        "German IT interview coach."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format="json",
            options={
                "temperature": 0.3,
            },
        )

    except Exception as error:
        raise RuntimeError(
            "The local AI could not generate "
            "interview questions."
        ) from error

    response_text = (
        response.get(
            "message",
            {},
        ).get(
            "content",
            "",
        )
    )

    if not response_text.strip():
        raise RuntimeError(
            "The local AI returned an empty response."
        )

    cleaned_response = clean_json_response(
        response_text
    )

    try:
        parsed_result = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "The local AI returned invalid JSON."
        ) from error

    return validate_interview_result(
        parsed_result
    )