import pytest

from market_intelligence.job_parser import UniversalJobParser


parser = UniversalJobParser()


def test_parses_complete_data_engineer_job():
    job = parser.parse(
        job_title="Junior Data Engineer",
        company="Example GmbH",
        location="Berlin",
        country="Germany",
        description="""
        We are looking for a Junior Data Engineer.

        Python, SQL and Apache Spark experience is required.
        Docker is nice to have.

        At least 2 years of professional experience are required.

        German B2 and English are required.

        This is a full-time hybrid position.
        """,
    )

    assert job.job_title == "Junior Data Engineer"
    assert job.company == "Example GmbH"

    assert job.job_family == "Data & Analytics"
    assert job.occupation == "Data Engineer"
    assert job.seniority == "Entry-level"

    assert "Python" in job.required_skills
    assert "SQL" in job.required_skills
    assert "Apache Spark" in job.required_skills

    assert "Docker" in job.preferred_skills

    assert "German" in job.required_languages
    assert "English" in job.required_languages

    assert job.experience_years == 2
    assert job.employment_type == "Full-time"
    assert job.work_mode == "Hybrid"


def test_parses_hospitality_job():
    job = parser.parse(
        job_title="Hotel Receptionist",
        company="Hotel Beispiel",
        location="Chemnitz",
        country="Germany",
        description="""
        Erfahrung im Kundenservice,
        an der Rezeption und mit Reservierungssystemen.

        Deutsch und Englisch erforderlich.

        Die Stelle ist in Teilzeit und vor Ort.
        """,
    )

    assert job.job_family == "Hospitality"
    assert job.occupation == "Receptionist"

    assert "Customer Service" in job.required_skills
    assert "Front Office" in job.required_skills
    assert "Reservation Management" in job.required_skills

    assert "German" in job.required_languages
    assert "English" in job.required_languages

    assert job.employment_type == "Part-time"
    assert job.work_mode == "On-site"


def test_parses_automotive_job():
    job = parser.parse(
        job_title="Automotive Software Engineer",
        description="""
        Development of automotive software.

        Experience with AUTOSAR,
        CAN bus, ISO 26262,
        MATLAB and Simulink is required.
        """,
    )

    assert job.job_family == "Automotive"
    assert job.occupation == "Automotive Software Engineer"

    assert "AUTOSAR" in job.required_skills
    assert "CAN Bus" in job.required_skills
    assert "ISO 26262" in job.required_skills
    assert "MATLAB" in job.required_skills
    assert "Simulink" in job.required_skills


def test_preserves_source_metadata():
    job = parser.parse(
        job_title="Data Analyst",
        description="SQL and Power BI are required.",
        company="Analytics GmbH",
        location="Munich",
        country="Germany",
        source="Company Website",
        source_url="https://example.com/jobs/123",
        posted_date="2026-08-14",
    )

    assert job.company == "Analytics GmbH"
    assert job.location == "Munich"
    assert job.country == "Germany"

    assert job.source == "Company Website"
    assert job.source_url == "https://example.com/jobs/123"
    assert job.posted_date == "2026-08-14"


def test_unknown_job_is_preserved():
    job = parser.parse(
        job_title="Specialist",
        description="""
        General organisational responsibilities
        within the organisation.
        """,
    )

    assert job.job_title == "Specialist"
    assert job.job_family == "Other"
    assert job.industry == "Other"


def test_rejects_completely_empty_job():
    with pytest.raises(ValueError):
        parser.parse(
            job_title="",
            description="",
        )
