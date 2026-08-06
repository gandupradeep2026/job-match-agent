from services.resume_doctor import (
    generate_resume_doctor_report,
)


def test_generate_resume_doctor_report() -> None:
    result = generate_resume_doctor_report(
        ats_result={
            "checks": [
                {
                    "name": "Skills section",
                    "passed": False,
                    "points": 0,
                    "max_points": 10,
                    "lost_points": 10,
                    "message": (
                        "No clear skills section was detected."
                    ),
                    "recommendation": (
                        "Add a clear skills section."
                    ),
                    "priority": "high",
                }
            ]
        },
        match_result={
            "missing_keywords": ["Active Directory"],
            "job_skill_frequency": {
                "Active Directory": 3,
            },
        },
        cv_recommendations={
            "missing_requirements": [],
            "weakly_evidenced_skills": [],
            "improvement_suggestions": [],
            "important_warnings": [],
        },
        german_recruiter_report={
            "priority_improvements": [],
        },
    )

    assert result["summary"]["total_problems"] == 2
    assert result["summary"]["high_priority"] == 2
    assert result["problems"][0]["priority"] == "high"
    assert result["top_actions"]
