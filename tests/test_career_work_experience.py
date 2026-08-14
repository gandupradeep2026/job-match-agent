from career.work_experience import WorkExperience
import career.database as career_database
import career.work_experience_database as experience_database


def _use_temp_database(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "career_profile.db"

    monkeypatch.setattr(
        career_database,
        "DATABASE_PATH",
        database_path,
    )

    monkeypatch.setattr(
        experience_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_required_fields():
    experience = WorkExperience(
        employer="Example GmbH",
        job_title_en="Data Engineer",
        start_date="2025-01",
    )

    assert experience.has_required_fields() is True


def test_missing_employer_fails_required_fields():
    experience = WorkExperience(
        job_title_en="Data Engineer",
        start_date="2025-01",
    )

    assert experience.has_required_fields() is False


def test_work_experience_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = experience_database.save_work_experience(
        WorkExperience(
            employer="Example GmbH",
            job_title_en="Data Engineer",
            job_title_de="Data Engineer",
            location="Berlin",
            country="Germany",
            start_date="2025-01",
            end_date="2026-01",
            employment_type="Full-time",
            description_en="Built data pipelines.",
            description_de="Datenpipelines entwickelt.",
            achievements_en=[
                "Reduced processing time by 30%."
            ],
            achievements_de=[
                "Verarbeitungszeit um 30 % reduziert."
            ],
            technologies=[
                "Python",
                "SQL",
                "GCP",
            ],
            verified=True,
        )
    )

    assert saved.id is not None
    assert saved.employer == "Example GmbH"
    assert saved.verified is True
    assert saved.technologies == [
        "Python",
        "SQL",
        "GCP",
    ]


def test_current_role_clears_end_date(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = experience_database.save_work_experience(
        WorkExperience(
            employer="Example GmbH",
            job_title_en="Data Engineer",
            start_date="2025-01",
            end_date="2026-01",
            is_current=True,
        )
    )

    assert saved.is_current is True
    assert saved.end_date == ""


def test_update_work_experience(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = experience_database.save_work_experience(
        WorkExperience(
            employer="Example GmbH",
            job_title_en="Junior Data Engineer",
            start_date="2025-01",
        )
    )

    saved.job_title_en = "Data Engineer"

    updated = experience_database.save_work_experience(
        saved
    )

    assert updated.job_title_en == "Data Engineer"


def test_list_work_experiences(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    experience_database.save_work_experience(
        WorkExperience(
            employer="Company A",
            job_title_en="Data Engineer",
            start_date="2024-01",
        )
    )

    experience_database.save_work_experience(
        WorkExperience(
            employer="Company B",
            job_title_en="Cloud Data Engineer",
            start_date="2025-01",
            is_current=True,
        )
    )

    records = (
        experience_database.get_work_experiences()
    )

    assert len(records) == 2
    assert records[0].employer == "Company B"


def test_delete_work_experience(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = experience_database.save_work_experience(
        WorkExperience(
            employer="Example GmbH",
            job_title_en="Data Engineer",
            start_date="2025-01",
        )
    )

    deleted = experience_database.delete_work_experience(
        saved.id
    )

    assert deleted is True
    assert experience_database.get_work_experiences() == []


def test_duplicate_technologies_are_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = experience_database.save_work_experience(
        WorkExperience(
            employer="Example GmbH",
            job_title_en="Data Engineer",
            start_date="2025-01",
            technologies=[
                "Python",
                "python",
                "SQL",
                "SQL",
            ],
        )
    )

    assert saved.technologies == [
        "Python",
        "SQL",
    ]
