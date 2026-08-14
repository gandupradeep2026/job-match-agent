from career.education import EducationRecord
import career.database as career_database
import career.education_database as education_database


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
        education_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_required_fields():
    record = EducationRecord(
        institution="Example University",
        degree_en="Master of Science",
        start_date="2023-10",
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_missing_institution_fails():
    record = EducationRecord(
        degree_en="Master of Science",
        start_date="2023-10",
    )

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
        education_database
        .save_education_record(
            EducationRecord(
                institution=(
                    "Example University"
                ),
                degree_en=(
                    "Master of Science"
                ),
                degree_de=(
                    "Master of Science"
                ),
                field_of_study_en=(
                    "Data Engineering"
                ),
                field_of_study_de=(
                    "Data Engineering"
                ),
                location="Berlin",
                country="Germany",
                start_date="2023-10",
                end_date="2026-09",
                grade="1.7",
                thesis_title_en=(
                    "Example Thesis"
                ),
                thesis_title_de=(
                    "Beispielarbeit"
                ),
                achievements_en=[
                    "Focused on cloud systems."
                ],
                achievements_de=[
                    "Schwerpunkt Cloud-Systeme."
                ],
                verified=True,
            )
        )
    )

    assert saved.id is not None
    assert (
        saved.institution
        == "Example University"
    )
    assert saved.grade == "1.7"
    assert saved.verified is True


def test_current_study_clears_end_date(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        education_database
        .save_education_record(
            EducationRecord(
                institution=(
                    "Example University"
                ),
                degree_en=(
                    "Master of Science"
                ),
                start_date="2023-10",
                end_date="2026-09",
                is_current=True,
            )
        )
    )

    assert saved.is_current is True
    assert saved.end_date == ""


def test_update_record(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        education_database
        .save_education_record(
            EducationRecord(
                institution=(
                    "Example University"
                ),
                degree_en=(
                    "Bachelor of Science"
                ),
                start_date="2020-10",
            )
        )
    )

    saved.degree_en = (
        "Bachelor of Engineering"
    )

    updated = (
        education_database
        .save_education_record(
            saved
        )
    )

    assert (
        updated.degree_en
        == "Bachelor of Engineering"
    )


def test_list_records(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    education_database.save_education_record(
        EducationRecord(
            institution="University A",
            degree_en="Bachelor",
            start_date="2019-10",
        )
    )

    education_database.save_education_record(
        EducationRecord(
            institution="University B",
            degree_en="Master",
            start_date="2023-10",
            is_current=True,
        )
    )

    records = (
        education_database
        .get_education_records()
    )

    assert len(records) == 2
    assert (
        records[0].institution
        == "University B"
    )


def test_delete_record(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        education_database
        .save_education_record(
            EducationRecord(
                institution=(
                    "Example University"
                ),
                degree_en="Master",
                start_date="2023-10",
            )
        )
    )

    deleted = (
        education_database
        .delete_education_record(
            saved.id
        )
    )

    assert deleted is True
    assert (
        education_database
        .get_education_records()
        == []
    )


def test_duplicate_highlights_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        education_database
        .save_education_record(
            EducationRecord(
                institution=(
                    "Example University"
                ),
                degree_en="Master",
                start_date="2023-10",
                achievements_en=[
                    "Cloud",
                    "cloud",
                    "Data",
                    "Data",
                ],
            )
        )
    )

    assert saved.achievements_en == [
        "Cloud",
        "Data",
    ]
