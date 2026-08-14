import pytest

from market_intelligence.market_taxonomy import (
    classify_market_job,
    subcategories_for_family,
    supported_market_families,
)


def test_has_nineteen_market_families():
    families = supported_market_families()

    assert len(families) == 19

    expected = {
        "Automotive & Mobility",
        "AI Engineering",
        "Cloud Engineering & DevOps",
        "Machine Learning",
        "Data Science & Analytics",
        "IT Support & Operations",
        "Software Development",
        "Agentic AI & LLM",
        "IT Administration & Infrastructure",
        "Data Engineering",
        "Cybersecurity",
        "Product & Project Management",
        "Finance & Accounting",
        "Sales & Business Development",
        "Marketing & Communications",
        "Human Resources",
        "Supply Chain & Logistics",
        "Manufacturing & Industrial Engineering",
        "Hospitality & Customer Service",
    }

    assert set(families) == expected


@pytest.mark.parametrize(
    (
        "title",
        "description",
        "legacy_family",
        "expected_family",
        "expected_role",
    ),
    [
        (
            "Automotive Software Engineer",
            "AUTOSAR ECU CAN",
            "Automotive",
            "Automotive & Mobility",
            "Automotive Software Engineer",
        ),
        (
            "Generative AI Engineer",
            "Build enterprise GenAI systems.",
            "AI & Machine Learning",
            "AI Engineering",
            "Generative AI Engineer",
        ),
        (
            "Cloud Engineer",
            "AWS Azure GCP Kubernetes.",
            "Cloud & DevOps",
            "Cloud Engineering & DevOps",
            "Cloud Engineer",
        ),
        (
            "Machine Learning Engineer",
            "Train and deploy ML models.",
            "AI & Machine Learning",
            "Machine Learning",
            "Machine Learning Engineer",
        ),
        (
            "Data Scientist",
            "Statistics and experimentation.",
            "Data & Analytics",
            "Data Science & Analytics",
            "Data Scientist",
        ),
        (
            "IT Support Specialist",
            "Service desk and desktop support.",
            "Customer Support",
            "IT Support & Operations",
            "IT Support Specialist",
        ),
        (
            "Backend Developer",
            "Develop backend applications.",
            "Software Engineering",
            "Software Development",
            "Backend Developer",
        ),
        (
            "Agentic AI Engineer",
            "Build multi-agent LLM workflows.",
            "AI & Machine Learning",
            "Agentic AI & LLM",
            "Agentic AI Engineer",
        ),
        (
            "Linux Administrator",
            "Operate Linux infrastructure.",
            "Other",
            "IT Administration & Infrastructure",
            "Linux Administrator",
        ),
        (
            "Cloud Data Engineer",
            "Build GCP and BigQuery pipelines.",
            "Data & Analytics",
            "Data Engineering",
            "Cloud Data Engineer",
        ),
        (
            "Security Engineer",
            "Cybersecurity engineering.",
            "Other",
            "Cybersecurity",
            "Security Engineer",
        ),
        (
            "Technical Product Manager",
            "Own technical product roadmap.",
            "Other",
            "Product & Project Management",
            "Technical Product Manager",
        ),
        (
            "Financial Analyst",
            "Financial planning.",
            "Finance & Accounting",
            "Finance & Accounting",
            "Financial Analyst",
        ),
        (
            "Business Development Manager",
            "Develop strategic accounts.",
            "Sales",
            "Sales & Business Development",
            "Business Development Manager",
        ),
        (
            "Product Marketing Manager",
            "Go-to-market strategy.",
            "Marketing",
            "Marketing & Communications",
            "Product Marketing Manager",
        ),
        (
            "Recruiter",
            "Talent acquisition.",
            "Human Resources",
            "Human Resources",
            "Recruiter",
        ),
        (
            "Supply Chain Analyst",
            "Supply planning.",
            "Logistics & Supply Chain",
            "Supply Chain & Logistics",
            "Supply Chain Analyst",
        ),
        (
            "Manufacturing Engineer",
            "Industrial production.",
            "Mechanical Engineering",
            "Manufacturing & Industrial Engineering",
            "Manufacturing Engineer",
        ),
        (
            "Hotel Receptionist",
            "Front office guest support.",
            "Hospitality",
            "Hospitality & Customer Service",
            "Receptionist",
        ),
    ],
)
def test_market_taxonomy_classification(
    title,
    description,
    legacy_family,
    expected_family,
    expected_role,
):
    result = classify_market_job(
        job_title=title,
        description=description,
        legacy_job_family=legacy_family,
    )

    assert (
        result.job_family
        == expected_family
    )

    assert (
        result.subcategory
        == expected_role
    )


def test_each_family_has_subcategories():
    for family in supported_market_families():
        assert subcategories_for_family(
            family
        )
