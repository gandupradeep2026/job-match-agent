from typing import Any


PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def _normalise_text(value: Any) -> str:
    """
    Convert supported values into a clean text string.
    """

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        for key in (
            "explanation",
            "title",
            "message",
            "text",
        ):
            text = value.get(key)

            if isinstance(text, str) and text.strip():
                return text.strip()

    return ""


def _normalise_items(
    value: Any,
) -> list[dict]:
    """
    Convert recommendation values into a consistent list of dictionaries.
    """

    if not isinstance(value, list):
        return []

    items = []

    for raw_item in value:
        if isinstance(raw_item, str):
            text = raw_item.strip()

            if text:
                items.append(
                    {
                        "title": text,
                        "explanation": text,
                        "importance": "medium",
                        "cv_evidence": "",
                        "job_evidence": "",
                    }
                )

        elif isinstance(raw_item, dict):
            title = _normalise_text(
                raw_item.get("title", "")
            )

            explanation = _normalise_text(
                raw_item.get("explanation", "")
            )

            if not title and explanation:
                title = explanation

            if not explanation and title:
                explanation = title

            if not title:
                continue

            importance = str(
                raw_item.get(
                    "importance",
                    "medium",
                )
            ).strip().lower()

            if importance not in {
                "high",
                "medium",
                "low",
            }:
                importance = "medium"

            items.append(
                {
                    "title": title,
                    "explanation": explanation,
                    "importance": importance,
                    "cv_evidence": _normalise_text(
                        raw_item.get(
                            "cv_evidence",
                            "",
                        )
                    ),
                    "job_evidence": _normalise_text(
                        raw_item.get(
                            "job_evidence",
                            "",
                        )
                    ),
                }
            )

    return items


def _build_rejection_reasons(
    ats_result: dict,
    match_result: dict,
    cv_recommendations: dict,
) -> list[dict]:
    """
    Build evidence-based reasons a recruiter may hesitate.
    """

    reasons = []

    missing_requirements = _normalise_items(
        cv_recommendations.get(
            "missing_requirements",
            [],
        )
    )

    weak_evidence = _normalise_items(
        cv_recommendations.get(
            "weakly_evidenced_skills",
            [],
        )
    )

    important_warnings = cv_recommendations.get(
        "important_warnings",
        [],
    )

    for item in missing_requirements:
        reasons.append(
            {
                "title": item["title"],
                "explanation": item["explanation"],
                "priority": item["importance"],
                "cv_evidence": item["cv_evidence"],
                "job_evidence": item["job_evidence"],
                "source": "AI CV comparison",
            }
        )

    for item in weak_evidence:
        reasons.append(
            {
                "title": item["title"],
                "explanation": item["explanation"],
                "priority": item["importance"],
                "cv_evidence": item["cv_evidence"],
                "job_evidence": item["job_evidence"],
                "source": "AI CV comparison",
            }
        )

    if isinstance(important_warnings, list):
        for warning in important_warnings:
            warning_text = _normalise_text(
                warning
            )

            if warning_text:
                reasons.append(
                    {
                        "title": "Credibility or accuracy warning",
                        "explanation": warning_text,
                        "priority": "high",
                        "cv_evidence": "",
                        "job_evidence": "",
                        "source": "AI warning",
                    }
                )

    missing_keywords = match_result.get(
        "missing_keywords",
        [],
    )

    frequency_data = match_result.get(
        "job_skill_frequency",
        {},
    )

    if isinstance(missing_keywords, list):
        sorted_keywords = sorted(
            [
                str(keyword).strip()
                for keyword in missing_keywords
                if str(keyword).strip()
            ],
            key=lambda keyword: (
                frequency_data.get(
                    keyword,
                    1,
                )
            ),
            reverse=True,
        )

        for keyword in sorted_keywords[:8]:
            frequency = int(
                frequency_data.get(
                    keyword,
                    1,
                )
                or 1
            )

            reasons.append(
                {
                    "title": (
                        f"Requirement not evidenced: {keyword}"
                    ),
                    "explanation": (
                        "This requirement appears in the job description "
                        "but was not detected in the CV."
                    ),
                    "priority": (
                        "high"
                        if frequency >= 3
                        else "medium"
                    ),
                    "cv_evidence": (
                        f"No recognised evidence of {keyword} "
                        "was detected in the CV."
                    ),
                    "job_evidence": (
                        f"{keyword} was mentioned "
                        f"{frequency} time(s)."
                    ),
                    "source": "Keyword analysis",
                }
            )

    checks = ats_result.get(
        "checks",
        [],
    )

    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue

            passed = bool(
                check.get(
                    "passed",
                    False,
                )
            )

            points = float(
                check.get(
                    "points",
                    0,
                )
                or 0
            )

            max_points = float(
                check.get(
                    "max_points",
                    points,
                )
                or points
            )

            lost_points = float(
                check.get(
                    "lost_points",
                    max(
                        max_points - points,
                        0,
                    ),
                )
                or 0
            )

            if passed and lost_points <= 0:
                continue

            title = _normalise_text(
                check.get(
                    "name",
                    "ATS issue",
                )
            )

            message = _normalise_text(
                check.get(
                    "message",
                    "",
                )
            )

            reasons.append(
                {
                    "title": title or "ATS issue",
                    "explanation": (
                        message
                        or "This ATS check was not fully satisfied."
                    ),
                    "priority": (
                        str(
                            check.get(
                                "priority",
                                "medium",
                            )
                        ).lower()
                    ),
                    "cv_evidence": "",
                    "job_evidence": "",
                    "source": "ATS analysis",
                }
            )

    unique_reasons = []
    seen = set()

    for reason in reasons:
        key = (
            reason["title"].strip().lower(),
            reason["explanation"].strip().lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_reasons.append(reason)

    unique_reasons.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(
                item.get(
                    "priority",
                    "medium",
                ),
                3,
            ),
            item.get(
                "title",
                "",
            ).lower(),
        )
    )

    return unique_reasons


