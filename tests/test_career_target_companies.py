from career.target_company import TargetCompany
import career.database as career_database
import career.target_company_database as company_database


def _use_temp_database(
    tmp_path,
    monkeypatch,
):
    database_path = (
        tmp_path
        / "career_profile.db"
    )

    monkeypatch.setattr(
        career_database,
        "DATABASE_PATH",
        database_path,
    )

    monkeypatch.setattr(
        company_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_required_fields():
    record = TargetCompany(
        company_name="Example GmbH"
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_missing_company_name_fails():
    record = TargetCompany()

    assert (
        record.has_required_fields()
        is False
    )


def test_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Example GmbH"
                ),
                priority=(
                    "A — Dream Company"
                ),
                status=(
                    "Ready to Apply"
                ),
                industry=(
                    "Cloud Technology"
                ),
                headquarters="Berlin",
                germany_locations=[
                    "Berlin",
                    "Munich",
                ],
                target_roles=[
                    "Data Engineer",
                    "Cloud Data Engineer",
                ],
                technologies=[
                    "GCP",
                    "BigQuery",
                ],
                why_company_en=(
                    "Strong cloud platform."
                ),
                why_company_de=(
                    "Starke Cloud-Plattform."
                ),
                last_researched_date=(
                    "2026-08-14"
                ),
            )
        )
    )

    assert saved.id is not None
    assert (
        saved.company_name
        == "Example GmbH"
    )
    assert saved.germany_locations == [
        "Berlin",
        "Munich",
    ]


def test_update_company(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Example GmbH"
                )
            )
        )
    )

    saved.status = (
        "Interviewing"
    )

    updated = (
        company_database
        .save_target_company(
            saved
        )
    )

    assert (
        updated.status
        == "Interviewing"
    )


def test_priority_order(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    company_database.save_target_company(
        TargetCompany(
            company_name="Company C",
            priority=(
                "C — Secondary Target"
            ),
        )
    )

    company_database.save_target_company(
        TargetCompany(
            company_name="Company A",
            priority=(
                "A — Dream Company"
            ),
        )
    )

    company_database.save_target_company(
        TargetCompany(
            company_name="Company B",
            priority=(
                "B — Strong Target"
            ),
        )
    )

    records = (
        company_database
        .get_target_companies()
    )

    assert [
        item.company_name
        for item in records
    ] == [
        "Company A",
        "Company B",
        "Company C",
    ]


def test_delete_company(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Delete GmbH"
                )
            )
        )
    )

    deleted = (
        company_database
        .delete_target_company(
            saved.id
        )
    )

    assert deleted is True
    assert (
        company_database
        .get_target_companies()
        == []
    )


def test_duplicate_roles_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Example GmbH"
                ),
                target_roles=[
                    "Data Engineer",
                    "data engineer",
                    "Cloud Engineer",
                    "Cloud Engineer",
                ],
            )
        )
    )

    assert saved.target_roles == [
        "Data Engineer",
        "Cloud Engineer",
    ]


def test_duplicate_technologies_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Example GmbH"
                ),
                technologies=[
                    "GCP",
                    "gcp",
                    "Python",
                    "Python",
                ],
            )
        )
    )

    assert saved.technologies == [
        "GCP",
        "Python",
    ]


def test_german_notes_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        company_database
        .save_target_company(
            TargetCompany(
                company_name=(
                    "Example GmbH"
                ),
                why_company_de=(
                    "Interessantes Unternehmen."
                ),
                why_fit_de=(
                    "Passende Erfahrung."
                ),
                next_action_de=(
                    "Karriereseite prüfen."
                ),
            )
        )
    )

    assert (
        saved.why_company_de
        == "Interessantes Unternehmen."
    )

    assert (
        saved.next_action_de
        == "Karriereseite prüfen."
    )
