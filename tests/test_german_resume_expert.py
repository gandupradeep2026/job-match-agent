from services.german_cv_checks import (
    analyse_achievement_quality,
    analyse_contact_details,
    analyse_cv_length,
    analyse_cv_structure,
    analyse_german_market_details,
    analyse_language_profile,
    detect_language_level,
    run_german_cv_checks,
)
from services.recruiter_scoring import (
    calculate_recruiter_scores,
)


SAMPLE_CV = """
Rahul Sharma

Email: rahul.sharma@email.com
Phone: +91 9876543210
LinkedIn: https://linkedin.com/in/rahulsharma
GitHub: https://github.com/rahulsharma

Professional Summary

Junior IT professional interested in system administration
and cloud technologies.

Technical Skills

Windows Server
Linux
Active Directory
Microsoft Azure
DNS
DHCP
Python

Professional Experience

IT Support Intern
January 2024 - June 2024

- Configured user accounts in Active Directory.
- Resolved DNS and DHCP incidents.
- Supported Microsoft 365 users.
- Documented technical issues.
- Improved internal documentation for 20 users.

Education

Bachelor of Technology in Computer Science
2020 - 2024

Projects

- Built an Azure-based file server.
- Implemented Active Directory authentication.

Languages

German - B1
English - C1

Open to relocation to Germany.
Visa status: Requires sponsorship.
"""


def build_category_match_result() -> dict:
    return {
        "overall_score": 76.0,
        "categories": {
            "required_skills": {
                "score": 80.0,
                "matched": [
                    "Windows Server",
                    "Linux",
                    "Active Directory",
                    "DNS",
                    "DHCP",
                ],
                "missing": [
                    "PowerShell",
                ],
                "status": "calculated",
            },
            "experience": {
                "score": 65.0,
                "matched": [
                    "IT support",
                ],
                "missing": [
                    "two years professional experience",
                ],
                "status": "calculated",
            },
            "responsibilities": {
                "score": 75.0,
                "matched": [
                    "Support users",
                    "Manage Active Directory",
                ],
                "missing": [
                    "Automate tasks",
                ],
                "status": "calculated",
            },
            "languages": {
                "score": 50.0,
                "matched": [
                    "English C1",
                ],
                "missing": [
                    "German B2",
                ],
                "status": "calculated",
            },
        },
    }


def test_detect_german_language_level() -> None:
    result = detect_language_level(
        SAMPLE_CV,
        "german",
    )

    assert result == "B1"


def test_detect_english_language_level() -> None:
    result = detect_language_level(
        SAMPLE_CV,
        "english",
    )

    assert result == "C1"


def test_contact_details_score() -> None:
    result = analyse_contact_details(
        SAMPLE_CV
    )

    assert result["checks"]["email"] is True
    assert result["checks"]["phone"] is True
    assert result["checks"]["linkedin"] is True
    assert result["checks"]["github"] is True
    assert result["score"] >= 80


def test_cv_structure_detects_main_sections() -> None:
    result = analyse_cv_structure(
        SAMPLE_CV
    )

    assert result["sections"]["summary"] is True
    assert result["sections"]["experience"] is True
    assert result["sections"]["education"] is True
    assert result["sections"]["skills"] is True
    assert result["sections"]["projects"] is True
    assert result["sections"]["languages"] is True
    assert result["score"] == 100.0


def test_language_profile_score() -> None:
    result = analyse_language_profile(
        SAMPLE_CV
    )

    assert result["german_level"] == "B1"
    assert result["english_level"] == "C1"
    assert result["score"] == 100.0


def test_achievement_quality_detects_bullets_and_numbers() -> None:
    result = analyse_achievement_quality(
        SAMPLE_CV
    )

    assert result["bullet_count"] >= 5
    assert result["action_verb_count"] >= 4
    assert result["numeric_achievement_count"] >= 1
    assert result["score"] > 0


def test_german_market_details_detect_relocation_and_visa() -> None:
    result = analyse_german_market_details(
        SAMPLE_CV
    )

    assert result["checks"]["relocation"] is True
    assert result["checks"]["work_authorization"] is True
    assert result["score"] >= 80


def test_cv_length_returns_valid_score() -> None:
    result = analyse_cv_length(
        SAMPLE_CV
    )

    assert result["word_count"] > 0
    assert 0.0 <= result["score"] <= 100.0
    assert result["message"]


def test_complete_german_cv_checks() -> None:
    result = run_german_cv_checks(
        SAMPLE_CV
    )

    assert "contact" in result
    assert "structure" in result
    assert "language" in result
    assert "achievements" in result
    assert "german_market" in result
    assert "length" in result
    assert isinstance(
        result["strengths"],
        list,
    )
    assert isinstance(
        result["improvements"],
        list,
    )


def test_recruiter_scoring_returns_expected_structure() -> None:
    german_checks = run_german_cv_checks(
        SAMPLE_CV
    )

    result = calculate_recruiter_scores(
        german_cv_checks=german_checks,
        ats_result={
            "score": 88.0,
        },
        job_match_result={
            "score": 74.0,
        },
        match_result={
            "score": 78.0,
        },
        category_match_result=(
            build_category_match_result()
        ),
    )

    assert 0.0 <= result[
        "recruiter_score"
    ] <= 100.0

    assert 0.0 <= result[
        "interview_probability"
    ] <= 100.0

    assert 0.0 <= result[
        "required_skill_score"
    ] <= 100.0

    assert "components" in result
    assert "recommendation" in result
    assert "strengths" in result
    assert "priority_improvements" in result


def test_recruiter_score_contains_all_components() -> None:
    german_checks = run_german_cv_checks(
        SAMPLE_CV
    )

    result = calculate_recruiter_scores(
        german_cv_checks=german_checks,
        ats_result={
            "score": 88.0,
        },
        job_match_result={
            "score": 74.0,
        },
        match_result={
            "score": 78.0,
        },
        category_match_result=(
            build_category_match_result()
        ),
    )

    expected_components = {
        "job_match",
        "ats_compatibility",
        "german_cv_quality",
        "experience_evidence",
        "professional_branding",
        "language_profile",
    }

    assert set(
        result["components"].keys()
    ) == expected_components


def test_recruiter_improvements_include_missing_required_skill() -> None:
    german_checks = run_german_cv_checks(
        SAMPLE_CV
    )

    result = calculate_recruiter_scores(
        german_cv_checks=german_checks,
        ats_result={
            "score": 88.0,
        },
        job_match_result={
            "score": 74.0,
        },
        match_result={
            "score": 78.0,
        },
        category_match_result=(
            build_category_match_result()
        ),
    )

    joined_improvements = " ".join(
        result[
            "priority_improvements"
        ]
    ).lower()

    assert "powershell" in joined_improvements