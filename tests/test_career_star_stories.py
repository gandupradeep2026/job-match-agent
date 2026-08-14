from career.star_story import StarStory
import career.database as career_database
import career.star_story_database as star_database


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
        star_database,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_complete_english_story_is_valid():
    record = StarStory(
        title_en="Solved a data issue",
        situation_en="A pipeline failed.",
        task_en="I had to restore it.",
        action_en="I diagnosed and fixed the issue.",
        result_en="The pipeline worked again.",
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_complete_german_story_is_valid():
    record = StarStory(
        title_de="Datenproblem gelöst",
        situation_de="Eine Pipeline fiel aus.",
        task_de="Ich sollte sie wiederherstellen.",
        action_de="Ich analysierte und behob den Fehler.",
        result_de="Die Pipeline lief wieder.",
    )

    assert (
        record.has_required_fields()
        is True
    )


def test_incomplete_story_is_invalid():
    record = StarStory(
        title_en="Incomplete",
        situation_en="Situation",
        task_en="Task",
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
        star_database
        .save_star_story(
            StarStory(
                title_en="Optimized pipeline",
                title_de="Pipeline optimiert",
                category="Problem Solving",
                source_type="Project",
                source_name="Cloud Pipeline",
                situation_en="The job was slow.",
                task_en="Improve processing time.",
                action_en="I profiled and optimized the transformation.",
                result_en="Runtime improved.",
                situation_de="Der Job war langsam.",
                task_de="Die Laufzeit verbessern.",
                action_de="Ich analysierte und optimierte die Verarbeitung.",
                result_de="Die Laufzeit wurde verbessert.",
                metric_value="30% faster",
                competencies=[
                    "Problem Solving",
                    "Optimization",
                ],
                technologies=[
                    "Python",
                    "Spark",
                ],
                question_tags=[
                    "Tell me about a challenge",
                ],
                verified=True,
            )
        )
    )

    assert saved.id is not None
    assert (
        saved.category
        == "Problem Solving"
    )
    assert (
        saved.metric_value
        == "30% faster"
    )
    assert saved.verified is True


def test_update_story(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        star_database
        .save_star_story(
            StarStory(
                title_en="Initial",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
            )
        )
    )

    saved.title_en = (
        "Updated"
    )

    updated = (
        star_database
        .save_star_story(
            saved
        )
    )

    assert (
        updated.title_en
        == "Updated"
    )


def test_verified_stories_sort_first(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    star_database.save_star_story(
        StarStory(
            title_en="Unverified",
            situation_en="S",
            task_en="T",
            action_en="A",
            result_en="R",
            verified=False,
        )
    )

    star_database.save_star_story(
        StarStory(
            title_en="Verified",
            situation_en="S",
            task_en="T",
            action_en="A",
            result_en="R",
            verified=True,
        )
    )

    records = (
        star_database
        .get_star_stories()
    )

    assert (
        records[0].title_en
        == "Verified"
    )


def test_delete_story(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        star_database
        .save_star_story(
            StarStory(
                title_en="Delete Me",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
            )
        )
    )

    deleted = (
        star_database
        .delete_star_story(
            saved.id
        )
    )

    assert deleted is True
    assert (
        star_database
        .get_star_stories()
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
        star_database
        .save_star_story(
            StarStory(
                title_en="Test",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
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


def test_duplicate_question_tags_removed(
    tmp_path,
    monkeypatch,
):
    _use_temp_database(
        tmp_path,
        monkeypatch,
    )

    saved = (
        star_database
        .save_star_story(
            StarStory(
                title_en="Test",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
                question_tags=[
                    "Failure",
                    "failure",
                    "Challenge",
                    "Challenge",
                ],
            )
        )
    )

    assert saved.question_tags == [
        "Failure",
        "Challenge",
    ]
