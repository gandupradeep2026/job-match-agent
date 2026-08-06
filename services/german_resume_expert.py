from typing import Any

from services.german_cv_checks import (
    run_german_cv_checks,
)
from services.recruiter_scoring import (
    calculate_recruiter_scores,
)


def build_german_specific_suggestions(
    german_cv_checks: dict,
    recruiter_scores: dict,
) -> list[str]:
    """
    Build practical suggestions for applications
    in the German job market.
    """

    suggestions = []

    language_result = german_cv_checks.get(
        "language",
        {},
    )

    german_level = language_result.get(
        "german_level",
        "",
    )

    if not german_level:
        suggestions.append(
            "State your German language level using "
            "the CEFR scale, such as German B1 or B2."
        )

    elif german_level in {
        "A1",
        "A2",
    }:
        suggestions.append(
            "Your stated German level may be insufficient "
            "for many customer-facing or Ausbildung roles. "
            "Check the exact requirement in the advertisement."
        )

    elif german_level == "B1":
        suggestions.append(
            "German B1 may be accepted for some roles, "
            "but many employers and Ausbildung positions "
            "request German B2."
        )

    structure_result = german_cv_checks.get(
        "structure",
        {},
    )

    sections = structure_result.get(
        "sections",
        {},
    )

    if not sections.get(
        "summary",
        False,
    ):
        suggestions.append(
            "Add a short profile section of approximately "
            "three to five lines explaining your IT focus "
            "and target position."
        )

    if not sections.get(
        "projects",
        False,
    ):
        suggestions.append(
            "For junior IT and Ausbildung applications, "
            "include relevant school, personal or "
            "technical projects."
        )

    contact_result = german_cv_checks.get(
        "contact",
        {},
    )

    contact_checks = contact_result.get(
        "checks",
        {},
    )

    if not contact_checks.get(
        "linkedin",
        False,
    ):
        suggestions.append(
            "Add a complete LinkedIn profile when it "
            "supports your professional application."
        )

    if not contact_checks.get(
        "github",
        False,
    ):
        suggestions.append(
            "For technical roles, add GitHub when it "
            "contains genuine projects demonstrating "
            "your abilities."
        )

    market_result = german_cv_checks.get(
        "german_market",
        {},
    )

    market_checks = market_result.get(
        "checks",
        {},
    )

    if not market_checks.get(
        "relocation",
        False,
    ):
        suggestions.append(
            "When applying from outside Germany, clearly "
            "state whether you are willing to relocate."
        )

    if not market_checks.get(
        "work_authorization",
        False,
    ):
        suggestions.append(
            "Consider stating your visa or work-authorization "
            "situation clearly and truthfully."
        )

    required_skill_score = float(
        recruiter_scores.get(
            "required_skill_score",
            0.0,
        )
    )

    if required_skill_score < 60:
        suggestions.append(
            "The CV does not currently demonstrate enough "
            "of the required skills. Add missing skills only "
            "when you can support them with education, "
            "projects or experience."
        )

    return suggestions


