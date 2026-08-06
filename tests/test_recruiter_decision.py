from services.recruiter_decision import (
    generate_recruiter_decision,
)


def test_generate_recruiter_decision() -> None:
    report = generate_recruiter_decision(
        ats_result={
            "score": 70,
            "checks": [
                {
                    "name": "Skills section",
                    "passed": False,
                    "points": 0,
                    "message": (
                        "No clear skills section was detected."
                    ),
                }
            ],
        },
        match_result={
            "score": 55,
            "missing_keywords": [
                "SQL",
            ],
            "job_skill_frequency": {
                "SQL": 3,
            },
        },
        job_match_result={
            "score": 60,
        },
        cv_recommendations={
            "missing_requirements": [],
            "weakly_evidenced_skills": [],
            "improvement_suggestions": [],
            "important_warnings": [],
        },
        extracted_job_details={
            "company": "Example GmbH",
            "job_title": "Data Analyst",
        },
    )

    assert report["company"] == "Example GmbH"
    assert report["job_title"] == "Data Analyst"
    assert 5 <= report["interview_probability"] <= 95
    assert report["rejection_reasons"]
    assert report["convincing_actions"]
