from market_intelligence.cv_skill_bridge import (
    CVSkillBridge,
)


bridge = CVSkillBridge()


def test_extracts_data_engineering_cv_skills():

    profile = bridge.extract_skills(
        """
        Data Engineer with experience in
        Python, SQL, PySpark, Apache Spark,
        Google Cloud Platform, BigQuery,
        Docker and Git.
        """
    )

    assert "Python" in profile.skills
    assert "SQL" in profile.skills
    assert "PySpark" in profile.skills
    assert "Apache Spark" in profile.skills

    assert (
        "Google Cloud Platform"
        in profile.skills
    )

    assert "BigQuery" in profile.skills
    assert "Docker" in profile.skills
    assert "Git" in profile.skills

    assert profile.skill_count >= 8


def test_extracts_german_hospitality_cv_skills():

    profile = bridge.extract_skills(
        """
        Erfahrung im Kundenservice,
        an der Rezeption sowie mit
        Reservierungssystemen.

        Erfahrung mit SAP und Excel.
        Sehr gute Kommunikationsfähigkeit.
        """
    )

    assert (
        "Customer Service"
        in profile.skills
    )

    assert "Front Office" in profile.skills

    assert (
        "Reservation Management"
        in profile.skills
    )

    assert "SAP" in profile.skills
    assert "Microsoft Excel" in profile.skills
    assert "Communication" in profile.skills


def test_empty_cv_returns_empty_profile():

    profile = bridge.extract_skills("")

    assert profile.skills == []
    assert profile.skill_count == 0
    assert profile.source_text_length == 0
