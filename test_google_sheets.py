import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def main() -> None:
    """
    Test whether the service account can access
    the configured Google spreadsheet.
    """

    load_dotenv()

    spreadsheet_id = os.getenv(
        "GOOGLE_SPREADSHEET_ID",
        "",
    ).strip()

    sheet_name = os.getenv(
        "GOOGLE_SHEET_NAME",
        "Applications",
    ).strip()

    credentials_path = Path(
        os.getenv(
            "GOOGLE_CREDENTIALS_PATH",
            "credentials/google-service-account.json",
        )
    )

    if not spreadsheet_id:
        print(
            "ERROR: GOOGLE_SPREADSHEET_ID "
            "is missing from .env."
        )
        sys.exit(1)

    if not sheet_name:
        print(
            "ERROR: GOOGLE_SHEET_NAME "
            "is missing from .env."
        )
        sys.exit(1)

    if not credentials_path.exists():
        print(
            "ERROR: Google credentials file "
            "was not found."
        )
        print(
            f"Expected location: "
            f"{credentials_path.resolve()}"
        )
        sys.exit(1)

    try:
        credentials = (
            Credentials.from_service_account_file(
                credentials_path,
                scopes=SCOPES,
            )
        )

        service = build(
            "sheets",
            "v4",
            credentials=credentials,
        )

        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:U5",
            )
            .execute()
        )

        values = result.get(
            "values",
            [],
        )

        print(
            "Google Sheets connection successful."
        )

        print(
            f"Sheet name: {sheet_name}"
        )

        print(
            f"Rows read: {len(values)}"
        )

        if values:
            print(
                "First row:"
            )

            print(
                values[0]
            )
        else:
            print(
                "The sheet is accessible but currently empty."
            )

    except HttpError as error:
        print(
            "Google Sheets connection failed."
        )

        print(
            f"HTTP error: {error}"
        )

        print(
            "Check that:"
        )

        print(
            "1. The Google Sheets API is enabled."
        )

        print(
            "2. The spreadsheet ID is correct."
        )

        print(
            "3. The spreadsheet is shared with "
            "the service-account email as Editor."
        )

        sys.exit(1)

    except Exception as error:
        print(
            "Google Sheets connection failed."
        )

        print(
            f"Error type: "
            f"{type(error).__name__}"
        )

        print(
            f"Error details: {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()