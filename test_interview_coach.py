from services.interview_coach import (
    build_interview_prompt,
)


def main() -> None:
    prompt = build_interview_prompt(
        cv_text=(
            "Junior IT candidate with Windows, "
            "Linux, Python and German B1."
        ),
        job_text=(
            "We seek an IT support trainee with "
            "Active Directory, Microsoft 365 and German B2."
        ),
        extracted_job_details={
            "company": "Example GmbH",
            "job_title": (
                "Fachinformatiker Systemintegration"
            ),
        },
        match_result={
            "missing_keywords": [
                "Active Directory",
                "Microsoft 365",
            ],
        },
        category_match_result={},
        german_recruiter_report={
            "priority_improvements": [
                "Improve German from B1 to B2.",
            ],
        },
    )

    print(prompt[:2000])


if __name__ == "__main__":
    main()