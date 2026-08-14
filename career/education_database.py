from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.education import EducationRecord


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def create_education_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                institution TEXT NOT NULL DEFAULT '',

                degree_en TEXT NOT NULL DEFAULT '',
                degree_de TEXT NOT NULL DEFAULT '',

                field_of_study_en TEXT NOT NULL DEFAULT '',
                field_of_study_de TEXT NOT NULL DEFAULT '',

                location TEXT NOT NULL DEFAULT '',
                country TEXT NOT NULL DEFAULT '',

                start_date TEXT NOT NULL DEFAULT '',
                end_date TEXT NOT NULL DEFAULT '',
                is_current INTEGER NOT NULL DEFAULT 0,

                grade TEXT NOT NULL DEFAULT '',

                thesis_title_en TEXT NOT NULL DEFAULT '',
                thesis_title_de TEXT NOT NULL DEFAULT '',

                description_en TEXT NOT NULL DEFAULT '',
                description_de TEXT NOT NULL DEFAULT '',

                achievements_en TEXT NOT NULL DEFAULT '[]',
                achievements_de TEXT NOT NULL DEFAULT '[]',

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
) -> EducationRecord:
    return EducationRecord(
        id=row["id"],
        institution=row["institution"] or "",
        degree_en=row["degree_en"] or "",
        degree_de=row["degree_de"] or "",
        field_of_study_en=(
            row["field_of_study_en"]
            or ""
        ),
        field_of_study_de=(
            row["field_of_study_de"]
            or ""
        ),
        location=row["location"] or "",
        country=row["country"] or "",
        start_date=row["start_date"] or "",
        end_date=row["end_date"] or "",
        is_current=bool(row["is_current"]),
        grade=row["grade"] or "",
        thesis_title_en=(
            row["thesis_title_en"]
            or ""
        ),
        thesis_title_de=(
            row["thesis_title_de"]
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
        achievements_en=_decode_list(
            row["achievements_en"]
        ),
        achievements_de=_decode_list(
            row["achievements_de"]
        ),
        verified=bool(row["verified"]),
        created_at=row["created_at"] or "",
        updated_at=row["updated_at"] or "",
    )


def save_education_record(
    record: EducationRecord,
) -> EducationRecord:
    create_education_table()

    now = _utc_now()
    connection = _get_connection()

    try:
        if record.id is None:
            cursor = connection.execute(
                """
                INSERT INTO education (
                    institution,
                    degree_en,
                    degree_de,
                    field_of_study_en,
                    field_of_study_de,
                    location,
                    country,
                    start_date,
                    end_date,
                    is_current,
                    grade,
                    thesis_title_en,
                    thesis_title_de,
                    description_en,
                    description_de,
                    achievements_en,
                    achievements_de,
                    verified,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    record.institution.strip(),
                    record.degree_en.strip(),
                    record.degree_de.strip(),
                    record.field_of_study_en.strip(),
                    record.field_of_study_de.strip(),
                    record.location.strip(),
                    record.country.strip(),
                    record.start_date.strip(),
                    (
                        ""
                        if record.is_current
                        else record.end_date.strip()
                    ),
                    int(bool(record.is_current)),
                    record.grade.strip(),
                    record.thesis_title_en.strip(),
                    record.thesis_title_de.strip(),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    _encode_list(
                        record.achievements_en
                    ),
                    _encode_list(
                        record.achievements_de
                    ),
                    int(bool(record.verified)),
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
                UPDATE education
                SET
                    institution = ?,
                    degree_en = ?,
                    degree_de = ?,
                    field_of_study_en = ?,
                    field_of_study_de = ?,
                    location = ?,
                    country = ?,
                    start_date = ?,
                    end_date = ?,
                    is_current = ?,
                    grade = ?,
                    thesis_title_en = ?,
                    thesis_title_de = ?,
                    description_en = ?,
                    description_de = ?,
                    achievements_en = ?,
                    achievements_de = ?,
                    verified = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record.institution.strip(),
                    record.degree_en.strip(),
                    record.degree_de.strip(),
                    record.field_of_study_en.strip(),
                    record.field_of_study_de.strip(),
                    record.location.strip(),
                    record.country.strip(),
                    record.start_date.strip(),
                    (
                        ""
                        if record.is_current
                        else record.end_date.strip()
                    ),
                    int(bool(record.is_current)),
                    record.grade.strip(),
                    record.thesis_title_en.strip(),
                    record.thesis_title_de.strip(),
                    record.description_en.strip(),
                    record.description_de.strip(),
                    _encode_list(
                        record.achievements_en
                    ),
                    _encode_list(
                        record.achievements_de
                    ),
                    int(bool(record.verified)),
                    now,
                    record.id,
                ),
            )

            record_id = int(record.id)

        connection.commit()

    finally:
        connection.close()

    saved = get_education_record(
        record_id
    )

    if saved is None:
        raise RuntimeError(
            "Education record could not be loaded after saving."
        )

    return saved


def get_education_record(
    record_id: int,
) -> EducationRecord | None:
    create_education_table()

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM education
            WHERE id = ?
            """,
            (record_id,),
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        return None

    return _row_to_record(row)


def get_education_records() -> list[EducationRecord]:
    create_education_table()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM education
            ORDER BY
                is_current DESC,
                start_date DESC,
                id DESC
            """
        ).fetchall()

    finally:
        connection.close()

    return [
        _row_to_record(row)
        for row in rows
    ]


def delete_education_record(
    record_id: int,
) -> bool:
    create_education_table()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM education
            WHERE id = ?
            """,
            (record_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()
