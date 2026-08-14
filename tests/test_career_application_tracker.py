from career.application_tracker_link import (
    CareerApplicationLink,
)
from career.target_company import (
    TargetCompany,
)
import career.application_tracker_service as service
import services.job_tracker as job_tracker


def _use_temp_db(
    tmp_path,
    monkeypatch,
):
    database_path = (
        tmp_path
        / "applications.db"
    )

    monkeypatch.setattr(
        job_tracker,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def _create_application():
    job_tracker.create_applications_table()

    return job_tracker.save_application(
        company="Example GmbH",
        job_title="Data Engineer",
        location="Berlin",
        application_date="2026-08-14",
        status="Applied",
        job_url="https://example.com/job",
        contact_name="",
        contact_email="",
        contact_phone="",
        skill_match_score=80.0,
        ats_score=75.0,
        overall_match_score=78.0,
        notes="",
    )


def test_career_columns_are_added(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    job_tracker.create_applications_table()

    service.ensure_career_application_columns()

    connection = (
        job_tracker.get_connection()
    )

    try:
        columns = (
            job_tracker.get_existing_columns(
                connection
            )
        )
    finally:
        connection.close()

    assert (
        "target_company_id"
        in columns
    )

    assert (
        "interview_pack_ready"
        in columns
    )


def test_link_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    application_id = (
        _create_application()
    )

    monkeypatch.setattr(
        service,
        "get_target_company",
        lambda company_id: TargetCompany(
            id=company_id,
            company_name="Example GmbH",
        ),
    )

    saved = (
        service
        .save_career_application_link(
            CareerApplicationLink(
                application_id=(
                    application_id
                ),
                target_company_id=1,
                career_target_role=(
                    "Data Engineer"
                ),
                preparation_stage=(
                    "Interview Prep"
                ),
                tailored_cv_ready=True,
                interview_pack_ready=True,
                interview_pack_language=(
                    "Both / Beide"
                ),
                career_next_action=(
                    "Practice STAR stories."
                ),
            )
        )
    )

    assert (
        saved.target_company_id
        == 1
    )

    assert (
        saved.tailored_cv_ready
        is True
    )

    assert (
        saved.interview_pack_ready
        is True
    )


def test_interview_ready_logic():
    link = CareerApplicationLink(
        application_id=1,
        preparation_stage=(
            "Interview Ready"
        ),
        interview_pack_ready=True,
    )

    assert (
        link.is_interview_ready()
        is True
    )


def test_invalid_stage_fails(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    application_id = (
        _create_application()
    )

    try:
        service.save_career_application_link(
            CareerApplicationLink(
                application_id=(
                    application_id
                ),
                preparation_stage=(
                    "Unknown Stage"
                ),
            )
        )

    except ValueError as error:
        assert (
            "Invalid preparation stage"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_invalid_company_fails(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    application_id = (
        _create_application()
    )

    monkeypatch.setattr(
        service,
        "get_target_company",
        lambda company_id: None,
    )

    try:
        service.save_career_application_link(
            CareerApplicationLink(
                application_id=(
                    application_id
                ),
                target_company_id=999,
            )
        )

    except ValueError as error:
        assert (
            "Target company does not exist"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_exact_company_match_suggestion():
    application = {
        "company": "Example GmbH",
    }

    companies = [
        TargetCompany(
            id=4,
            company_name=(
                "Example GmbH"
            ),
        ),
        TargetCompany(
            id=5,
            company_name=(
                "Other GmbH"
            ),
        ),
    ]

    result = (
        service
        .suggest_target_company_id(
            application,
            companies,
        )
    )

    assert result == 4


def test_non_exact_company_match_not_suggested():
    application = {
        "company": "Example",
    }

    companies = [
        TargetCompany(
            id=4,
            company_name=(
                "Example GmbH"
            ),
        ),
    ]

    result = (
        service
        .suggest_target_company_id(
            application,
            companies,
        )
    )

    assert result is None


def test_overview_contains_career_fields(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    application_id = (
        _create_application()
    )

    monkeypatch.setattr(
        service,
        "get_target_company",
        lambda company_id: None,
    )

    service.save_career_application_link(
        CareerApplicationLink(
            application_id=(
                application_id
            ),
            career_target_role=(
                "Data Engineer"
            ),
            preparation_stage=(
                "CV Ready"
            ),
            tailored_cv_ready=True,
        )
    )

    overview = (
        service
        .get_career_application_overview()
    )

    assert len(
        overview
    ) == 1

    assert (
        overview[0][
            "preparation_stage"
        ]
        == "CV Ready"
    )

    assert (
        overview[0][
            "tailored_cv_ready"
        ]
        is True
    )


def test_missing_application_returns_none(
    tmp_path,
    monkeypatch,
):
    _use_temp_db(
        tmp_path,
        monkeypatch,
    )

    job_tracker.create_applications_table()

    result = (
        service
        .get_career_application_link(
            999
        )
    )

    assert result is None
