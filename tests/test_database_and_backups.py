from pathlib import Path

import pytest

import services.backup_service as backup_service
import services.job_tracker as job_tracker


@pytest.fixture()
def temporary_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """
    Redirect tracker and backup operations to a temporary folder.
    """

    test_database_path = (
        tmp_path
        / "database"
        / "applications.db"
    )

    test_backup_directory = (
        tmp_path
        / "backups"
    )

    monkeypatch.setattr(
        job_tracker,
        "DATABASE_PATH",
        test_database_path,
    )

    monkeypatch.setattr(
        backup_service,
        "DATABASE_PATH",
        test_database_path,
    )

    monkeypatch.setattr(
        backup_service,
        "BACKUP_DIRECTORY",
        test_backup_directory,
    )

    job_tracker.create_applications_table()

    return test_database_path


def save_sample_application(
    company: str = "TechNova GmbH",
    job_title: str = "IT Support Specialist",
    location: str = "Berlin",
    job_url: str = "https://example.com/jobs/123",
) -> int:
    """
    Insert one sample application into the temporary database.
    """

    return job_tracker.save_application(
        company=company,
        job_title=job_title,
        location=location,
        application_date="2026-08-06",
        status="Applied",
        job_url=job_url,
        contact_name="Anna Becker",
        contact_email="anna.becker@example.com",
        contact_phone="+49 30 123456",
        skill_match_score=78.0,
        ats_score=84.0,
        overall_match_score=81.0,
        notes="Sample test application.",
        last_follow_up_date="",
        next_follow_up_date="2026-08-13",
        application_source="Company Website",
        cv_version="CV_IT_v1",
        cover_letter_version="CoverLetter_TechNova_v1",
    )


def test_create_applications_table(
    temporary_database: Path,
) -> None:
    assert temporary_database.exists()

    applications = (
        job_tracker.get_all_applications()
    )

    assert applications == []


def test_save_and_read_application(
    temporary_database: Path,
) -> None:
    application_id = (
        save_sample_application()
    )

    assert application_id > 0

    application = (
        job_tracker.get_application_by_id(
            application_id
        )
    )

    assert application is not None
    assert application["company"] == "TechNova GmbH"
    assert application["job_title"] == (
        "IT Support Specialist"
    )
    assert application["status"] == "Applied"
    assert application["overall_match_score"] == 81.0


def test_get_all_applications_returns_newest_first(
    temporary_database: Path,
) -> None:
    first_id = save_sample_application(
        company="First GmbH",
        job_title="First Role",
        job_url="https://example.com/jobs/first",
    )

    second_id = save_sample_application(
        company="Second GmbH",
        job_title="Second Role",
        job_url="https://example.com/jobs/second",
    )

    applications = (
        job_tracker.get_all_applications()
    )

    assert len(applications) == 2
    assert applications[0]["id"] == second_id
    assert applications[1]["id"] == first_id


def test_update_application(
    temporary_database: Path,
) -> None:
    application_id = (
        save_sample_application()
    )

    updated = job_tracker.update_application(
        application_id=application_id,
        company="TechNova GmbH",
        job_title="Senior IT Support Specialist",
        location="Hamburg",
        application_date="2026-08-07",
        status="Interview",
        job_url="https://example.com/jobs/123",
        contact_name="Anna Becker",
        contact_email="anna.becker@example.com",
        contact_phone="+49 40 123456",
        notes="Interview scheduled.",
        last_follow_up_date="2026-08-08",
        next_follow_up_date="2026-08-15",
        application_source="LinkedIn",
        cv_version="CV_IT_v2",
        cover_letter_version="CoverLetter_TechNova_v2",
    )

    assert updated is True

    application = (
        job_tracker.get_application_by_id(
            application_id
        )
    )

    assert application is not None
    assert application["job_title"] == (
        "Senior IT Support Specialist"
    )
    assert application["location"] == "Hamburg"
    assert application["status"] == "Interview"
    assert application["cv_version"] == "CV_IT_v2"


