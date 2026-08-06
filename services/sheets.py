import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


SHEET_HEADERS = [
    "ID",
    "Company",
    "Job Title",
    "Location",
    "Application Date",
    "Status",
    "Source",
    "Last Follow-up",
    "Next Follow-up",
    "Job URL",
    "Contact Name",
    "Contact Email",
    "Contact Phone",
    "Skill Match",
    "ATS Score",
    "Overall Match",
    "CV Version",
    "Cover Letter Version",
    "Notes",
    "Created At",
    "Updated At",
]


def get_google_settings() -> dict:
    """
    Load Google Sheets configuration from .env.
    """

    load_dotenv()

    enabled_value = os.getenv(
        "GOOGLE_SHEETS_ENABLED",
        "false",
    ).strip().lower()

    return {
        "enabled": enabled_value in {
            "true",
            "1",
            "yes",
            "on",
        },
        "spreadsheet_id": os.getenv(
            "GOOGLE_SPREADSHEET_ID",
            "",
        ).strip(),
        "sheet_name": os.getenv(
            "GOOGLE_SHEET_NAME",
            "Applications",
        ).strip(),
        "credentials_path": Path(
            os.getenv(
                "GOOGLE_CREDENTIALS_PATH",
                (
                    "credentials/"
                    "google-service-account.json"
                ),
            )
        ),
    }


def validate_google_settings(
    settings: dict,
) -> None:
    """
    Validate the required Google Sheets settings.
    """

    if not settings["enabled"]:
        raise ValueError(
            "Google Sheets synchronization is disabled."
        )

    if not settings["spreadsheet_id"]:
        raise ValueError(
            "GOOGLE_SPREADSHEET_ID is missing."
        )

    if not settings["sheet_name"]:
        raise ValueError(
            "GOOGLE_SHEET_NAME is missing."
        )

    credentials_path = settings[
        "credentials_path"
    ]

    if not credentials_path.exists():
        raise FileNotFoundError(
            "Google credentials were not found at: "
            f"{credentials_path.resolve()}"
        )


def get_sheets_service():
    """
    Build an authenticated Google Sheets API service.
    """

    settings = get_google_settings()

    validate_google_settings(
        settings
    )

    credentials = (
        Credentials.from_service_account_file(
            str(settings["credentials_path"]),
            scopes=SCOPES,
        )
    )

    service = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )

    return service


def test_google_sheets_connection() -> dict:
    """
    Test whether the configured spreadsheet can be read.
    """

    settings = get_google_settings()

    try:
        service = get_sheets_service()

        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=(
                    settings["spreadsheet_id"]
                ),
                range=(
                    f"{settings['sheet_name']}!A1:U5"
                ),
            )
            .execute()
        )

        values = result.get(
            "values",
            [],
        )

        return {
            "success": True,
            "message": (
                "Google Sheets connection successful."
            ),
            "rows_read": len(values),
            "sheet_name": settings[
                "sheet_name"
            ],
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error),
            "rows_read": 0,
            "sheet_name": settings.get(
                "sheet_name",
                "",
            ),
        }


def ensure_header_row() -> None:
    """
    Create or correct the header row.
    """

    settings = get_google_settings()
    service = get_sheets_service()

    existing_result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings[
                "spreadsheet_id"
            ],
            range=(
                f"{settings['sheet_name']}!A1:U1"
            ),
        )
        .execute()
    )

    existing_values = existing_result.get(
        "values",
        [],
    )

    current_headers = (
        existing_values[0]
        if existing_values
        else []
    )

    if current_headers == SHEET_HEADERS:
        return

    (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=settings[
                "spreadsheet_id"
            ],
            range=(
                f"{settings['sheet_name']}!A1:U1"
            ),
            valueInputOption="RAW",
            body={
                "values": [
                    SHEET_HEADERS
                ],
            },
        )
        .execute()
    )


