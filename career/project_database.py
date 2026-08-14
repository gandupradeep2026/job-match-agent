from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.project import ProjectRecord


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


def create_projects_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name_en TEXT NOT NULL DEFAULT '',
                name_de TEXT NOT NULL DEFAULT '',

                project_type TEXT NOT NULL DEFAULT '',

                role_en TEXT NOT NULL DEFAULT '',
                role_de TEXT NOT NULL DEFAULT '',

                start_date TEXT NOT NULL DEFAULT '',
                end_date TEXT NOT NULL DEFAULT '',
                is_current INTEGER NOT NULL DEFAULT 0,

                description_en TEXT NOT NULL DEFAULT '',
                description_de TEXT NOT NULL DEFAULT '',

                responsibilities_en TEXT NOT NULL DEFAULT '[]',
                responsibilities_de TEXT NOT NULL DEFAULT '[]',

                achievements_en TEXT NOT NULL DEFAULT '[]',
                achievements_de TEXT NOT NULL DEFAULT '[]',

                technologies TEXT NOT NULL DEFAULT '[]',
                skills TEXT NOT NULL DEFAULT '[]',

                repository_url TEXT NOT NULL DEFAULT '',
                demo_url TEXT NOT NULL DEFAULT '',

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
) -> ProjectRecord:
    return ProjectRecord(
        id=row["id"],
        name_en=row["name_en"] or "",
        name_de=row["name_de"] or "",
        project_type=(
            row["project_type"]
            or ""
        ),
        role_en=row["role_en"] or "",
        role_de=row["role_de"] or "",
        start_date=(
            row["start_date"]
            or ""
        ),
        end_date=(
            row["end_date"]
            or ""
        ),
        is_current=bool(
            row["is_current"]
        ),
        description_en=(
            row["description_en"]
            or ""
        ),
        description_de=(
            row["description_de"]
            or ""
        ),
        responsibilities_en=_decode_list(
            row["responsibilities_en"]
        ),
        responsibilities_de=_decode_list(
            row["responsibilities_de"]
        ),
        achievements_en=_decode_list(
            row["achievements_en"]
        ),
        achievements_de=_decode_list(
            row["achievements_de"]
        ),
        technologies=_decode_list(
            row["technologies"]
        ),
        skills=_decode_list(
            row["skills"]
        ),
        repository_url=(
            row["repository_url"]
            or ""
        ),
        demo_url=(
            row["demo_url"]
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


def save_project_record(
    record: ProjectRecord,
) -> ProjectRecord:
    create_projects_table()

    now = _utc_now()

    connection = _get_connection()

    try:
        if record.id is None:
            cursor = connection.execute(
                """
                INSERT INTO projects (
                    name_en,
                    name_de,
                    project_type,
                    role_en,
                    role_de,
                    start_date,
                    end_date,
                    is_current,
                    description_en,
                    description_de,
                    responsibilities_en,
                    responsibilities_de,
                    achievements_en,
                    achievements_de,
                    technologies,
                    skills,
                    repository_url,
                    demo_url,
                    verified,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    record.name_en.strip(),
                    record.name_de.strip(),
                    record.project_type.strip(),
                    record.role_en.strip(),
                    record.role_de.strip(),
                    record.start_date.strip(),
                    (
                        ""
                        if record.is_current
                        else record.end_date.strip()
                    ),
                    int(
                        bool(
                            record.is_current
                        )
                    ),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    _encode_list(
                        record.responsibilities_en
                    ),
                    _encode_list(
                        record.responsibilities_de
                    ),
                    _encode_list(
                        record.achievements_en
                    ),
                    _encode_list(
                        record.achievements_de
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    _encode_list(
                        record.skills
                    ),
                    record.repository_url.strip(),
                    record.demo_url.strip(),
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
                UPDATE projects
                SET
                    name_en = ?,
                    name_de = ?,
                    project_type = ?,
                    role_en = ?,
                    role_de = ?,
                    start_date = ?,
                    end_date = ?,
                    is_current = ?,
                    description_en = ?,
                    description_de = ?,
                    responsibilities_en = ?,
                    responsibilities_de = ?,
                    achievements_en = ?,
                    achievements_de = ?,
                    technologies = ?,
                    skills = ?,
                    repository_url = ?,
                    demo_url = ?,
                    verified = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record.name_en.strip(),
                    record.name_de.strip(),
                    record.project_type.strip(),
                    record.role_en.strip(),
                    record.role_de.strip(),
                    record.start_date.strip(),
                    (
                        ""
                        if record.is_current
                        else record.end_date.strip()
                    ),
                    int(
                        bool(
                            record.is_current
                        )
                    ),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    _encode_list(
                        record.responsibilities_en
                    ),
                    _encode_list(
                        record.responsibilities_de
                    ),
                    _encode_list(
                        record.achievements_en
                    ),
                    _encode_list(
                        record.achievements_de
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    _encode_list(
                        record.skills
                    ),
                    record.repository_url.strip(),
                    record.demo_url.strip(),
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

    saved = get_project_record(
        record_id
    )

    if saved is None:
        raise RuntimeError(
            "Project record could not be loaded after saving."
        )

    return saved


def get_project_record(
    record_id: int,
) -> ProjectRecord | None:
    create_projects_table()

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM projects
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


def get_project_records() -> list[ProjectRecord]:
    create_projects_table()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM projects
            ORDER BY
                is_current DESC,
                start_date DESC,
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


def delete_project_record(
    record_id: int,
) -> bool:
    create_projects_table()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM projects
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
