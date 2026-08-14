from career.elevator_pitch import ElevatorPitchResult
from career.interview_preparation import (
    InterviewPreparationRequest,
)
from career.models import CareerProfile
from career.project import ProjectRecord
from career.star_story import StarStory
from career.target_company import TargetCompany
import services.interview_preparation_service as service


def _patch_base(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "load_profile",
        lambda: CareerProfile(
            full_name="Test Candidate",
            target_roles=[
                "Data Engineer",
            ],
            technical_skills=[
                "Python",
                "SQL",
                "GCP",
            ],
            verified=True,
        ),
    )

    monkeypatch.setattr(
        service,
        "get_work_experiences",
        lambda: [],
    )

    monkeypatch.setattr(
        service,
        "get_education_records",
        lambda: [],
    )

    monkeypatch.setattr(
        service,
        "get_achievement_records",
        lambda: [],
    )

    monkeypatch.setattr(
        service,
        "get_project_records",
        lambda: [
            ProjectRecord(
                name_en="Cloud Pipeline",
                name_de="Cloud-Datenpipeline",
                start_date="2026-01",
                technologies=[
                    "Spark",
                    "BigQuery",
                ],
                skills=[
                    "ETL",
                ],
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_star_stories",
        lambda: [
            StarStory(
                title_en="Solved a pipeline issue",
                title_de="Pipeline-Problem gelöst",
                category="Problem Solving",
                situation_en="The pipeline failed.",
                task_en="Restore processing.",
                action_en="I diagnosed and fixed the issue.",
                result_en="Processing resumed.",
                situation_de="Die Pipeline fiel aus.",
                task_de="Die Verarbeitung wiederherstellen.",
                action_de="Ich analysierte und behob den Fehler.",
                result_de="Die Verarbeitung lief wieder.",
                competencies=[
                    "Problem Solving",
                ],
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "generate_personal_elevator_pitch",
        lambda request: ElevatorPitchResult(
            language=request.language,
            duration_seconds=60,
            audience="Hiring Manager",
            target_role=request.target_role,
            text=(
                "Prepared introduction."
                if request.language == "English"
                else "Vorbereitete Vorstellung."
            ),
            warnings=[],
            evidence_count=3,
        ),
    )

    monkeypatch.setattr(
        service,
        "get_target_company",
        lambda company_id: TargetCompany(
            id=company_id,
            company_name="Example GmbH",
            why_company_en=(
                "I value the company's cloud focus."
            ),
            why_company_de=(
                "Ich schätze den Cloud-Fokus des Unternehmens."
            ),
            why_fit_en=(
                "My verified skills align with the role."
            ),
            why_fit_de=(
                "Meine verifizierten Kenntnisse passen zur Position."
            ),
        ),
    )


def test_english_pack(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert (
        pack.tell_me_about_yourself.answer
        == "Prepared introduction."
    )

    assert (
        "Python"
        in pack.why_this_role.answer
    )

    assert (
        pack.company_name
        == "Example GmbH"
    )


def test_german_pack(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="Deutsch",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert (
        pack.tell_me_about_yourself.answer
        == "Vorbereitete Vorstellung."
    )

    assert (
        "Cloud-Fokus"
        in pack.why_this_company.answer
    )


def test_why_company_requires_company(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=None,
            )
        )
    )

    assert (
        pack.why_this_company.answer
        == ""
    )

    assert (
        pack.why_this_company.warnings
    )


def test_weakness_requires_user_input(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        pack.weakness.answer
        == ""
    )

    assert (
        "will not invent"
        in pack.weakness.warnings[0]
    )


def test_weakness_uses_only_user_input(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                development_area=(
                    "public speaking"
                ),
                improvement_action=(
                    "I practice short technical presentations"
                ),
                improvement_evidence=(
                    "I now present more confidently"
                ),
            )
        )
    )

    assert (
        "public speaking"
        in pack.weakness.answer
    )

    assert (
        "practice short technical presentations"
        in pack.weakness.answer
    )


def test_behavioral_answer_uses_verified_star_story(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
            )
        )
    )

    assert len(
        pack.behavioral_answers
    ) == 1

    assert (
        "The pipeline failed"
        in pack.behavioral_answers[0].answer
    )


def test_unverified_star_story_is_excluded(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    monkeypatch.setattr(
        service,
        "get_star_stories",
        lambda: [
            StarStory(
                title_en="Hidden Story",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
                verified=False,
            )
        ],
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        pack.behavioral_answers
        == []
    )


def test_technical_focus_combines_profile_and_project(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
            )
        )
    )

    assert (
        "Python"
        in pack.technical_focus
    )

    assert (
        "Spark"
        in pack.technical_focus
    )

    assert (
        "ETL"
        in pack.technical_focus
    )


def test_unverified_profile_creates_warning(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    monkeypatch.setattr(
        service,
        "load_profile",
        lambda: CareerProfile(
            target_roles=[
                "Data Engineer",
            ],
            verified=False,
        ),
    )

    pack = (
        service
        .generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
            )
        )
    )

    assert any(
        "not verified"
        in warning.lower()
        for warning in pack.warnings
    )


def test_invalid_language_fails(
    monkeypatch,
):
    _patch_base(
        monkeypatch
    )

    try:
        service.generate_interview_preparation_pack(
            InterviewPreparationRequest(
                language="French",
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
