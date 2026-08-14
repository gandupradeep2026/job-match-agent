from __future__ import annotations

from datetime import datetime

from career.application_tracker_link import (
    CareerApplicationLink,
)
from career.target_company_database import (
    get_target_company,
)
from services import job_tracker


CAREER_COLUMNS = {
    "target_company_id": "INTEGER",
    "career_target_role": "TEXT",
    "preparation_stage": "TEXT",
    "tailored_cv_ready": "INTEGER",
    "interview_pack_ready": "INTEGER",
    "interview_pack_language": "TEXT",
    "career_next_action": "TEXT",
    "career_notes": "TEXT",
    "last_career_sync_at": "TEXT",
}


PREPARATION_STAGES = [
    "Not Started",
    "Profile Ready",
    "CV Ready",
    "Applied",
    "Interview Prep",
    "Interview Ready",
]


INTERVIEW_PACK_LANGUAGES = [
    "",
    "English",
    "Deutsch",
    "Both / Beide",
]


def ensure_career_application_columns() -> None:
    """
    Extend the existing applications table using the same additive
    migration pattern already used by the Job Tracker.
    """

    job_tracker.create_applications_table()

    connection = (
        job_tracker.get_connection()
    )

    try:
        existing = (
            job_tracker.get_existing_columns(
                connection
            )
        )

        for column_name, column_type in (
            CAREER_COLUMNS.items()
        ):
            if column_name in existing:
                continue

            connection.execute(
                f"""
                ALTER TABLE applications
                ADD COLUMN {column_name} {column_type}
                """
            )

        connection.commit()

    finally:
        connection.close()


def _row_to_link(
    application: dict,
) -> CareerApplicationLink:
    target_company_id = (
        application.get(
            "target_company_id"
        )
    )

    if target_company_id in (
        "",
        None,
    ):
        target_company_id = None
    else:
        target_company_id = int(
            target_company_id
        )

    return CareerApplicationLink(
        application_id=int(
            application["id"]
        ),
        target_company_id=(
            target_company_id
        ),
        career_target_role=(
            application.get(
                "career_target_role"
            )
            or ""
        ),
        preparation_stage=(
            application.get(
                "preparation_stage"
            )
            or "Not Started"
        ),
        tailored_cv_ready=bool(
            application.get(
                "tailored_cv_ready"
            )
        ),
        interview_pack_ready=bool(
            application.get(
                "interview_pack_ready"
            )
        ),
        interview_pack_language=(
            application.get(
                "interview_pack_language"
            )
            or ""
        ),
        career_next_action=(
            application.get(
                "career_next_action"
            )
            or ""
        ),
        career_notes=(
            application.get(
                "career_notes"
            )
            or ""
        ),
        last_career_sync_at=(
            application.get(
                "last_career_sync_at"
            )
            or ""
        ),
    )


def get_career_application_link(
    application_id: int,
) -> CareerApplicationLink | None:
    ensure_career_application_columns()

    application = (
        job_tracker.get_application_by_id(
            application_id
        )
    )

    if application is None:
        return None

    return _row_to_link(
        application
    )


def save_career_application_link(
    link: CareerApplicationLink,
) -> CareerApplicationLink:
    ensure_career_application_columns()

    application = (
        job_tracker.get_application_by_id(
            link.application_id
        )
    )

    if application is None:
        raise ValueError(
            "Application does not exist."
        )

    if (
        link.target_company_id
        is not None
        and get_target_company(
            link.target_company_id
        )
        is None
    ):
        raise ValueError(
            "Target company does not exist."
        )

    if (
        link.preparation_stage
        not in PREPARATION_STAGES
    ):
        raise ValueError(
            "Invalid preparation stage."
        )

    if (
        link.interview_pack_language
        not in INTERVIEW_PACK_LANGUAGES
    ):
        raise ValueError(
            "Invalid interview pack language."
        )

    sync_time = (
        datetime.now().isoformat(
            timespec="seconds"
        )
    )

    connection = (
        job_tracker.get_connection()
    )

    try:
        cursor = connection.execute(
            """
            UPDATE applications
            SET
                target_company_id = ?,
                career_target_role = ?,
                preparation_stage = ?,
                tailored_cv_ready = ?,
                interview_pack_ready = ?,
                interview_pack_language = ?,
                career_next_action = ?,
                career_notes = ?,
                last_career_sync_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                link.target_company_id,
                link.career_target_role.strip(),
                link.preparation_stage,
                int(
                    bool(
                        link.tailored_cv_ready
                    )
                ),
                int(
                    bool(
                        link.interview_pack_ready
                    )
                ),
                link.interview_pack_language,
                link.career_next_action.strip(),
                link.career_notes.strip(),
                sync_time,
                sync_time,
                link.application_id,
            ),
        )

        connection.commit()

        if cursor.rowcount <= 0:
            raise ValueError(
                "Application does not exist."
            )

    finally:
        connection.close()

    saved = get_career_application_link(
        link.application_id
    )

    if saved is None:
        raise RuntimeError(
            "Career application link could not be loaded after saving."
        )

    return saved


def get_career_application_overview() -> list[dict]:
    ensure_career_application_columns()

    applications = (
        job_tracker.get_all_applications()
    )

    result = []

    for application in applications:
        company_name = ""

        target_company_id = (
            application.get(
                "target_company_id"
            )
        )

        if target_company_id not in (
            None,
            "",
        ):
            target_company = (
                get_target_company(
                    int(
                        target_company_id
                    )
                )
            )

            if target_company is not None:
                company_name = (
                    target_company.company_name
                )

        result.append(
            {
                "application_id": (
                    application["id"]
                ),
                "company": (
                    application.get(
                        "company"
                    )
                    or ""
                ),
                "job_title": (
                    application.get(
                        "job_title"
                    )
                    or ""
                ),
                "application_status": (
                    application.get(
                        "status"
                    )
                    or ""
                ),
                "target_company": (
                    company_name
                ),
                "career_target_role": (
                    application.get(
                        "career_target_role"
                    )
                    or ""
                ),
                "preparation_stage": (
                    application.get(
                        "preparation_stage"
                    )
                    or "Not Started"
                ),
                "tailored_cv_ready": bool(
                    application.get(
                        "tailored_cv_ready"
                    )
                ),
                "interview_pack_ready": bool(
                    application.get(
                        "interview_pack_ready"
                    )
                ),
                "career_next_action": (
                    application.get(
                        "career_next_action"
                    )
                    or ""
                ),
            }
        )

    return result


def suggest_target_company_id(
    application: dict,
    target_companies,
) -> int | None:
    """
    Suggest a target-company link only for an exact normalized company name.
    """

    application_name = (
        job_tracker.normalize_comparison_text(
            application.get(
                "company"
            )
        )
    )

    if not application_name:
        return None

    for target_company in target_companies:
        target_name = (
            job_tracker.normalize_comparison_text(
                target_company.company_name
            )
        )

        if (
            target_name
            and target_name
            == application_name
        ):
            return target_company.id

    return None
