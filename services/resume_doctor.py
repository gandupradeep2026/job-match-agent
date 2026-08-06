from typing import Any


PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def clean_string_list(
    value: Any,
    maximum_items: int = 20,
) -> list[str]:
    """Return a clean, unique list of strings."""

    if not isinstance(value, list):
        return []

    cleaned_items = []

    for item in value:
        if not isinstance(item, str):
            continue

        cleaned_item = item.strip()

        if not cleaned_item:
            continue

        if cleaned_item in cleaned_items:
            continue

        cleaned_items.append(cleaned_item)

        if len(cleaned_items) >= maximum_items:
            break

    return cleaned_items


def build_ats_problems(
    ats_result: dict,
) -> list[dict]:
    """Convert failed or partial ATS checks into problems."""

    problems = []

    for check in ats_result.get("checks", []):
        max_points = check.get(
            "max_points",
            check.get("points", 0),
        )
        earned_points = check.get("points", 0)
        lost_points = check.get(
            "lost_points",
            max(max_points - earned_points, 0),
        )

        if lost_points <= 0:
            continue

        problems.append(
            {
                "category": "ATS",
                "title": check.get("name", "ATS issue"),
                "priority": check.get("priority", "medium"),
                "impact": f"{lost_points} ATS point(s) lost",
                "why_it_matters": check.get("message", ""),
                "evidence": [],
                "recommended_action": check.get(
                    "recommendation",
                    "",
                ),
                "requires_user_confirmation": False,
            }
        )

    return problems


def build_missing_skill_problems(
    match_result: dict,
) -> list[dict]:
    """Convert missing job keywords into ordered problems."""

    problems = []
    missing_keywords = clean_string_list(
        match_result.get("missing_keywords", [])
    )
    frequency_data = match_result.get(
        "job_skill_frequency",
        {},
    )

    sorted_keywords = sorted(
        missing_keywords,
        key=lambda keyword: frequency_data.get(keyword, 1),
        reverse=True,
    )

    for keyword in sorted_keywords:
        frequency = frequency_data.get(keyword, 1)
        priority = "high" if frequency >= 3 else "medium"

        problems.append(
            {
                "category": "Job match",
                "title": f"Missing job keyword: {keyword}",
                "priority": priority,
                "impact": (
                    f"Mentioned {frequency} time(s) "
                    "in the job description"
                ),
                "why_it_matters": (
                    "This requirement appears in the job description "
                    "but was not detected in the CV."
                ),
                "evidence": [
                    (
                        f"The job description mentions {keyword} "
                        f"{frequency} time(s)."
                    ),
                    f"The CV analysis did not detect {keyword}.",
                ],
                "recommended_action": (
                    f"Add {keyword} only if you genuinely have this "
                    "skill or experience. Otherwise, treat it as a "
                    "learning gap and do not make a false claim."
                ),
                "requires_user_confirmation": True,
            }
        )

    return problems


def build_ai_recommendation_problems(
    cv_recommendations: dict,
) -> list[dict]:
    """Convert local-AI recommendations into doctor items."""

    problems = []

    groups = [
        (
            "missing_requirements",
            "Missing requirement",
            "high",
            "May reduce fit for the target role",
            (
                "Address this only with truthful evidence from your "
                "real experience, education, projects, or certificates."
            ),
            True,
        ),
        (
            "weakly_evidenced_skills",
            "Weakly evidenced skill",
            "medium",
            "The skill may not be convincing to a recruiter",
            (
                "Strengthen the CV with a truthful example showing "
                "where and how you used this skill."
            ),
            True,
        ),
        (
            "improvement_suggestions",
            "CV improvement opportunity",
            "medium",
            "Could improve clarity and relevance",
            "",
            False,
        ),
        (
            "important_warnings",
            "Important warning",
            "high",
            "Potential credibility or accuracy risk",
            (
                "Review this carefully and remove or correct anything "
                "that is not fully true."
            ),
            True,
        ),
    ]

    for (
        field_name,
        title,
        priority,
        impact,
        default_action,
        confirmation_required,
    ) in groups:
        for item in clean_string_list(
            cv_recommendations.get(field_name, [])
        ):
            problems.append(
                {
                    "category": "AI review",
                    "title": title,
                    "priority": priority,
                    "impact": impact,
                    "why_it_matters": item,
                    "evidence": [],
                    "recommended_action": (
                        item
                        if field_name == "improvement_suggestions"
                        else default_action
                    ),
                    "requires_user_confirmation": (
                        confirmation_required
                    ),
                }
            )

    return problems


def build_recruiter_problems(
    german_recruiter_report: dict,
) -> list[dict]:
    """Convert German recruiter feedback into doctor items."""

    problems = []

    for item in clean_string_list(
        german_recruiter_report.get(
            "priority_improvements",
            [],
        )
    ):
        problems.append(
            {
                "category": "German recruiter",
                "title": "German-market improvement",
                "priority": "medium",
                "impact": (
                    "May affect recruiter confidence or "
                    "German-market fit"
                ),
                "why_it_matters": item,
                "evidence": [],
                "recommended_action": item,
                "requires_user_confirmation": False,
            }
        )

    return problems


def remove_duplicate_problems(
    problems: list[dict],
) -> list[dict]:
    """Remove repeated problem descriptions."""

    unique_problems = []
    seen_keys = set()

    for problem in problems:
        key = (
            str(problem.get("category", "")).strip().lower(),
            str(problem.get("title", "")).strip().lower(),
            str(problem.get("why_it_matters", "")).strip().lower(),
        )

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_problems.append(problem)

    return unique_problems


def calculate_doctor_summary(
    problems: list[dict],
) -> dict:
    """Calculate counts and an overall readiness label."""

    high_count = sum(
        problem.get("priority") == "high"
        for problem in problems
    )
    medium_count = sum(
        problem.get("priority") == "medium"
        for problem in problems
    )
    low_count = sum(
        problem.get("priority") == "low"
        for problem in problems
    )

    if high_count >= 5:
        readiness = "Major revision recommended"
    elif high_count >= 2:
        readiness = "Important improvements needed"
    elif high_count == 1 or medium_count >= 4:
        readiness = "Some improvements recommended"
    else:
        readiness = "Generally ready"

    return {
        "total_problems": len(problems),
        "high_priority": high_count,
        "medium_priority": medium_count,
        "low_priority": low_count,
        "readiness": readiness,
    }


def generate_resume_doctor_report(
    ats_result: dict,
    match_result: dict,
    cv_recommendations: dict,
    german_recruiter_report: dict,
) -> dict:
    """Build one ordered, explainable Resume Doctor report."""

    problems = []
    problems.extend(build_ats_problems(ats_result))
    problems.extend(build_missing_skill_problems(match_result))
    problems.extend(
        build_ai_recommendation_problems(cv_recommendations)
    )
    problems.extend(
        build_recruiter_problems(german_recruiter_report)
    )

    problems = remove_duplicate_problems(problems)
    problems = sorted(
        problems,
        key=lambda problem: (
            PRIORITY_ORDER.get(
                problem.get("priority", "medium"),
                3,
            ),
            problem.get("category", ""),
            problem.get("title", ""),
        ),
    )

    summary = calculate_doctor_summary(problems)

    return {
        "summary": summary,
        "problems": problems,
        "top_actions": [
            problem.get("recommended_action", "")
            for problem in problems[:8]
            if problem.get("recommended_action", "")
        ],
    }
