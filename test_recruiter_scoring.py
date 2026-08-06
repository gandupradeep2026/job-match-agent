from services.german_cv_checks import (
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


def main() -> None:
    german_checks = run_german_cv_checks(
        SAMPLE_CV
    )

    ats_result = {
        "score": 88.0,
    }

    match_result = {
        "score": 78.0,
    }

    job_match_result = {
        "score": 74.0,
    }

    category_match_result = {
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

    result = calculate_recruiter_scores(
        german_cv_checks=german_checks,
        ats_result=ats_result,
        job_match_result=job_match_result,
        match_result=match_result,
        category_match_result=(
            category_match_result
        ),
    )

    print(
        "Recruiter score:",
        result["recruiter_score"],
    )

    print(
        "Interview probability:",
        result["interview_probability"],
    )

    print(
        "Recommendation:",
        result["recommendation"]["decision"],
    )

    print("\nComponents:")

    for name, score in result[
        "components"
    ].items():
        print(
            f"- {name}: {score}%"
        )

    print("\nStrengths:")

    for strength in result[
        "strengths"
    ]:
        print(
            f"- {strength}"
        )

    print("\nPriority improvements:")

    for improvement in result[
        "priority_improvements"
    ]:
        print(
            f"- {improvement}"
        )


if __name__ == "__main__":
    main()