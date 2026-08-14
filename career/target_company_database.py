from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from career.database import DATABASE_PATH
from career.target_company import TargetCompany


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


def create_target_companies_table() -> None:
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS target_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                company_name TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'B — Strong Target',
                status TEXT NOT NULL DEFAULT 'Researching',

                industry TEXT NOT NULL DEFAULT '',

                headquarters TEXT NOT NULL DEFAULT '',
                germany_locations TEXT NOT NULL DEFAULT '[]',

                target_roles TEXT NOT NULL DEFAULT '[]',
                technologies TEXT NOT NULL DEFAULT '[]',

                careers_url TEXT NOT NULL DEFAULT '',
                company_url TEXT NOT NULL DEFAULT '',
                linkedin_url TEXT NOT NULL DEFAULT '',

                contact_name TEXT NOT NULL DEFAULT '',
                contact_role TEXT NOT NULL DEFAULT '',
                contact_email TEXT NOT NULL DEFAULT '',
                contact_linkedin TEXT NOT NULL DEFAULT '',

                why_company_en TEXT NOT NULL DEFAULT '',
                why_company_de TEXT NOT NULL DEFAULT '',

                why_fit_en TEXT NOT NULL DEFAULT '',
                why_fit_de TEXT NOT NULL DEFAULT '',

                next_action_en TEXT NOT NULL DEFAULT '',
                next_action_de TEXT NOT NULL DEFAULT '',

                notes_en TEXT NOT NULL DEFAULT '',
                notes_de TEXT NOT NULL DEFAULT '',

                last_researched_date TEXT NOT NULL DEFAULT '',

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
) -> TargetCompany:
    return TargetCompany(
        id=row["id"],
        company_name=(
            row["company_name"]
            or ""
        ),
        priority=(
            row["priority"]
            or "B — Strong Target"
        ),
        status=(
            row["status"]
            or "Researching"
        ),
        industry=(
            row["industry"]
            or ""
        ),
        headquarters=(
            row["headquarters"]
            or ""
        ),
        germany_locations=_decode_list(
            row["germany_locations"]
        ),
        target_roles=_decode_list(
            row["target_roles"]
        ),
        technologies=_decode_list(
            row["technologies"]
        ),
        careers_url=(
            row["careers_url"]
            or ""
        ),
        company_url=(
            row["company_url"]
            or ""
        ),
        linkedin_url=(
            row["linkedin_url"]
            or ""
        ),
        contact_name=(
            row["contact_name"]
            or ""
        ),
        contact_role=(
            row["contact_role"]
            or ""
        ),
        contact_email=(
            row["contact_email"]
            or ""
        ),
        contact_linkedin=(
            row["contact_linkedin"]
            or ""
        ),
        why_company_en=(
            row["why_company_en"]
            or ""
        ),
        why_company_de=(
            row["why_company_de"]
            or ""
        ),
        why_fit_en=(
            row["why_fit_en"]
            or ""
        ),
        why_fit_de=(
            row["why_fit_de"]
            or ""
        ),
        next_action_en=(
            row["next_action_en"]
            or ""
        ),
        next_action_de=(
            row["next_action_de"]
            or ""
        ),
        notes_en=(
            row["notes_en"]
            or ""
        ),
        notes_de=(
            row["notes_de"]
            or ""
        ),
        last_researched_date=(
            row["last_researched_date"]
            or ""
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


def save_target_company(
    record: TargetCompany,
) -> TargetCompany:
    create_target_companies_table()

    now = _utc_now()

    connection = _get_connection()

    try:
        if record.id is None:
            cursor = connection.execute(
                """
                INSERT INTO target_companies (
                    company_name,
                    priority,
                    status,
                    industry,
                    headquarters,
                    germany_locations,
                    target_roles,
                    technologies,
                    careers_url,
                    company_url,
                    linkedin_url,
                    contact_name,
                    contact_role,
                    contact_email,
                    contact_linkedin,
                    why_company_en,
                    why_company_de,
                    why_fit_en,
                    why_fit_de,
                    next_action_en,
                    next_action_de,
                    notes_en,
                    notes_de,
                    last_researched_date,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?
                )
                """,
                (
                    record.company_name.strip(),
                    record.priority.strip(),
                    record.status.strip(),
                    record.industry.strip(),
                    record.headquarters.strip(),
                    _encode_list(
                        record.germany_locations
                    ),
                    _encode_list(
                        record.target_roles
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    record.careers_url.strip(),
                    record.company_url.strip(),
                    record.linkedin_url.strip(),
                    record.contact_name.strip(),
                    record.contact_role.strip(),
                    record.contact_email.strip(),
                    record.contact_linkedin.strip(),
                    record.why_company_en.strip(),
                    record.why_company_de.strip(),
                    record.why_fit_en.strip(),
                    record.why_fit_de.strip(),
                    record.next_action_en.strip(),
                    record.next_action_de.strip(),
                    record.notes_en.strip(),
                    record.notes_de.strip(),
                    record.last_researched_date.strip(),
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
                UPDATE target_companies
                SET
                    company_name = ?,
                    priority = ?,
                    status = ?,
                    industry = ?,
                    headquarters = ?,
                    germany_locations = ?,
                    target_roles = ?,
                    technologies = ?,
                    careers_url = ?,
                    company_url = ?,
                    linkedin_url = ?,
                    contact_name = ?,
                    contact_role = ?,
                    contact_email = ?,
                    contact_linkedin = ?,
                    why_company_en = ?,
                    why_company_de = ?,
                    why_fit_en = ?,
                    why_fit_de = ?,
                    next_action_en = ?,
                    next_action_de = ?,
                    notes_en = ?,
                    notes_de = ?,
                    last_researched_date = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    record.company_name.strip(),
                    record.priority.strip(),
                    record.status.strip(),
                    record.industry.strip(),
                    record.headquarters.strip(),
                    _encode_list(
                        record.germany_locations
                    ),
                    _encode_list(
                        record.target_roles
                    ),
                    _encode_list(
                        record.technologies
                    ),
                    record.careers_url.strip(),
                    record.company_url.strip(),
                    record.linkedin_url.strip(),
                    record.contact_name.strip(),
                    record.contact_role.strip(),
                    record.contact_email.strip(),
                    record.contact_linkedin.strip(),
                    record.why_company_en.strip(),
                    record.why_company_de.strip(),
                    record.why_fit_en.strip(),
                    record.why_fit_de.strip(),
                    record.next_action_en.strip(),
                    record.next_action_de.strip(),
                    record.notes_en.strip(),
                    record.notes_de.strip(),
                    record.last_researched_date.strip(),
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

    saved = get_target_company(
        record_id
    )

    if saved is None:
        raise RuntimeError(
            "Target company could not be loaded after saving."
        )

    return saved


def get_target_company(
    record_id: int,
) -> TargetCompany | None:
    create_target_companies_table()

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM target_companies
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


def get_target_companies() -> list[TargetCompany]:
    create_target_companies_table()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM target_companies
            ORDER BY
                CASE priority
                    WHEN 'A — Dream Company' THEN 1
                    WHEN 'B — Strong Target' THEN 2
                    WHEN 'C — Secondary Target' THEN 3
                    ELSE 4
                END,
                company_name COLLATE NOCASE,
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


def delete_target_company(
    record_id: int,
) -> bool:
    create_target_companies_table()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM target_companies
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
