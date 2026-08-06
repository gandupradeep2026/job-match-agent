from typing import Any


DEFAULT_WEIGHTS = {
    "job_match": 0.30,
    "ats_compatibility": 0.20,
    "german_cv_quality": 0.20,
    "experience_evidence": 0.10,
    "professional_branding": 0.10,
    "language_profile": 0.10,
}


def clamp_score(
    value: float,
) -> float:
    """
    Keep a score between 0 and 100.
    """

    return min(
        max(
            float(value),
            0.0,
        ),
        100.0,
    )


def safe_score(
    result: dict,
    key: str = "score",
) -> float:
    """
    Read a numeric score safely from a dictionary.
    """

    try:
        return clamp_score(
            float(
                result.get(
                    key,
                    0.0,
                )
            )
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def average_scores(
    scores: list[float],
) -> float:
    """
    Return the average of available scores.
    """

    valid_scores = [
        clamp_score(score)
        for score in scores
    ]

    if not valid_scores:
        return 0.0

    return round(
        sum(valid_scores)
        / len(valid_scores),
        1,
    )


def calculate_german_cv_quality(
    german_cv_checks: dict,
) -> float:
    """
    Calculate the general German CV quality score.

    Components:
    - Structure: 35%
    - Achievement quality: 30%
    - CV length: 20%
    - German-market details: 15%
    """

    structure_score = safe_score(
        german_cv_checks.get(
            "structure",
            {},
        )
    )

    achievement_score = safe_score(
        german_cv_checks.get(
            "achievements",
            {},
        )
    )

    length_score = safe_score(
        german_cv_checks.get(
            "length",
            {},
        )
    )

    market_score = safe_score(
        german_cv_checks.get(
            "german_market",
            {},
        )
    )

    score = (
        structure_score * 0.35
        + achievement_score * 0.30
        + length_score * 0.20
        + market_score * 0.15
    )

    return round(
        clamp_score(score),
        1,
    )


def calculate_professional_branding(
    german_cv_checks: dict,
) -> float:
    """
    Calculate professional-branding quality.

    The contact analysis already includes:
    - Email
    - Phone
    - LinkedIn
    - GitHub
    - Portfolio
    """

    contact_result = german_cv_checks.get(
        "contact",
        {},
    )

    return safe_score(
        contact_result
    )


def calculate_experience_evidence(
    german_cv_checks: dict,
    category_match_result: dict,
) -> float:
    """
    Combine CV achievement quality with job-specific
    experience and responsibility matching.
    """

    achievement_score = safe_score(
        german_cv_checks.get(
            "achievements",
            {},
        )
    )

    categories = category_match_result.get(
        "categories",
        {},
    )

    experience_result = categories.get(
        "experience",
        {},
    )

    responsibility_result = categories.get(
        "responsibilities",
        {},
    )

    active_scores = [
        achievement_score,
    ]

    if (
        experience_result.get(
            "status"
        )
        != "not_specified"
    ):
        active_scores.append(
            safe_score(
                experience_result
            )
        )

    if (
        responsibility_result.get(
            "status"
        )
        != "not_specified"
    ):
        active_scores.append(
            safe_score(
                responsibility_result
            )
        )

    return average_scores(
        active_scores
    )


def calculate_language_profile_score(
    german_cv_checks: dict,
    category_match_result: dict,
) -> float:
    """
    Combine detected CV language information with
    job-specific language matching.
    """

    cv_language_score = safe_score(
        german_cv_checks.get(
            "language",
            {},
        )
    )

    categories = category_match_result.get(
        "categories",
        {},
    )

    job_language_result = categories.get(
        "languages",
        {},
    )

    if (
        job_language_result.get(
            "status"
        )
        == "not_specified"
    ):
        return cv_language_score

    job_language_score = safe_score(
        job_language_result
    )

    score = (
        cv_language_score * 0.45
        + job_language_score * 0.55
    )

    return round(
        clamp_score(score),
        1,
    )


def calculate_job_match_component(
    job_match_result: dict,
    match_result: dict,
    category_match_result: dict,
) -> float:
    """
    Calculate the job-match component using the
    multi-category score as the main source.
    """

    category_score = safe_score(
        category_match_result,
        key="overall_score",
    )

    overall_job_score = safe_score(
        job_match_result
    )

    keyword_score = safe_score(
        match_result
    )

    available_scores = []

    if category_match_result:
        available_scores.append(
            (
                category_score,
                0.60,
            )
        )

    if job_match_result:
        available_scores.append(
            (
                overall_job_score,
                0.25,
            )
        )

    if match_result:
        available_scores.append(
            (
                keyword_score,
                0.15,
            )
        )

    if not available_scores:
        return 0.0

    weighted_total = sum(
        score * weight
        for score, weight in available_scores
    )

    total_weight = sum(
        weight
        for _, weight in available_scores
    )

    return round(
        clamp_score(
            weighted_total
            / total_weight
        ),
        1,
    )


def calculate_interview_probability(
    recruiter_score: float,
    job_match_score: float,
    required_skill_score: float,
) -> float:
    """
    Produce an estimated interview probability.

    This is not an employer prediction. It is an
    explainable internal estimate.
    """

    score = (
        recruiter_score * 0.45
        + job_match_score * 0.35
        + required_skill_score * 0.20
    )

    # Keep the estimate conservative.
    score = score * 0.90

    return round(
        clamp_score(score),
        1,
    )


def determine_recruiter_recommendation(
    recruiter_score: float,
    required_skill_score: float,
    language_score: float,
) -> dict[str, str]:
    """
    Determine the recruiter-style recommendation.
    """

    if (
        recruiter_score >= 82
        and required_skill_score >= 75
        and language_score >= 60
    ):
        return {
            "decision": "Recommended for Interview",
            "level": "strong",
            "explanation": (
                "The CV shows strong overall alignment, "
                "sufficient required-skill evidence and a "
                "credible language profile."
            ),
        }

    if (
        recruiter_score >= 68
        and required_skill_score >= 55
    ):
        return {
            "decision": "Potential Interview",
            "level": "positive",
            "explanation": (
                "The candidate appears relevant, but the CV "
                "should be improved before submission."
            ),
        }

    if recruiter_score >= 50:
        return {
            "decision": "Review After Improvements",
            "level": "moderate",
            "explanation": (
                "The application has some relevant evidence, "
                "but important gaps or presentation issues remain."
            ),
        }

    return {
        "decision": "Not Yet Competitive",
        "level": "low",
        "explanation": (
            "The current CV does not provide enough evidence "
            "for this specific role."
        ),
    }


def collect_priority_improvements(
    german_cv_checks: dict,
    category_match_result: dict,
    limit: int = 8,
) -> list[str]:
    """
    Build a priority improvement list.

    Job-specific missing requirements appear first,
    followed by German CV improvements.
    """

    improvements = []

    categories = category_match_result.get(
        "categories",
        {},
    )

    required_skill_result = categories.get(
        "required_skills",
        {},
    )

    missing_required_skills = required_skill_result.get(
        "missing",
        [],
    )

    for skill in missing_required_skills:
        improvements.append(
            (
                f"Required skill not evidenced in the CV: "
                f"{skill}. Add it only when you can prove it."
            )
        )

    language_result = categories.get(
        "languages",
        {},
    )

    for language_requirement in language_result.get(
        "missing",
        [],
    ):
        improvements.append(
            (
                "Language requirement not evidenced: "
                f"{language_requirement}."
            )
        )

    experience_result = categories.get(
        "experience",
        {},
    )

    if (
        experience_result.get(
            "status"
        )
        != "not_specified"
        and safe_score(
            experience_result
        )
        < 60
    ):
        improvements.append(
            (
                "Make your relevant experience easier to verify "
                "with clear role titles, dates and evidence."
            )
        )

    for improvement in german_cv_checks.get(
        "improvements",
        [],
    ):
        if improvement not in improvements:
            improvements.append(
                improvement
            )

    return improvements[:limit]


def collect_recruiter_strengths(
    german_cv_checks: dict,
    category_match_result: dict,
    limit: int = 8,
) -> list[str]:
    """
    Build a list of strongest recruiter-positive signals.
    """

    strengths = []

    categories = category_match_result.get(
        "categories",
        {},
    )

    required_skill_result = categories.get(
        "required_skills",
        {},
    )

    required_skill_score = safe_score(
        required_skill_result
    )

    if (
        required_skill_result.get(
            "status"
        )
        != "not_specified"
    ):
        strengths.append(
            (
                "Required-skill evidence score: "
                f"{required_skill_score}%."
            )
        )

    responsibility_result = categories.get(
        "responsibilities",
        {},
    )

    responsibility_score = safe_score(
        responsibility_result
    )

    if (
        responsibility_result.get(
            "status"
        )
        != "not_specified"
        and responsibility_score >= 60
    ):
        strengths.append(
            (
                "The CV demonstrates relevant responsibility "
                f"coverage of {responsibility_score}%."
            )
        )

    for strength in german_cv_checks.get(
        "strengths",
        [],
    ):
        if strength not in strengths:
            strengths.append(
                strength
            )

    return strengths[:limit]


def calculate_recruiter_scores(
    german_cv_checks: dict,
    ats_result: dict,
    job_match_result: dict,
    match_result: dict,
    category_match_result: dict,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Calculate the complete German recruiter score.
    """

    active_weights = (
        weights.copy()
        if weights
        else DEFAULT_WEIGHTS.copy()
    )

    german_cv_quality = calculate_german_cv_quality(
        german_cv_checks
    )

    professional_branding = (
        calculate_professional_branding(
            german_cv_checks
        )
    )

    experience_evidence = (
        calculate_experience_evidence(
            german_cv_checks=(
                german_cv_checks
            ),
            category_match_result=(
                category_match_result
            ),
        )
    )

    language_profile = (
        calculate_language_profile_score(
            german_cv_checks=(
                german_cv_checks
            ),
            category_match_result=(
                category_match_result
            ),
        )
    )

    job_match_score = (
        calculate_job_match_component(
            job_match_result=(
                job_match_result
            ),
            match_result=match_result,
            category_match_result=(
                category_match_result
            ),
        )
    )

    ats_compatibility = safe_score(
        ats_result
    )

    components = {
        "job_match": job_match_score,
        "ats_compatibility": (
            ats_compatibility
        ),
        "german_cv_quality": (
            german_cv_quality
        ),
        "experience_evidence": (
            experience_evidence
        ),
        "professional_branding": (
            professional_branding
        ),
        "language_profile": (
            language_profile
        ),
    }

    total_weight = sum(
        active_weights.values()
    )

    if total_weight <= 0:
        recruiter_score = 0.0

    else:
        recruiter_score = sum(
            components[name]
            * active_weights.get(
                name,
                0.0,
            )
            for name in components
        ) / total_weight

    recruiter_score = round(
        clamp_score(
            recruiter_score
        ),
        1,
    )

    categories = category_match_result.get(
        "categories",
        {},
    )

    required_skill_result = categories.get(
        "required_skills",
        {},
    )

    if (
        required_skill_result.get(
            "status"
        )
        == "not_specified"
    ):
        required_skill_score = (
            job_match_score
        )

    else:
        required_skill_score = safe_score(
            required_skill_result
        )

    interview_probability = (
        calculate_interview_probability(
            recruiter_score=(
                recruiter_score
            ),
            job_match_score=(
                job_match_score
            ),
            required_skill_score=(
                required_skill_score
            ),
        )
    )

    recommendation = (
        determine_recruiter_recommendation(
            recruiter_score=(
                recruiter_score
            ),
            required_skill_score=(
                required_skill_score
            ),
            language_score=(
                language_profile
            ),
        )
    )

    strengths = collect_recruiter_strengths(
        german_cv_checks=(
            german_cv_checks
        ),
        category_match_result=(
            category_match_result
        ),
    )

    priority_improvements = (
        collect_priority_improvements(
            german_cv_checks=(
                german_cv_checks
            ),
            category_match_result=(
                category_match_result
            ),
        )
    )

    return {
        "recruiter_score": recruiter_score,
        "interview_probability": (
            interview_probability
        ),
        "required_skill_score": (
            required_skill_score
        ),
        "components": components,
        "weights": active_weights,
        "recommendation": recommendation,
        "strengths": strengths,
        "priority_improvements": (
            priority_improvements
        ),
    }