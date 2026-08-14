from career.interview_preparation import (
    BehavioralAnswer,
    InterviewPreparationPack,
    InterviewPreparationRequest,
    PreparedAnswer,
)
from career.elevator_pitch import (
    ElevatorPitchResult,
)
from career.target_company import (
    TargetCompany,
)
import services.interview_pack_service as service


def _prep_pack(
    language: str,
) -> InterviewPreparationPack:
    return InterviewPreparationPack(
        language=language,
        target_role="Data Engineer",
        company_name="Example GmbH",
        tell_me_about_yourself=PreparedAnswer(
            question="Tell me about yourself.",
            answer="Prepared introduction.",
        ),
        why_this_role=PreparedAnswer(
            question="Why this role?",
            answer="Because it matches my skills.",
        ),
        why_this_company=PreparedAnswer(
            question="Why this company?",
            answer="Because of the cloud focus.",
        ),
        strengths=PreparedAnswer(
            question="Strengths?",
            answer="Python and problem solving.",
        ),
        weakness=PreparedAnswer(
            question="Development area?",
            answer="Public speaking.",
        ),
        behavioral_answers=[
            BehavioralAnswer(
                category="Problem Solving",
                story_title="Solved Pipeline",
                question="Tell me about a problem.",
                answer="Situation: S\nTask: T\nAction: A\nResult: R",
            )
        ],
        technical_focus=[
            "Python",
            "SQL",
            "GCP",
        ],
        warnings=[],
    )


def _patch_dependencies(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "generate_interview_preparation_pack",
        lambda request: _prep_pack(
            request.language
        ),
    )

    monkeypatch.setattr(
        service,
        "generate_personal_elevator_pitch",
        lambda request: ElevatorPitchResult(
            language=request.language,
            duration_seconds=(
                request.duration_seconds
            ),
            audience=request.audience,
            target_role=request.target_role,
            text=(
                f"Pitch {request.duration_seconds}"
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
            technologies=[
                "BigQuery",
                "Spark",
            ],
        ),
    )


def test_complete_pack_contains_three_pitches(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert (
        pack.elevator_pitch_30
        == "Pitch 30"
    )

    assert (
        pack.elevator_pitch_60
        == "Pitch 60"
    )

    assert (
        pack.elevator_pitch_90
        == "Pitch 90"
    )


def test_complete_pack_reuses_core_answers(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
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
        pack.why_this_company.answer
        == "Because of the cloud focus."
    )


def test_employer_questions_are_generated(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert (
        len(
            pack.employer_questions
        )
        >= 5
    )

    assert any(
        "Example GmbH"
        in question
        for question in (
            pack.employer_questions
        )
    )


def test_company_technologies_can_appear_in_questions(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert any(
        (
            "BigQuery"
            in question
            or "Spark"
            in question
        )
        for question in (
            pack.employer_questions
        )
    )


def test_text_export_contains_major_sections(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    text = (
        service
        .build_complete_interview_pack_text(
            pack
        )
    )

    assert (
        "COMPLETE INTERVIEW PACK"
        in text
    )

    assert (
        "BEHAVIORAL / STAR ANSWERS"
        in text
    )

    assert (
        "QUESTIONS TO ASK THE EMPLOYER"
        in text
    )


def test_docx_export_returns_bytes(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    result = (
        service
        .build_complete_interview_pack_docx(
            pack
        )
    )

    assert isinstance(
        result,
        bytes,
    )

    assert len(
        result
    ) > 100


def test_german_pack(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="Deutsch",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    text = (
        service
        .build_complete_interview_pack_text(
            pack
        )
    )

    assert (
        "KOMPLETTES INTERVIEW-PAKET"
        in text
    )

    assert (
        "FRAGEN AN DEN ARBEITGEBER"
        in text
    )


def test_checklist_is_included(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    pack = (
        service
        .create_complete_interview_pack(
            InterviewPreparationRequest(
                language="English",
                target_role="Data Engineer",
                company_id=1,
            )
        )
    )

    assert (
        len(
            pack.preparation_checklist
        )
        >= 6
    )


def test_invalid_language_fails(
    monkeypatch,
):
    _patch_dependencies(
        monkeypatch
    )

    try:
        service.create_complete_interview_pack(
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
