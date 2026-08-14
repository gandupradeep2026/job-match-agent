from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.star_story import StarStory


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def _encode_list(
    values: list[str],
) -> str:
    cleaned = []
    seen = set()

    for value in values or []:
        item = str(value).strip()

        if not item:
            continue

        key = item.casefold()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(item)

    return json.dumps(
        cleaned,
        ensure_ascii=False,
    )


def _decode_list(
    value: str | None,
) -> list[str]:
    if not value:
        return []

    try:
        result = json.loads(
            value
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return []

    if not isinstance(
        result,
        list,
    ):
        return []

    return [
        str(item).strip()
        for item in result
        if str(item).strip()
    ]


def create_star_story_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS star_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title_en TEXT NOT NULL DEFAULT '',
                title_de TEXT NOT NULL DEFAULT '',

                category TEXT NOT NULL DEFAULT '',
                source_type TEXT NOT NULL DEFAULT '',
                source_name TEXT NOT NULL DEFAULT '',

                situation_en TEXT NOT NULL DEFAULT '',
                situation_de TEXT NOT NULL DEFAULT '',

                task_en TEXT NOT NULL DEFAULT '',
                task_de TEXT NOT NULL DEFAULT '',

                action_en TEXT NOT NULL DEFAULT '',
                action_de TEXT NOT NULL DEFAULT '',

                result_en TEXT NOT NULL DEFAULT '',
                result_de TEXT NOT NULL DEFAULT '',

                lesson_en TEXT NOT NULL DEFAULT '',
                lesson_de TEXT NOT NULL DEFAULT '',

                metric_value TEXT NOT NULL DEFAULT '',

                competencies TEXT NOT NULL DEFAULT '[]',
                technologies TEXT NOT NULL DEFAULT '[]',
                question_tags TEXT NOT NULL DEFAULT '[]',

                verified INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def _row_to_record(
    row: sqlite3.Row,
) -> StarStory:
    return StarStory(
        id=row["id"],
        title_en=row["title_en"] or "",
        title_de=row["title_de"] or "",
        category=row["category"] or "",
        source_type=row["source_type"] or "",
        source_name=row["source_name"] or "",
        situation_en=row["situation_en"] or "",
        situation_de=row["situation_de"] or "",
        task_en=row["task_en"] or "",
        task_de=row["task_de"] or "",
        action_en=row["action_en"] or "",
        action_de=row["action_de"] or "",
        result_en=row["result_en"] or "",
        result_de=row["result_de"] or "",
        lesson_en=row["lesson_en"] or "",
        lesson_de=row["lesson_de"] or "",
        metric_value=row["metric_value"] or "",
        competencies=_decode_list(
            row["competencies"]
        ),
        technologies=_decode_list(
            row["technologies"]
        ),
        question_tags=_decode_list(
            row["question_tags"]
        ),
        verified=bool(
            row["verified"]
        ),
        created_at=row["created_at"] or "",
        updated_at=row["updated_at"] or "",
    )


def save_star_story(
    record: StarStory,
) -> StarStory:
    create_star_story_table()

    now = _utc_now()

    connection = _get_connection()

    try:
        if record.id is None:
            cursor = connection.execute(
                """
                INSERT INTO star_stories (
                    title_en,
                    title_de,
                    category,
                    source_type,
                    source_name,
                    situation_en,
                    situation_de,
                    task_en,
                    task_de,
                    action_en,
                    action_de,
                    result_en,
                    result_de,
                    lesson_en,
                    lesson_de,
                    metric_value,
                    competencies,
                    technologies,
                    question_tags,
                    verified,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    record.title_en.strip(),
                    record.title_de.strip(),
                    record.category.strip(),
                    record.source_type.strip(),
                    record.source_name.strip(),
                    record.situation_en.strip(),
                    record.situation_de.strip(),
                    record.task_en.strip(),
                    record.task_de.strip(),
                    record.action_en.strip(),
                    record.action_de.strip(),
                    record.result_en.strip(),
                    record.result_de.strip(),
                    record.lesson_en.strip(),
                    record.lesson_de.strip(),
                    record.metric_value.strip(),
                    _encode_list(
                        record.competencies
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    _encode_list(
                        record.question_tags
                    ),
                    int(
                        bool(
                            record.verified
                        )
                    ),
                    now,
                    now,
                ),
            )

            record_id = int(
                cursor.lastrowid
            )

        else:
            connection.execute(
                """
                UPDATE star_stories
                SET
                    title_en = ?,
                    title_de = ?,
                    category = ?,
                    source_type = ?,
                    source_name = ?,
                    situation_en = ?,
                    situation_de = ?,
                    task_en = ?,
                    task_de = ?,
                    action_en = ?,
                    action_de = ?,
                    result_en = ?,
                    result_de = ?,
                    lesson_en = ?,
                    lesson_de = ?,
                    metric_value = ?,
                    competencies = ?,
                    technologies = ?,
                    question_tags = ?,
                    verified = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record.title_en.strip(),
                    record.title_de.strip(),
                    record.category.strip(),
                    record.source_type.strip(),
                    record.source_name.strip(),
                    record.situation_en.strip(),
                    record.situation_de.strip(),
                    record.task_en.strip(),
                    record.task_de.strip(),
                    record.action_en.strip(),
                    record.action_de.strip(),
                    record.result_en.strip(),
                    record.result_de.strip(),
                    record.lesson_en.strip(),
                    record.lesson_de.strip(),
                    record.metric_value.strip(),
                    _encode_list(
                        record.competencies
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    _encode_list(
                        record.question_tags
                    ),
                    int(
                        bool(
                            record.verified
                        )
                    ),
                    now,
                    record.id,
                ),
            )

            record_id = int(
                record.id
            )

        connection.commit()

    finally:
        connection.close()

    saved = get_star_story(
        record_id
    )

    if saved is None:
        raise RuntimeError(
            "STAR story could not be loaded after saving."
        )

    return saved


def get_star_story(
    record_id: int,
) -> StarStory | None:
    create_star_story_table()

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM star_stories
            WHERE id = ?
            """,
            (
                record_id,
            ),
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        return None

    return _row_to_record(
        row
    )


def get_star_stories() -> list[StarStory]:
    create_star_story_table()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM star_stories
            ORDER BY
                verified DESC,
                updated_at DESC,
                id DESC
            """
        ).fetchall()

    finally:
        connection.close()

    return [
        _row_to_record(
            row
        )
        for row in rows
    ]


def delete_star_story(
    record_id: int,
) -> bool:
    create_star_story_table()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM star_stories
            WHERE id = ?
            """,
            (
                record_id,
            ),
        )

        connection.commit()

        return (
            cursor.rowcount
            > 0
        )

    finally:
        connection.close()
