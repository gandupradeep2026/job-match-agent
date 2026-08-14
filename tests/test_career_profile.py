from career.models import CareerProfile
import career.database as career_database


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

    return database_path


def test_empty_profile_defaults():
    profile = CareerProfile()

    assert profile.full_name == ""
    assert profile.target_roles == []
    assert profile.technical_skills == []
    assert profile.verified is False


def test_profile_identity_validation():
    profile = CareerProfile(
        full_name="Test Candidate",
        email="candidate@example.com",
    )

    assert (
        profile.has_basic_identity()
        is True
    )


def test_profile_round_trip(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    profile = CareerProfile(
        full_name="Test Candidate",
        email="candidate@example.com",
        phone="+49 123 456789",

        city="Chemnitz",
        country="Germany",

        professional_summary_en=(
            "Data engineering candidate."
        ),

        professional_summary_de=(
            "Kandidat im Bereich Data Engineering."
        ),

        target_roles=[
            "Data Engineer",
            "Cloud Data Engineer",
        ],

        preferred_locations=[
            "Germany",
            "Berlin",
        ],

        employment_types=[
            "Full-time",
        ],

        technical_skills=[
            "Python",
            "SQL",
            "Google Cloud Platform",
        ],

        languages=[
            "English",
            "German",
        ],

        certifications=[
            "Example Certification",
        ],

        verified=True,
    )

    saved = (
        career_database
        .save_profile(
            profile
        )
    )

    assert (
        saved.full_name
        == "Test Candidate"
    )

    assert (
        saved.city
        == "Chemnitz"
    )

    assert (
        saved.target_roles
        == [
            "Data Engineer",
            "Cloud Data Engineer",
        ]
    )

    assert (
        "Google Cloud Platform"
        in saved.technical_skills
    )

    assert (
        saved.verified
        is True
    )


def test_profile_update(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    career_database.save_profile(
        CareerProfile(
            full_name="Candidate",
            email="old@example.com",
        )
    )

    updated = (
        career_database
        .save_profile(
            CareerProfile(
                full_name="Candidate",
                email="new@example.com",
                target_roles=[
                    "Data Engineer"
                ],
            )
        )
    )

    assert (
        updated.email
        == "new@example.com"
    )

    assert (
        updated.target_roles
        == ["Data Engineer"]
    )


def test_duplicate_list_values_are_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        career_database
        .save_profile(
            CareerProfile(
                full_name="Candidate",
                email="candidate@example.com",
                technical_skills=[
                    "Python",
                    "python",
                    "SQL",
                    "SQL",
                ],
            )
        )
    )

    assert (
        saved.technical_skills
        == [
            "Python",
            "SQL",
        ]
    )


def test_profile_exists(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    assert (
        career_database.profile_exists()
        is False
    )

    career_database.save_profile(
        CareerProfile(
            full_name="Candidate",
            email="candidate@example.com",
        )
    )

    assert (
        career_database.profile_exists()
        is True
    )


def test_truth_lock_can_be_changed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    career_database.save_profile(
        CareerProfile(
            full_name="Candidate",
            email="candidate@example.com",
            verified=False,
        )
    )

    result = (
        career_database
        .set_profile_verification(
            True
        )
    )

    assert (
        result.is_truth_locked()
        is True
    )