def build_recruiter_notes(
    german_cv_checks: dict,
    recruiter_scores: dict,
) -> list[str]:
    """
    Create concise recruiter-style observations.
    """

    notes = []

    components = recruiter_scores.get(
        "components",
        {},
    )

    job_match = float(
        components.get(
            "job_match",
            0.0,
        )
    )

    ats_score = float(
        components.get(
            "ats_compatibility",
            0.0,
        )
    )

    german_cv_quality = float(
        components.get(
            "german_cv_quality",
            0.0,
        )
    )

    experience_score = float(
        components.get(
            "experience_evidence",
            0.0,
        )
    )

    branding_score = float(
        components.get(
            "professional_branding",
            0.0,
        )
    )

    language_score = float(
        components.get(
            "language_profile",
            0.0,
        )
    )

    if job_match >= 75:
        notes.append(
            "The candidate shows strong alignment "
            "with the target role."
        )

    elif job_match >= 55:
        notes.append(
            "The candidate shows partial alignment, "
            "but several requirements need stronger evidence."
        )

    else:
        notes.append(
            "The CV currently provides limited evidence "
            "for this specific role."
        )

    if ats_score >= 80:
        notes.append(
            "The CV is generally readable by an ATS."
        )

    else:
        notes.append(
            "The CV structure or content may reduce "
            "ATS readability."
        )

    if german_cv_quality >= 75:
        notes.append(
            "The CV follows several useful "
            "German-market conventions."
        )

    else:
        notes.append(
            "The CV needs stronger structure and "
            "German-market positioning."
        )

    if experience_score < 60:
        notes.append(
            "Experience and project evidence should "
            "be made more specific."
        )

    if branding_score < 60:
        notes.append(
            "Professional branding is incomplete, "
            "such as LinkedIn, GitHub or contact information."
        )

    if language_score < 60:
        notes.append(
            "Language evidence may not fully satisfy "
            "the job requirement."
        )

    return notes


def build_next_actions(
    recruiter_scores: dict,
    german_suggestions: list[str],
) -> list[str]:
    """
    Create an ordered list of recommended next actions.
    """

    actions = []

    priority_improvements = recruiter_scores.get(
        "priority_improvements",
        [],
    )

    for improvement in priority_improvements:
        if improvement not in actions:
            actions.append(
                improvement
            )

    for suggestion in german_suggestions:
        if suggestion not in actions:
            actions.append(
                suggestion
            )

    standard_actions = [
        (
            "Tailor the CV summary and technical skills "
            "section to the specific position."
        ),
        (
            "Verify every generated CV or cover-letter "
            "sentence before submitting the application."
        ),
        (
            "Use the application tracker to record the "
            "version of the CV and cover letter submitted."
        ),
    ]

    for action in standard_actions:
        if action not in actions:
            actions.append(
                action
            )

    return actions[:10]


def generate_german_recruiter_report(
    cv_text: str,
    ats_result: dict,
    job_match_result: dict,
    match_result: dict,
    category_match_result: dict,
) -> dict[str, Any]:
    """
    Run the German CV checks and recruiter scoring.

    Returns one unified report for the Streamlit UI.
    """

    cleaned_cv_text = cv_text.strip()

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    german_cv_checks = run_german_cv_checks(
        cleaned_cv_text
    )

    recruiter_scores = calculate_recruiter_scores(
        german_cv_checks=german_cv_checks,
        ats_result=ats_result,
        job_match_result=job_match_result,
        match_result=match_result,
        category_match_result=(
            category_match_result
        ),
    )

    german_suggestions = (
        build_german_specific_suggestions(
            german_cv_checks=(
                german_cv_checks
            ),
            recruiter_scores=(
                recruiter_scores
            ),
        )
    )

    recruiter_notes = build_recruiter_notes(
        german_cv_checks=german_cv_checks,
        recruiter_scores=recruiter_scores,
    )

    next_actions = build_next_actions(
        recruiter_scores=recruiter_scores,
        german_suggestions=(
            german_suggestions
        ),
    )

    return {
        "recruiter_score": recruiter_scores.get(
            "recruiter_score",
            0.0,
        ),
        "interview_probability": recruiter_scores.get(
            "interview_probability",
            0.0,
        ),
        "required_skill_score": recruiter_scores.get(
            "required_skill_score",
            0.0,
        ),
        "components": recruiter_scores.get(
            "components",
            {},
        ),
        "weights": recruiter_scores.get(
            "weights",
            {},
        ),
        "recommendation": recruiter_scores.get(
            "recommendation",
            {},
        ),
        "strengths": recruiter_scores.get(
            "strengths",
            [],
        ),
        "priority_improvements": recruiter_scores.get(
            "priority_improvements",
            [],
        ),
        "german_suggestions": (
            german_suggestions
        ),
        "recruiter_notes": recruiter_notes,
        "next_actions": next_actions,
        "cv_checks": german_cv_checks,
    }