def _build_convincing_actions(
    cv_recommendations: dict,
    rejection_reasons: list[dict],
) -> list[str]:
    """
    Build truthful actions that could strengthen the application.
    """

    actions = []

    improvement_items = _normalise_items(
        cv_recommendations.get(
            "improvement_suggestions",
            [],
        )
    )

    for item in improvement_items:
        text = item["explanation"]

        if text and text not in actions:
            actions.append(text)

    for reason in rejection_reasons:
        title = reason.get(
            "title",
            "",
        )

        if title.startswith(
            "Requirement not evidenced:"
        ):
            requirement = title.split(
                ":",
                1,
            )[-1].strip()

            action = (
                f"Add truthful evidence of {requirement} only if you "
                "can support it with real work, study, or project experience."
            )

        elif reason.get(
            "source"
        ) == "ATS analysis":
            action = (
                f"Fix the ATS issue: {title}. "
                "Use simple, standard CV formatting and clear section names."
            )

        else:
            action = (
                f"Strengthen or clarify: {title}. "
                "Use specific evidence already present in your background."
            )

        if action not in actions:
            actions.append(action)

    return actions[:8]


def _calculate_probability(
    ats_score: float,
    skill_score: float,
    overall_score: float,
    high_priority_count: int,
    medium_priority_count: int,
) -> int:
    """
    Calculate a transparent interview-readiness estimate.

    This is a heuristic, not a prediction of an employer decision.
    """

    base_score = (
        overall_score * 0.50
        + skill_score * 0.30
        + ats_score * 0.20
    )

    penalty = (
        high_priority_count * 5
        + medium_priority_count * 2
    )

    probability = round(
        max(
            min(
                base_score - penalty,
                95,
            ),
            5,
        )
    )

    return int(
        probability
    )


def generate_recruiter_decision(
    ats_result: dict,
    match_result: dict,
    job_match_result: dict,
    cv_recommendations: dict,
    extracted_job_details: dict,
) -> dict:
    """
    Generate an explainable recruiter-style decision report.
    """

    ats_score = float(
        ats_result.get(
            "score",
            0,
        )
        or 0
    )

    skill_score = float(
        match_result.get(
            "score",
            0,
        )
        or 0
    )

    overall_score = float(
        job_match_result.get(
            "score",
            0,
        )
        or 0
    )

    rejection_reasons = _build_rejection_reasons(
        ats_result=ats_result,
        match_result=match_result,
        cv_recommendations=cv_recommendations,
    )

    high_priority_count = sum(
        1
        for item in rejection_reasons
        if item.get(
            "priority"
        ) == "high"
    )

    medium_priority_count = sum(
        1
        for item in rejection_reasons
        if item.get(
            "priority"
        ) == "medium"
    )

    probability = _calculate_probability(
        ats_score=ats_score,
        skill_score=skill_score,
        overall_score=overall_score,
        high_priority_count=high_priority_count,
        medium_priority_count=medium_priority_count,
    )

    if probability >= 75:
        decision = "Likely interview"
        decision_level = "positive"
        summary = (
            "The application appears competitive, although the listed "
            "weaknesses should still be reviewed."
        )
    elif probability >= 55:
        decision = "Possible interview"
        decision_level = "mixed"
        summary = (
            "The application has relevant strengths, but important gaps "
            "may prevent an interview."
        )
    else:
        decision = "Interview unlikely without revision"
        decision_level = "negative"
        summary = (
            "The current CV-job fit has substantial weaknesses. "
            "Revise the application before submitting."
        )

    company = _normalise_text(
        extracted_job_details.get(
            "company",
            "",
        )
    )

    job_title = _normalise_text(
        extracted_job_details.get(
            "job_title",
            "",
        )
    )

    convincing_actions = _build_convincing_actions(
        cv_recommendations=cv_recommendations,
        rejection_reasons=rejection_reasons,
    )

    return {
        "decision": decision,
        "decision_level": decision_level,
        "summary": summary,
        "interview_probability": probability,
        "company": company,
        "job_title": job_title,
        "scores": {
            "overall_match": round(
                overall_score,
                1,
            ),
            "skill_match": round(
                skill_score,
                1,
            ),
            "ats_score": round(
                ats_score,
                1,
            ),
        },
        "high_priority_count": high_priority_count,
        "medium_priority_count": medium_priority_count,
        "rejection_reasons": rejection_reasons[:10],
        "convincing_actions": convincing_actions,
        "disclaimer": (
            "This is an explainable heuristic based on your app's "
            "analysis results. It is not an employer decision or a "
            "guaranteed interview probability."
        ),
    }