def application_to_row(
    application: dict,
) -> list[Any]:
    """
    Convert an application dictionary into one sheet row.
    """

    return [
        application.get(
            "id",
            "",
        ),
        application.get(
            "company",
            "",
        ),
        application.get(
            "job_title",
            "",
        ),
        application.get(
            "location",
            "",
        ),
        application.get(
            "application_date",
            "",
        ),
        application.get(
            "status",
            "",
        ),
        application.get(
            "application_source",
            "",
        ),
        application.get(
            "last_follow_up_date",
            "",
        ),
        application.get(
            "next_follow_up_date",
            "",
        ),
        application.get(
            "job_url",
            "",
        ),
        application.get(
            "contact_name",
            "",
        ),
        application.get(
            "contact_email",
            "",
        ),
        application.get(
            "contact_phone",
            "",
        ),
        application.get(
            "skill_match_score",
            0.0,
        ),
        application.get(
            "ats_score",
            0.0,
        ),
        application.get(
            "overall_match_score",
            0.0,
        ),
        application.get(
            "cv_version",
            "",
        ),
        application.get(
            "cover_letter_version",
            "",
        ),
        application.get(
            "notes",
            "",
        ),
        application.get(
            "created_at",
            "",
        ),
        application.get(
            "updated_at",
            "",
        ),
    ]


def get_sheet_rows() -> list[list]:
    """
    Read all application rows from Google Sheets.
    """

    settings = get_google_settings()
    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings[
                "spreadsheet_id"
            ],
            range=(
                f"{settings['sheet_name']}!A2:U"
            ),
        )
        .execute()
    )

    return result.get(
        "values",
        [],
    )


def find_application_row(
    application_id: int,
) -> int | None:
    """
    Find the Google Sheets row number for a local application ID.

    Sheet row 1 contains headers, so data begins at row 2.
    """

    rows = get_sheet_rows()

    for index, row in enumerate(
        rows,
        start=2,
    ):
        if not row:
            continue

        sheet_id = str(
            row[0]
        ).strip()

        if sheet_id == str(
            application_id
        ):
            return index

    return None


def append_application(
    application: dict,
) -> dict:
    """
    Append one application to Google Sheets.
    """

    settings = get_google_settings()
    service = get_sheets_service()

    row = application_to_row(
        application
    )

    response = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=settings[
                "spreadsheet_id"
            ],
            range=(
                f"{settings['sheet_name']}!A:U"
            ),
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={
                "values": [
                    row
                ],
            },
        )
        .execute()
    )

    updates = response.get(
        "updates",
        {},
    )

    return {
        "action": "created",
        "updated_range": updates.get(
            "updatedRange",
            "",
        ),
    }


def update_sheet_application(
    application: dict,
    row_number: int,
) -> dict:
    """
    Update an existing application row.
    """

    settings = get_google_settings()
    service = get_sheets_service()

    row = application_to_row(
        application
    )

    range_name = (
        f"{settings['sheet_name']}!"
        f"A{row_number}:U{row_number}"
    )

    response = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=settings[
                "spreadsheet_id"
            ],
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={
                "values": [
                    row
                ],
            },
        )
        .execute()
    )

    return {
        "action": "updated",
        "updated_range": response.get(
            "updatedRange",
            range_name,
        ),
    }


def sync_application(
    application: dict,
) -> dict:
    """
    Create or update one application in Google Sheets.

    The local application ID prevents duplicate rows.
    """

    application_id = application.get(
        "id"
    )

    if application_id is None:
        raise ValueError(
            "The application has no local ID."
        )

    ensure_header_row()

    existing_row = find_application_row(
        application_id
    )

    if existing_row is None:
        result = append_application(
            application
        )

    else:
        result = update_sheet_application(
            application=application,
            row_number=existing_row,
        )

    return {
        "success": True,
        "application_id": application_id,
        **result,
    }


def sync_all_applications(
    applications: list[dict],
) -> dict:
    """
    Synchronize every local application.

    Existing rows are updated and missing rows are appended.
    """

    ensure_header_row()

    created_count = 0
    updated_count = 0
    failed_count = 0
    errors = []

    for application in applications:
        try:
            result = sync_application(
                application
            )

            if result["action"] == "created":
                created_count += 1

            elif result["action"] == "updated":
                updated_count += 1

        except Exception as error:
            failed_count += 1

            errors.append(
                {
                    "application_id": (
                        application.get(
                            "id",
                            "",
                        )
                    ),
                    "error": str(error),
                }
            )

    return {
        "success": failed_count == 0,
        "total": len(applications),
        "created": created_count,
        "updated": updated_count,
        "failed": failed_count,
        "errors": errors,
    }