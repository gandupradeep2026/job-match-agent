from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.work_experience import WorkExperience


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _encode_list(values: list[str]) -> str:
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

    return json.dumps(cleaned, ensure_ascii=False)


def _decode_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        result = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(result, list):
        return []

    return [
        str(item).strip()
        for item in result
        if str(item).strip()
    ]


def create_work_experience_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS work_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer TEXT NOT NULL DEFAULT '',
                job_title_en TEXT NOT NULL DEFAULT '',
                job_title_de TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                country TEXT NOT NULL DEFAULT '',
                start_date TEXT NOT NULL DEFAULT '',
                end_date TEXT NOT NULL DEFAULT '',
                is_current INTEGER NOT NULL DEFAULT 0,
                employment_type TEXT NOT NULL DEFAULT '',
                description_en TEXT NOT NULL DEFAULT '',
                description_de TEXT NOT NULL DEFAULT '',
                achievements_en TEXT NOT NULL DEFAULT '[]',
                achievements_de TEXT NOT NULL DEFAULT '[]',
                technologies TEXT NOT NULL DEFAULT '[]',
                verified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def _row_to_experience(row: sqlite3.Row) -> WorkExperience:
    return WorkExperience(
        id=row["id"],
        employer=row["employer"] or "",
        job_title_en=row["job_title_en"] or "",
        job_title_de=row["job_title_de"] or "",
        location=row["location"] or "",
        country=row["country"] or "",
        start_date=row["start_date"] or "",
        end_date=row["end_date"] or "",
        is_current=bool(row["is_current"]),
        employment_type=row["employment_type"] or "",
        description_en=row["description_en"] or "",
        description_de=row["description_de"] or "",
        achievements_en=_decode_list(row["achievements_en"]),
        achievements_de=_decode_list(row["achievements_de"]),
        technologies=_decode_list(row["technologies"]),
        verified=bool(row["verified"]),
        created_at=row["created_at"] or "",
        updated_at=row["updated_at"] or "",
    )


def save_work_experience(
    experience: WorkExperience,
) -> WorkExperience:
    create_work_experience_table()
    now = _utc_now()
    connection = _get_connection()

    try:
        if experience.id is None:
            cursor = connection.execute(
                """
                INSERT INTO work_experience (
                    employer,
                    job_title_en,
                    job_title_de,
                    location,
                    country,
                    start_date,
                    end_date,
                    is_current,
                    employment_type,
                    description_en,
                    description_de,
                    achievements_en,
                    achievements_de,
                    technologies,
                    verified,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experience.employer.strip(),
                    experience.job_title_en.strip(),
                    experience.job_title_de.strip(),
                    experience.location.strip(),
                    experience.country.strip(),
                    experience.start_date.strip(),
                    "" if experience.is_current else experience.end_date.strip(),
                    int(bool(experience.is_current)),
                    experience.employment_type.strip(),
                    experience.description_en.strip(),
                    experience.description_de.strip(),
                    _encode_list(experience.achievements_en),
                    _encode_list(experience.achievements_de),
                    _encode_list(experience.technologies),
                    int(bool(experience.verified)),
                    now,
                    now,
                ),
            )
            experience_id = int(cursor.lastrowid)
        else:
            connection.execute(
                """
                UPDATE work_experience
                SET
                    employer = ?,
                    job_title_en = ?,
                    job_title_de = ?,
                    location = ?,
                    country = ?,
                    start_date = ?,
                    end_date = ?,
                    is_current = ?,
                    employment_type = ?,
                    description_en = ?,
                    description_de = ?,
                    achievements_en = ?,
                    achievements_de = ?,
                    technologies = ?,
                    verified = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    experience.employer.strip(),
                    experience.job_title_en.strip(),
                    experience.job_title_de.strip(),
                    experience.location.strip(),
                    experience.country.strip(),
                    experience.start_date.strip(),
                    "" if experience.is_current else experience.end_date.strip(),
                    int(bool(experience.is_current)),
                    experience.employment_type.strip(),
                    experience.description_en.strip(),
                    experience.description_de.strip(),
                    _encode_list(experience.achievements_en),
                    _encode_list(experience.achievements_de),
                    _encode_list(experience.technologies),
                    int(bool(experience.verified)),
                    now,
                    experience.id,
                ),
            )
            experience_id = int(experience.id)

        connection.commit()
    finally:
        connection.close()

    saved = get_work_experience(experience_id)
    if saved is None:
        raise RuntimeError(
            "Work experience could not be loaded after saving."
        )

    return saved


def get_work_experience(
    experience_id: int,
) -> WorkExperience | None:
    create_work_experience_table()
    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM work_experience
            WHERE id = ?
            """,
            (experience_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return _row_to_experience(row)


def get_work_experiences() -> list[WorkExperience]:
    create_work_experience_table()
    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM work_experience
            ORDER BY
                is_current DESC,
                start_date DESC,
                id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [
        _row_to_experience(row)
        for row in rows
    ]


def delete_work_experience(
    experience_id: int,
) -> bool:
    create_work_experience_table()
    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM work_experience
            WHERE id = ?
            """,
            (experience_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()