def test_delete_application(
    temporary_database: Path,
) -> None:
    application_id = (
        save_sample_application()
    )

    deleted = job_tracker.delete_application(
        application_id
    )

    assert deleted is True

    application = (
        job_tracker.get_application_by_id(
            application_id
        )
    )

    assert application is None


def test_find_possible_duplicate_by_url(
    temporary_database: Path,
) -> None:
    save_sample_application()

    duplicates = (
        job_tracker.find_possible_duplicates(
            company="Another Company",
            job_title="Different Role",
            location="Munich",
            job_url="https://www.example.com/jobs/123?utm_source=test",
        )
    )

    assert len(duplicates) == 1
    assert duplicates[0]["confidence"] == "high"
    assert "Same job URL" in duplicates[0][
        "reasons"
    ]


def test_find_possible_duplicate_by_details(
    temporary_database: Path,
) -> None:
    save_sample_application(
        job_url="",
    )

    duplicates = (
        job_tracker.find_possible_duplicates(
            company="technova gmbh",
            job_title="IT Support Specialist",
            location="Berlin",
            job_url="",
        )
    )

    assert len(duplicates) == 1
    assert duplicates[0]["confidence"] == "high"


def test_create_and_validate_backup(
    temporary_database: Path,
) -> None:
    save_sample_application()

    result = (
        backup_service.create_database_backup()
    )

    backup_path = result["path"]

    assert result["success"] is True
    assert backup_path.exists()
    assert result["application_count"] == 1

    validation = (
        backup_service.validate_sqlite_database(
            backup_path
        )
    )

    assert validation["valid"] is True
    assert validation["integrity_status"] == "ok"
    assert validation["application_count"] == 1


def test_list_local_backups(
    temporary_database: Path,
) -> None:
    save_sample_application()

    backup_service.create_database_backup()

    backups = (
        backup_service.list_local_backups()
    )

    assert len(backups) == 1
    assert backups[0]["valid"] is True
    assert backups[0]["application_count"] == 1


def test_restore_database_from_backup(
    temporary_database: Path,
) -> None:
    original_id = save_sample_application(
        company="Original GmbH",
        job_title="Original Role",
    )

    backup_result = (
        backup_service.create_database_backup()
    )

    job_tracker.delete_application(
        original_id
    )

    assert (
        job_tracker.get_all_applications()
        == []
    )

    restore_result = (
        backup_service.restore_database_from_backup(
            backup_result["path"]
        )
    )

    applications = (
        job_tracker.get_all_applications()
    )

    assert restore_result["success"] is True
    assert restore_result["application_count"] == 1
    assert len(applications) == 1
    assert applications[0]["company"] == (
        "Original GmbH"
    )


def test_restore_creates_safety_backup(
    temporary_database: Path,
) -> None:
    save_sample_application(
        company="Before Restore GmbH",
        job_title="Existing Role",
    )

    source_backup = (
        backup_service.create_database_backup(
            prefix="source"
        )
    )

    save_sample_application(
        company="New Record GmbH",
        job_title="New Role",
        job_url="https://example.com/jobs/new",
    )

    restore_result = (
        backup_service.restore_database_from_backup(
            source_backup["path"]
        )
    )

    safety_backup_path = Path(
        restore_result[
            "safety_backup_path"
        ]
    )

    assert safety_backup_path.exists()

    safety_validation = (
        backup_service.validate_sqlite_database(
            safety_backup_path
        )
    )

    assert (
        safety_validation[
            "application_count"
        ]
        == 2
    )


def test_invalid_backup_is_rejected(
    temporary_database: Path,
    tmp_path: Path,
) -> None:
    invalid_file = (
        tmp_path
        / "invalid.db"
    )

    invalid_file.write_text(
        "This is not a SQLite database.",
        encoding="utf-8",
    )

    with pytest.raises(
        backup_service.BackupError
    ):
        backup_service.validate_sqlite_database(
            invalid_file
        )


def test_delete_local_backup(
    temporary_database: Path,
) -> None:
    save_sample_application()

    backup_result = (
        backup_service.create_database_backup()
    )

    deleted = (
        backup_service.delete_local_backup(
            backup_result["path"]
        )
    )

    assert deleted is True
    assert not backup_result["path"].exists()