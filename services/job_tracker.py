import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path("database/applications.db")


def get_connection() -> sqlite3.Connection:
    """
    Open a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def get_existing_columns(
    connection: sqlite3.Connection,
) -> set[str]:
    """
    Return all existing columns from the applications table.
    """

    rows = connection.execute(
        "PRAGMA table_info(applications)"
    ).fetchall()

    return {
        row["name"]
        for row in rows
    }


def add_missing_columns(
    connection: sqlite3.Connection,
) -> None:
    """
    Add newer fields to an existing database.

    This lets older databases continue working without
    deleting existing application records.
    """

    existing_columns = get_existing_columns(
        connection
    )

    new_columns = {
        "location": "TEXT",
        "contact_phone": "TEXT",
        "updated_at": "TEXT",
        "last_follow_up_date": "TEXT",
        "next_follow_up_date": "TEXT",
        "application_source": "TEXT",
        "cv_version": "TEXT",
        "cover_letter_version": "TEXT",
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"""
                ALTER TABLE applications
                ADD COLUMN {column_name} {column_type}
                """
            )

    connection.commit()


def create_applications_table() -> None:
    """
    Create the applications table if it does not exist.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                job_title TEXT NOT NULL,
                location TEXT,
                application_date TEXT NOT NULL,
                status TEXT NOT NULL,
                job_url TEXT,
                contact_name TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                skill_match_score REAL,
                ats_score REAL,
                overall_match_score REAL,
                notes TEXT,
                last_follow_up_date TEXT,
                next_follow_up_date TEXT,
                application_source TEXT,
                cv_version TEXT,
                cover_letter_version TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """
        )

        connection.commit()

        add_missing_columns(
            connection
        )

    finally:
        connection.close()


def save_application(
    company: str,
    job_title: str,
    location: str,
    application_date: str,
    status: str,
    job_url: str,
    contact_name: str,
    contact_email: str,
    contact_phone: str,
    skill_match_score: float,
    ats_score: float,
    overall_match_score: float,
    notes: str,
    last_follow_up_date: str = "",
    next_follow_up_date: str = "",
    application_source: str = "",
    cv_version: str = "",
    cover_letter_version: str = "",
) -> int:
    """
    Save one verified application and return its ID.
    """

    connection = get_connection()

    current_time = datetime.now().isoformat(
        timespec="seconds"
    )

    try:
        cursor = connection.execute(
            """
            INSERT INTO applications (
                company,
                job_title,
                location,
                application_date,
                status,
                job_url,
                contact_name,
                contact_email,
                contact_phone,
                skill_match_score,
                ats_score,
                overall_match_score,
                notes,
                last_follow_up_date,
                next_follow_up_date,
                application_source,
                cv_version,
                cover_letter_version,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                company.strip(),
                job_title.strip(),
                location.strip(),
                application_date,
                status,
                job_url.strip(),
                contact_name.strip(),
                contact_email.strip(),
                contact_phone.strip(),
                skill_match_score,
                ats_score,
                overall_match_score,
                notes.strip(),
                last_follow_up_date,
                next_follow_up_date,
                application_source.strip(),
                cv_version.strip(),
                cover_letter_version.strip(),
                current_time,
                current_time,
            ),
        )

        connection.commit()

        return int(cursor.lastrowid)

    finally:
        connection.close()


def get_all_applications() -> list[dict]:
    """
    Return all applications, newest first.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM applications
            ORDER BY id DESC
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()


def get_application_by_id(
    application_id: int,
) -> dict | None:
    """
    Return one application using its database ID.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM applications
            WHERE id = ?
            """,
            (application_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def update_application(
    application_id: int,
    company: str,
    job_title: str,
    location: str,
    application_date: str,
    status: str,
    job_url: str,
    contact_name: str,
    contact_email: str,
    contact_phone: str,
    notes: str,
    last_follow_up_date: str,
    next_follow_up_date: str,
    application_source: str,
    cv_version: str,
    cover_letter_version: str,
) -> bool:
    """
    Update an existing application.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE applications
            SET
                company = ?,
                job_title = ?,
                location = ?,
                application_date = ?,
                status = ?,
                job_url = ?,
                contact_name = ?,
                contact_email = ?,
                contact_phone = ?,
                notes = ?,
                last_follow_up_date = ?,
                next_follow_up_date = ?,
                application_source = ?,
                cv_version = ?,
                cover_letter_version = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                company.strip(),
                job_title.strip(),
                location.strip(),
                application_date,
                status,
                job_url.strip(),
                contact_name.strip(),
                contact_email.strip(),
                contact_phone.strip(),
                notes.strip(),
                last_follow_up_date,
                next_follow_up_date,
                application_source.strip(),
                cv_version.strip(),
                cover_letter_version.strip(),
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                application_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def delete_application(
    application_id: int,
) -> bool:
    """
    Permanently delete an application.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM applications
            WHERE id = ?
            """,
            (application_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()