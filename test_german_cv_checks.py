from services.german_cv_checks import (
    run_german_cv_checks,
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
    result = run_german_cv_checks(
        SAMPLE_CV
    )

    print("Contact score:")
    print(result["contact"]["score"])

    print("Structure score:")
    print(result["structure"]["score"])

    print("Language score:")
    print(result["language"]["score"])

    print("Achievement score:")
    print(result["achievements"]["score"])

    print("German-market score:")
    print(result["german_market"]["score"])

    print("Strengths:")
    for strength in result["strengths"]:
        print(f"- {strength}")

    print("Improvements:")
    for improvement in result["improvements"]:
        print(f"- {improvement}")


if __name__ == "__main__":
    main()