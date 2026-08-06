def calculate_job_match_score(
    skill_score: float,
    ats_score: float,
    ats_checks: list[dict],
) -> dict:
    """
    Calculate an estimated overall job-match score.

    Weighting:
    - Skill match: 60%
    - ATS readability: 30%
    - Critical CV information: 10%
    """

    critical_check_names = {
        "Email address",
        "Phone number",
        "Experience section",
        "Education section",
    }

    critical_checks = [
        check
        for check in ats_checks
        if check["name"] in critical_check_names
    ]

    passed_critical_checks = sum(
        1
        for check in critical_checks
        if check["passed"]
    )

    if critical_checks:
        profile_completeness_score = (
            passed_critical_checks / len(critical_checks)
        ) * 100
    else:
        profile_completeness_score = 0.0

    overall_score = (
        skill_score * 0.60
        + ats_score * 0.30
        + profile_completeness_score * 0.10
    )

    overall_score = round(overall_score, 1)

    if overall_score >= 80:
        rating = "Strong Match"
        explanation = (
            "Your CV is strongly aligned with the job description."
        )

    elif overall_score >= 65:
        rating = "Good Match"
        explanation = (
            "Your CV matches many requirements, but some improvements "
            "may increase your chances."
        )

    elif overall_score >= 50:
        rating = "Moderate Match"
        explanation = (
            "Your CV has some relevant qualifications, but several "
            "important requirements may be missing."
        )

    else:
        rating = "Low Match"
        explanation = (
            "Your CV currently has limited alignment with this job."
        )

    return {
        "score": overall_score,
        "rating": rating,
        "explanation": explanation,
        "profile_completeness_score": round(
            profile_completeness_score,
            1,
        ),
        "weights": {
            "skill_match": 60,
            "ats_readability": 30,
            "profile_completeness": 10,
        },
    }