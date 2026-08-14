from career.achievement import AchievementRecord
import career.database as career_database
import career.achievement_database as achievement_database


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
        achievement_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_required_fields():
    record = AchievementRecord(
        title_en="Improved pipeline performance",
        achievement_date="2026-08",
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_missing_title_fails():
    record = AchievementRecord(
        achievement_date="2026-08",
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
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_en=(
                    "Reduced processing time"
                ),
                title_de=(
                    "Verarbeitungszeit reduziert"
                ),
                category=(
                    "Process Improvement"
                ),
                source_type=(
                    "Project"
                ),
                source_name=(
                    "Cloud Pipeline"
                ),
                achievement_date=(
                    "2026-08"
                ),
                description_en=(
                    "Optimized the ETL workflow."
                ),
                result_en=(
                    "Processing completed faster."
                ),
                metric_value=(
                    "30% faster"
                ),
                competencies=[
                    "Problem Solving",
                    "Optimization",
                ],
                technologies=[
                    "Python",
                    "SQL",
                ],
                verified=True,
            )
        )
    )

    assert saved.id is not None
    assert (
        saved.metric_value
        == "30% faster"
    )
    assert saved.verified is True


def test_update_record(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_en="Initial Result",
                achievement_date="2026-08",
            )
        )
    )

    saved.metric_value = (
        "25% improvement"
    )

    updated = (
        achievement_database
        .save_achievement_record(
            saved
        )
    )

    assert (
        updated.metric_value
        == "25% improvement"
    )


def test_list_records_orders_newest_first(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    achievement_database.save_achievement_record(
        AchievementRecord(
            title_en="Older",
            achievement_date="2025-01",
        )
    )

    achievement_database.save_achievement_record(
        AchievementRecord(
            title_en="Newer",
            achievement_date="2026-08",
        )
    )

    records = (
        achievement_database
        .get_achievement_records()
    )

    assert len(records) == 2
    assert (
        records[0].title_en
        == "Newer"
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
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_en="Delete Me",
                achievement_date="2026-08",
            )
        )
    )

    deleted = (
        achievement_database
        .delete_achievement_record(
            saved.id
        )
    )

    assert deleted is True
    assert (
        achievement_database
        .get_achievement_records()
        == []
    )


def test_duplicate_competencies_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_en="Test",
                achievement_date="2026-08",
                competencies=[
                    "Leadership",
                    "leadership",
                    "Communication",
                    "Communication",
                ],
            )
        )
    )

    assert saved.competencies == [
        "Leadership",
        "Communication",
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
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_en="Test",
                achievement_date="2026-08",
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


def test_german_title_is_sufficient(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        achievement_database
        .save_achievement_record(
            AchievementRecord(
                title_de="Automatisierung umgesetzt",
                achievement_date="2026-08",
            )
        )
    )

    assert (
        saved.has_required_fields()
        is True
    )
