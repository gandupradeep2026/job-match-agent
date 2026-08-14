from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.achievement import AchievementRecord


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
        result = json.loads(value)
    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return []

    if not isinstance(result, list):
        return []

    return [
        str(item).strip()
        for item in result
        if str(item).strip()
    ]


def create_achievements_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title_en TEXT NOT NULL DEFAULT '',
                title_de TEXT NOT NULL DEFAULT '',

                category TEXT NOT NULL DEFAULT '',
                source_type TEXT NOT NULL DEFAULT '',
                source_name TEXT NOT NULL DEFAULT '',

                achievement_date TEXT NOT NULL DEFAULT '',

                description_en TEXT NOT NULL DEFAULT '',
                description_de TEXT NOT NULL DEFAULT '',

                result_en TEXT NOT NULL DEFAULT '',
                result_de TEXT NOT NULL DEFAULT '',

                metric_value TEXT NOT NULL DEFAULT '',

                competencies TEXT NOT NULL DEFAULT '[]',
                technologies TEXT NOT NULL DEFAULT '[]',

                evidence_url TEXT NOT NULL DEFAULT '',

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
) -> AchievementRecord:
    return AchievementRecord(
        id=row["id"],
        title_en=row["title_en"] or "",
        title_de=row["title_de"] or "",
        category=row["category"] or "",
        source_type=row["source_type"] or "",
        source_name=row["source_name"] or "",
        achievement_date=(
            row["achievement_date"]
            or ""
        ),
        description_en=(
            row["description_en"]
            or ""
        ),
        description_de=(
            row["description_de"]
            or ""
        ),
        result_en=(
            row["result_en"]
            or ""
        ),
        result_de=(
            row["result_de"]
            or ""
        ),
        metric_value=(
            row["metric_value"]
            or ""
        ),
        competencies=_decode_list(
            row["competencies"]
        ),
        technologies=_decode_list(
            row["technologies"]
        ),
        evidence_url=(
            row["evidence_url"]
            or ""
        ),
        verified=bool(
            row["verified"]
        ),
        created_at=(
            row["created_at"]
            or ""
        ),
        updated_at=(
            row["updated_at"]
            or ""
        ),
    )


def save_achievement_record(
    record: AchievementRecord,
) -> AchievementRecord:
    create_achievements_table()

    now = _utc_now()
    connection = _get_connection()

    try:
        if record.id is None:
            cursor = connection.execute(
                """
                INSERT INTO achievements (
                    title_en,
                    title_de,
                    category,
                    source_type,
                    source_name,
                    achievement_date,
                    description_en,
                    description_de,
                    result_en,
                    result_de,
                    metric_value,
                    competencies,
                    technologies,
                    evidence_url,
                    verified,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    record.title_en.strip(),
                    record.title_de.strip(),
                    record.category.strip(),
                    record.source_type.strip(),
                    record.source_name.strip(),
                    record.achievement_date.strip(),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    record.result_en.strip(),
                    record.result_de.strip(),
                    record.metric_value.strip(),
                    _encode_list(
                        record.competencies
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    record.evidence_url.strip(),
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
                UPDATE achievements
                SET
                    title_en = ?,
                    title_de = ?,
                    category = ?,
                    source_type = ?,
                    source_name = ?,
                    achievement_date = ?,
                    description_en = ?,
                    description_de = ?,
                    result_en = ?,
                    result_de = ?,
                    metric_value = ?,
                    competencies = ?,
                    technologies = ?,
                    evidence_url = ?,
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
                    record.achievement_date.strip(),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    record.result_en.strip(),
                    record.result_de.strip(),
                    record.metric_value.strip(),
                    _encode_list(
                        record.competencies
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    record.evidence_url.strip(),
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

    saved = get_achievement_record(
        record_id
    )

    if saved is None:
        raise RuntimeError(
            "Achievement record could not be loaded after saving."
        )

    return saved


def get_achievement_record(
    record_id: int,
) -> AchievementRecord | None:
    create_achievements_table()

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM achievements
            WHERE id = ?
            """,
            (record_id,),
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        return None

    return _row_to_record(
        row
    )


def get_achievement_records() -> list[AchievementRecord]:
    create_achievements_table()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM achievements
            ORDER BY
                achievement_date DESC,
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


def delete_achievement_record(
    record_id: int,
) -> bool:
    create_achievements_table()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM achievements
            WHERE id = ?
            """,
            (record_id,),
        )

        connection.commit()

        return (
            cursor.rowcount
            > 0
        )

    finally:
        connection.close()
