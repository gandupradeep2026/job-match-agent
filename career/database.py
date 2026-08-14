from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from career.models import CareerProfile


DATABASE_PATH = Path(
    "database/career_profile.db"
)


def _utc_now() -> str:
    """
    Return an ISO formatted UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def get_connection() -> sqlite3.Connection:
    """
    Open the Career Profile SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def _encode_list(
    values: list[str],
) -> str:
    """
    Store a Python list safely as JSON.
    """

    cleaned = []

    seen = set()

    for value in values or []:
        item = str(
            value
        ).strip()

        if not item:
            continue

        key = item.casefold()

        if key in seen:
            continue

        seen.add(
            key
        )

        cleaned.append(
            item
        )

    return json.dumps(
        cleaned,
        ensure_ascii=False,
    )


def _decode_list(
    value: str | None,
) -> list[str]:
    """
    Convert stored JSON back into a list.

    Invalid or empty values safely return an empty list.
    """

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


def create_career_profile_table() -> None:
    """
    Create the Master Career Profile table.

    The application currently maintains one master profile,
    represented by row ID 1.
    """

    connection = (
        get_connection()
    )

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS career_profile (
                id INTEGER PRIMARY KEY
                    CHECK (id = 1),

                full_name TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',

                city TEXT NOT NULL DEFAULT '',
                country TEXT NOT NULL DEFAULT '',

                linkedin_url TEXT NOT NULL DEFAULT '',
                github_url TEXT NOT NULL DEFAULT '',

                professional_summary_en
                    TEXT NOT NULL DEFAULT '',

                professional_summary_de
                    TEXT NOT NULL DEFAULT '',

                target_roles
                    TEXT NOT NULL DEFAULT '[]',

                preferred_locations
                    TEXT NOT NULL DEFAULT '[]',

                employment_types
                    TEXT NOT NULL DEFAULT '[]',

                technical_skills
                    TEXT NOT NULL DEFAULT '[]',

                languages
                    TEXT NOT NULL DEFAULT '[]',

                certifications
                    TEXT NOT NULL DEFAULT '[]',

                verified INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def profile_exists() -> bool:
    """
    Return whether a Master Career Profile has been saved.
    """

    create_career_profile_table()

    connection = (
        get_connection()
    )

    try:
        row = connection.execute(
            """
            SELECT id
            FROM career_profile
            WHERE id = 1
            """
        ).fetchone()

        return row is not None

    finally:
        connection.close()


def save_profile(
    profile: CareerProfile,
) -> CareerProfile:
    """
    Insert or update the Master Career Profile.

    A single profile is stored with ID 1.
    """

    create_career_profile_table()

    now = _utc_now()

    created_at = (
        profile.created_at.strip()
        if profile.created_at
        else now
    )

    connection = (
        get_connection()
    )

    try:
        connection.execute(
            """
            INSERT INTO career_profile (
                id,

                full_name,
                email,
                phone,

                city,
                country,

                linkedin_url,
                github_url,

                professional_summary_en,
                professional_summary_de,

                target_roles,
                preferred_locations,
                employment_types,

                technical_skills,
                languages,
                certifications,

                verified,

                created_at,
                updated_at
            )
            VALUES (
                1,

                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?,
                ?, ?
            )

            ON CONFLICT(id)
            DO UPDATE SET

                full_name = excluded.full_name,
                email = excluded.email,
                phone = excluded.phone,

                city = excluded.city,
                country = excluded.country,

                linkedin_url = excluded.linkedin_url,
                github_url = excluded.github_url,

                professional_summary_en =
                    excluded.professional_summary_en,

                professional_summary_de =
                    excluded.professional_summary_de,

                target_roles =
                    excluded.target_roles,

                preferred_locations =
                    excluded.preferred_locations,

                employment_types =
                    excluded.employment_types,

                technical_skills =
                    excluded.technical_skills,

                languages =
                    excluded.languages,

                certifications =
                    excluded.certifications,

                verified =
                    excluded.verified,

                updated_at =
                    excluded.updated_at
            """,
            (
                profile.full_name.strip(),
                profile.email.strip(),
                profile.phone.strip(),

                profile.city.strip(),
                profile.country.strip(),

                profile.linkedin_url.strip(),
                profile.github_url.strip(),

                (
                    profile
                    .professional_summary_en
                    .strip()
                ),

                (
                    profile
                    .professional_summary_de
                    .strip()
                ),

                _encode_list(
                    profile.target_roles
                ),

                _encode_list(
                    profile.preferred_locations
                ),

                _encode_list(
                    profile.employment_types
                ),

                _encode_list(
                    profile.technical_skills
                ),

                _encode_list(
                    profile.languages
                ),

                _encode_list(
                    profile.certifications
                ),

                int(
                    bool(
                        profile.verified
                    )
                ),

                created_at,
                now,
            ),
        )

        connection.commit()

    finally:
        connection.close()

    return load_profile()


def load_profile() -> CareerProfile:
    """
    Load the saved Master Career Profile.

    If no profile exists yet, return an empty CareerProfile.
    """

    create_career_profile_table()

    connection = (
        get_connection()
    )

    try:
        row = connection.execute(
            """
            SELECT *
            FROM career_profile
            WHERE id = 1
            """
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        return CareerProfile()

    return CareerProfile(
        full_name=(
            row["full_name"]
            or ""
        ),
        email=(
            row["email"]
            or ""
        ),
        phone=(
            row["phone"]
            or ""
        ),
        city=(
            row["city"]
            or ""
        ),
        country=(
            row["country"]
            or ""
        ),
        linkedin_url=(
            row["linkedin_url"]
            or ""
        ),
        github_url=(
            row["github_url"]
            or ""
        ),
        professional_summary_en=(
            row[
                "professional_summary_en"
            ]
            or ""
        ),
        professional_summary_de=(
            row[
                "professional_summary_de"
            ]
            or ""
        ),
        target_roles=(
            _decode_list(
                row[
                    "target_roles"
                ]
            )
        ),
        preferred_locations=(
            _decode_list(
                row[
                    "preferred_locations"
                ]
            )
        ),
        employment_types=(
            _decode_list(
                row[
                    "employment_types"
                ]
            )
        ),
        technical_skills=(
            _decode_list(
                row[
                    "technical_skills"
                ]
            )
        ),
        languages=(
            _decode_list(
                row[
                    "languages"
                ]
            )
        ),
        certifications=(
            _decode_list(
                row[
                    "certifications"
                ]
            )
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


def set_profile_verification(
    verified: bool,
) -> CareerProfile:
    """
    Enable or disable the profile-wide Truth Lock.
    """

    profile = (
        load_profile()
    )

    profile.verified = bool(
        verified
    )

    return save_profile(
        profile
    )
