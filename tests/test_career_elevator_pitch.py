from career.achievement import AchievementRecord
from career.education import EducationRecord
from career.elevator_pitch import (
    ElevatorPitchRequest,
)
from career.models import CareerProfile
from career.project import ProjectRecord
from career.work_experience import WorkExperience
import services.elevator_pitch_service as pitch_service


def _patch_data(
    monkeypatch,
):
    monkeypatch.setattr(
        pitch_service,
        "load_profile",
        lambda: CareerProfile(
            full_name="Test Candidate",
            professional_summary_en=(
                "I build data solutions."
            ),
            professional_summary_de=(
                "Ich entwickle Datenlösungen."
            ),
            target_roles=[
                "Data Engineer",
            ],
            technical_skills=[
                "Python",
                "SQL",
                "GCP",
                "Spark",
                "BigQuery",
            ],
            verified=True,
        ),
    )

    monkeypatch.setattr(
        pitch_service,
        "get_work_experiences",
        lambda: [
            WorkExperience(
                employer="Example GmbH",
                job_title_en="Data Engineer",
                job_title_de="Data Engineer",
                start_date="2025-01",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        pitch_service,
        "get_education_records",
        lambda: [
            EducationRecord(
                institution="Example University",
                degree_en="Master of Science",
                degree_de="Master of Science",
                field_of_study_en="Data Engineering",
                field_of_study_de="Data Engineering",
                start_date="2023-10",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        pitch_service,
        "get_project_records",
        lambda: [
            ProjectRecord(
                name_en="Cloud Pipeline",
                name_de="Cloud-Datenpipeline",
                start_date="2026-01",
                technologies=[
                    "Python",
                    "GCP",
                ],
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        pitch_service,
        "get_achievement_records",
        lambda: [
            AchievementRecord(
                title_en="Improved processing",
                title_de="Verarbeitung verbessert",
                achievement_date="2026-08",
                metric_value="30%",
                verified=True,
            )
        ],
    )


def test_english_30_second_pitch(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=30,
                audience="Recruiter",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Test Candidate"
        in result.text
    )

    assert (
        "Data Engineer"
        in result.text
    )

    assert (
        "Python"
        in result.text
    )


def test_german_pitch(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="Deutsch",
                duration_seconds=60,
                audience="Hiring Manager",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Hallo, ich bin Test Candidate"
        in result.text
    )

    assert (
        "Ich entwickle Datenlösungen"
        in result.text
    )


def test_60_second_pitch_includes_project(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=60,
                audience="Technical Manager",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Cloud Pipeline"
        in result.text
    )


def test_90_second_pitch_includes_achievement(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=90,
                audience="Hiring Manager",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Improved processing"
        in result.text
    )

    assert (
        "30%"
        in result.text
    )


def test_unverified_experience_is_not_used(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    monkeypatch.setattr(
        pitch_service,
        "get_work_experiences",
        lambda: [
            WorkExperience(
                employer="Hidden GmbH",
                job_title_en="Hidden Role",
                start_date="2025-01",
                verified=False,
            )
        ],
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=60,
                audience="Recruiter",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Hidden GmbH"
        not in result.text
    )

    assert (
        "Hidden Role"
        not in result.text
    )


def test_unverified_profile_creates_warning(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    monkeypatch.setattr(
        pitch_service,
        "load_profile",
        lambda: CareerProfile(
            full_name="Test Candidate",
            target_roles=[
                "Data Engineer",
            ],
            verified=False,
        ),
    )

    result = (
        pitch_service
        .generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=30,
                audience="Recruiter",
                target_role="Data Engineer",
            )
        )
    )

    assert any(
        "not verified"
        in warning.lower()
        for warning in result.warnings
    )


def test_invalid_duration_fails(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    try:
        pitch_service.generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="English",
                duration_seconds=45,
                audience="Recruiter",
                target_role="Data Engineer",
            )
        )

    except ValueError as error:
        assert (
            "30, 60 or 90"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_invalid_language_fails(
    monkeypatch,
):
    _patch_data(
        monkeypatch
    )

    try:
        pitch_service.generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language="French",
                duration_seconds=30,
                audience="Recruiter",
                target_role="Data Engineer",
            )
        )

    except ValueError as error:
        assert (
            "English or Deutsch"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )
