from services.interview_simulator import (
    build_question_bank,
    calculate_session_summary,
    clamp_score,
)


def test_clamp_score() -> None:
    assert clamp_score(12) == 10.0
    assert clamp_score(-2) == 0.0
    assert clamp_score("7.4") == 7.4


def test_build_question_bank() -> None:
    result = {
        "english": {
            "hr_and_motivation": [
                "Tell me about yourself.",
            ],
            "technical": [
                "Explain your Python experience.",
            ],
            "role_specific": [],
            "missing_skill_questions": [],
        }
    }

    questions = build_question_bank(
        interview_result=result,
        language="English",
        maximum_questions=5,
    )

    assert len(
        questions
    ) == 2

    assert questions[0][
        "category"
    ] == "HR and Motivation"


def test_calculate_session_summary() -> None:
    evaluations = [
        {
            "overall_score": 8,
            "scores": {
                "relevance": 8,
                "clarity": 7,
                "evidence": 6,
                "structure": 5,
                "confidence": 9,
            },
        },
        {
            "overall_score": 6,
            "scores": {
                "relevance": 7,
                "clarity": 6,
                "evidence": 5,
                "structure": 4,
                "confidence": 8,
            },
        },
    ]

    summary = calculate_session_summary(
        evaluations
    )

    assert summary[
        "average_score"
    ] == 7.0

    assert summary[
        "answered_questions"
    ] == 2

    assert summary[
        "strongest_area"
    ] == "Confidence"
