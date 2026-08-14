from career.project import ProjectRecord
import career.database as career_database
import career.project_database as project_database


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
        project_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_required_fields():
    record = ProjectRecord(
        name_en="Data Platform Project",
        start_date="2026-01",
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_missing_name_fails():
    record = ProjectRecord(
        start_date="2026-01",
    )

    assert (
        record.has_required_fields()
        is False
    )


def test_project_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en=(
                    "Cloud Data Pipeline"
                ),
                name_de=(
                    "Cloud-Datenpipeline"
                ),
                project_type=(
                    "Portfolio Project"
                ),
                role_en=(
                    "Data Engineer"
                ),
                role_de=(
                    "Data Engineer"
                ),
                start_date="2026-01",
                end_date="2026-06",
                description_en=(
                    "Built a cloud data pipeline."
                ),
                description_de=(
                    "Cloud-Datenpipeline entwickelt."
                ),
                responsibilities_en=[
                    "Designed ETL pipeline."
                ],
                achievements_en=[
                    "Automated data processing."
                ],
                technologies=[
                    "Python",
                    "SQL",
                    "GCP",
                ],
                skills=[
                    "Data Engineering",
                    "ETL",
                ],
                repository_url=(
                    "https://github.com/example/project"
                ),
                verified=True,
            )
        )
    )

    assert saved.id is not None
    assert (
        saved.name_en
        == "Cloud Data Pipeline"
    )
    assert saved.verified is True
    assert saved.technologies == [
        "Python",
        "SQL",
        "GCP",
    ]


def test_current_project_clears_end_date(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en="Current Project",
                start_date="2026-01",
                end_date="2026-08",
                is_current=True,
            )
        )
    )

    assert saved.is_current is True
    assert saved.end_date == ""


def test_update_project(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en="Version 1",
                start_date="2026-01",
            )
        )
    )

    saved.name_en = (
        "Version 2"
    )

    updated = (
        project_database
        .save_project_record(
            saved
        )
    )

    assert (
        updated.name_en
        == "Version 2"
    )


def test_list_projects(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    project_database.save_project_record(
        ProjectRecord(
            name_en="Older Project",
            start_date="2025-01",
        )
    )

    project_database.save_project_record(
        ProjectRecord(
            name_en="Current Project",
            start_date="2026-01",
            is_current=True,
        )
    )

    records = (
        project_database
        .get_project_records()
    )

    assert len(records) == 2
    assert (
        records[0].name_en
        == "Current Project"
    )


def test_delete_project(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en="Delete Me",
                start_date="2026-01",
            )
        )
    )

    deleted = (
        project_database
        .delete_project_record(
            saved.id
        )
    )

    assert deleted is True
    assert (
        project_database
        .get_project_records()
        == []
    )


def test_duplicate_technologies_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en="Test Project",
                start_date="2026-01",
                technologies=[
                    "Python",
                    "python",
                    "SQL",
                    "SQL",
                ],
            )
        )
    )

    assert saved.technologies == [
        "Python",
        "SQL",
    ]


def test_duplicate_skills_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        project_database
        .save_project_record(
            ProjectRecord(
                name_en="Test Project",
                start_date="2026-01",
                skills=[
                    "ETL",
                    "etl",
                    "Cloud",
                    "Cloud",
                ],
            )
        )
    )

    assert saved.skills == [
        "ETL",
        "Cloud",
    ]
