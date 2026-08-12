import json
from typing import Any

import ollama

from services.local_ai_service import get_ollama_model


SIMULATOR_CATEGORIES = {
    "hr_and_motivation": "HR and Motivation",
    "technical": "Technical",
    "role_specific": "Role-Specific",
    "missing_skill_questions": "Missing-Skill Clarification",
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
        cleaned_text = cleaned_text[:-3].strip()

    return cleaned_text


def clamp_score(
    value: Any,
) -> float:
    """
    Convert a value into a score between 0 and 10.
    """

    try:
        score = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    return round(
        min(
            max(
                score,
                0.0,
            ),
            10.0,
        ),
        1,
    )


def normalise_feedback(
    parsed_result: Any,
) -> dict:
    """
    Validate and normalise simulator feedback.
    """

    if not isinstance(
        parsed_result,
        dict,
    ):
        raise ValueError(
            "The interview feedback was not a JSON object."
        )

    scores = parsed_result.get(
        "scores",
        {},
    )

    if not isinstance(
        scores,
        dict,
    ):
        scores = {}

    strengths = parsed_result.get(
        "strengths",
        [],
    )

    improvements = parsed_result.get(
        "improvements",
        [],
    )

    warnings = parsed_result.get(
        "warnings",
        [],
    )

    return {
        "overall_score": clamp_score(
            parsed_result.get(
                "overall_score",
                0,
            )
        ),
        "scores": {
            "relevance": clamp_score(
                scores.get(
                    "relevance",
                    0,
                )
            ),
            "clarity": clamp_score(
                scores.get(
                    "clarity",
                    0,
                )
            ),
            "evidence": clamp_score(
                scores.get(
                    "evidence",
                    0,
                )
            ),
            "structure": clamp_score(
                scores.get(
                    "structure",
                    0,
                )
            ),
            "confidence": clamp_score(
                scores.get(
                    "confidence",
                    0,
                )
            ),
        },
        "summary": str(
            parsed_result.get(
                "summary",
                "",
            )
        ).strip(),
        "strengths": [
            str(item).strip()
            for item in strengths
            if str(item).strip()
        ][:5],
        "improvements": [
            str(item).strip()
            for item in improvements
            if str(item).strip()
        ][:5],
        "suggested_answer": str(
            parsed_result.get(
                "suggested_answer",
                "",
            )
        ).strip(),
        "warnings": [
            str(item).strip()
            for item in warnings
            if str(item).strip()
        ][:5],
    }


def build_answer_evaluation_prompt(
    question: str,
    answer: str,
    cv_text: str,
    job_text: str,
    language: str,
) -> str:
    """
    Build the prompt for evaluating one interview answer.
    """

    return f"""
You are an experienced German IT recruiter and interview coach.

Evaluate the candidate's answer to one interview question.

Required output language: {language}

Important rules:

1. Judge only the answer that was provided.
2. Use the CV and job description only as context.
3. Never invent candidate experience, achievements, skills,
   projects, certifications, dates, language levels, or responsibilities.
4. Do not reward unsupported claims.
5. If the answer includes a claim not supported by the CV,
   mention that in warnings.
6. Score each category from 0 to 10:
   - relevance
   - clarity
   - evidence
   - structure
   - confidence
7. For behavioural answers, consider STAR structure when appropriate.
8. The suggested answer must remain truthful and use only information
   supported by the candidate's answer or CV.
9. Return valid JSON only.
10. Do not return Markdown.

Return exactly this structure:

{{
  "overall_score": 0,
  "scores": {{
    "relevance": 0,
    "clarity": 0,
    "evidence": 0,
    "structure": 0,
    "confidence": 0
  }},
  "summary": "",
  "strengths": [],
  "improvements": [],
  "suggested_answer": "",
  "warnings": []
}}

INTERVIEW QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

CV CONTEXT:
{cv_text}

JOB DESCRIPTION CONTEXT:
{job_text}
""".strip()


def evaluate_interview_answer(
    question: str,
    answer: str,
    cv_text: str,
    job_text: str,
    language: str,
) -> dict:
    """
    Evaluate one interview answer using the local Ollama model.
    """

    cleaned_question = question.strip()
    cleaned_answer = answer.strip()
    cleaned_cv_text = cv_text.strip()
    cleaned_job_text = job_text.strip()

    if not cleaned_question:
        raise ValueError(
            "The interview question is empty."
        )

    if not cleaned_answer:
        raise ValueError(
            "The interview answer is empty."
        )

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    if not cleaned_job_text:
        raise ValueError(
            "The job-description text is empty."
        )

    if language not in {
        "English",
        "German",
    }:
        raise ValueError(
            "The simulator language must be English or German."
        )

    prompt = build_answer_evaluation_prompt(
        question=cleaned_question,
        answer=cleaned_answer,
        cv_text=cleaned_cv_text,
        job_text=cleaned_job_text,
        language=language,
    )

    try:
        response = ollama.chat(
            model=get_ollama_model(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise interview evaluator."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format="json",
            options={
                "temperature": 0.1,
            },
        )

    except Exception as error:
        raise RuntimeError(
            "The local AI could not evaluate the interview answer."
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
            "The local AI returned an empty interview evaluation."
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

    return normalise_feedback(
        parsed_result
    )


def build_question_bank(
    interview_result: dict,
    language: str,
    maximum_questions: int = 10,
) -> list[dict]:
    """
    Build a simulator question bank from generated interview questions.
    """

    language_key = (
        "german"
        if language == "German"
        else "english"
    )

    language_result = interview_result.get(
        language_key,
        {},
    )

    if not isinstance(
        language_result,
        dict,
    ):
        return []

    questions = []

    for category_key, category_label in (
        SIMULATOR_CATEGORIES.items()
    ):
        category_questions = language_result.get(
            category_key,
            [],
        )

        if not isinstance(
            category_questions,
            list,
        ):
            continue

        for question in category_questions:
            cleaned_question = str(
                question
            ).strip()

            if not cleaned_question:
                continue

            questions.append(
                {
                    "category": category_label,
                    "question": cleaned_question,
                }
            )

            if len(
                questions
            ) >= maximum_questions:
                return questions

    return questions


def calculate_session_summary(
    evaluations: list[dict],
) -> dict:
    """
    Calculate final simulator-session results.
    """

    if not evaluations:
        return {
            "average_score": 0.0,
            "answered_questions": 0,
            "strongest_area": "",
            "weakest_area": "",
        }

    average_score = round(
        sum(
            float(
                item.get(
                    "overall_score",
                    0,
                )
            )
            for item in evaluations
        )
        / len(
            evaluations
        ),
        1,
    )

    score_names = [
        "relevance",
        "clarity",
        "evidence",
        "structure",
        "confidence",
    ]

    averages = {}

    for score_name in score_names:
        averages[
            score_name
        ] = round(
            sum(
                float(
                    item.get(
                        "scores",
                        {},
                    ).get(
                        score_name,
                        0,
                    )
                )
                for item in evaluations
            )
            / len(
                evaluations
            ),
            1,
        )

    strongest_area = max(
        averages,
        key=averages.get,
    )

    weakest_area = min(
        averages,
        key=averages.get,
    )

    return {
        "average_score": average_score,
        "answered_questions": len(
            evaluations
        ),
        "strongest_area": strongest_area.title(),
        "weakest_area": weakest_area.title(),
        "category_averages": averages,
    }
