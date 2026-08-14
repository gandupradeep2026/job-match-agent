from career.achievement import AchievementRecord
from career.education import EducationRecord
from career.master_cv import build_master_cv_data
from career.models import CareerProfile
from career.project import ProjectRecord
from career.work_experience import WorkExperience
from services.master_cv_service import (
    build_master_cv_text,
)


def _profile(
    *,
    verified: bool = True,
) -> CareerProfile:
    return CareerProfile(
        full_name="Test Candidate",
        email="test@example.com",
        city="Berlin",
        country="Germany",
        professional_summary_en=(
            "English professional summary."
        ),
        professional_summary_de=(
            "Deutsches berufliches Profil."
        ),
        target_roles=[
            "Data Engineer",
        ],
        technical_skills=[
            "Python",
            "SQL",
        ],
        languages=[
            "English",
            "German",
        ],
        certifications=[
            "Example Certificate",
        ],
        verified=verified,
    )


def test_english_master_cv_uses_english_fields():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[
            WorkExperience(
                employer="Example GmbH",
                job_title_en="Data Engineer",
                job_title_de="Dateningenieur",
                start_date="2025-01",
                verified=True,
            )
        ],
        education_records=[],
        projects=[],
        achievements=[],
        language="English",
    )

    assert (
        data.professional_summary
        == "English professional summary."
    )

    assert (
        "Data Engineer"
        in data.experiences[0]
    )


def test_german_master_cv_uses_german_fields():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[
            WorkExperience(
                employer="Example GmbH",
                job_title_en="Data Engineer",
                job_title_de="Dateningenieur",
                start_date="2025-01",
                verified=True,
            )
        ],
        education_records=[],
        projects=[],
        achievements=[],
        language="Deutsch",
    )

    assert (
        data.professional_summary
        == "Deutsches berufliches Profil."
    )

    assert (
        "Dateningenieur"
        in data.experiences[0]
    )


def test_unverified_experience_is_excluded():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[
            WorkExperience(
                employer="Hidden GmbH",
                job_title_en="Data Engineer",
                start_date="2025-01",
                verified=False,
            )
        ],
        education_records=[],
        projects=[],
        achievements=[],
        language="English",
    )

    assert data.experiences == []


def test_unverified_project_is_excluded():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[],
        education_records=[],
        projects=[
            ProjectRecord(
                name_en="Unverified Project",
                start_date="2026-01",
                verified=False,
            )
        ],
        achievements=[],
        language="English",
    )

    assert data.projects == []


def test_verified_project_is_included():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[],
        education_records=[],
        projects=[
            ProjectRecord(
                name_en="Verified Project",
                name_de="Verifiziertes Projekt",
                start_date="2026-01",
                verified=True,
            )
        ],
        achievements=[],
        language="English",
    )

    assert (
        "Verified Project"
        in data.projects[0]
    )


def test_verified_education_is_included():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[],
        education_records=[
            EducationRecord(
                institution="Example University",
                degree_en="Master of Science",
                degree_de="Master of Science",
                start_date="2023-10",
                verified=True,
            )
        ],
        projects=[],
        achievements=[],
        language="English",
    )

    assert (
        "Example University"
        in data.education[0]
    )


def test_verified_achievement_is_included():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[],
        education_records=[],
        projects=[],
        achievements=[
            AchievementRecord(
                title_en="Improved Performance",
                title_de="Leistung verbessert",
                achievement_date="2026-08",
                metric_value="30%",
                verified=True,
            )
        ],
        language="English",
    )

    assert (
        "Improved Performance"
        in data.achievements[0]
    )

    assert (
        "30%"
        in data.achievements[0]
    )


def test_unverified_profile_creates_warning():
    data = build_master_cv_data(
        profile=_profile(
            verified=False
        ),
        experiences=[],
        education_records=[],
        projects=[],
        achievements=[],
        language="English",
    )

    assert any(
        "not verified"
        in warning.lower()
        for warning in data.warnings
    )


def test_master_cv_text_contains_sections():
    data = build_master_cv_data(
        profile=_profile(),
        experiences=[
            WorkExperience(
                employer="Example GmbH",
                job_title_en="Data Engineer",
                start_date="2025-01",
                verified=True,
            )
        ],
        education_records=[],
        projects=[],
        achievements=[],
        language="English",
    )

    text = build_master_cv_text(
        data
    )

    assert (
        "PROFESSIONAL"
        not in text
    )

    assert (
        "Professional Summary"
        in text
    )

    assert (
        "Technical Skills"
        in text
    )

    assert (
        "Professional Experience"
        in text
    )
