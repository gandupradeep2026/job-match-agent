import json
import os
import platform
import sqlite3
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv, set_key
from ollama import list as list_models
from ollama import ps

from services.job_tracker import (
    DATABASE_PATH,
    get_all_applications,
)
from services.sheets import (
    get_google_settings,
    test_google_sheets_connection,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


REQUIRED_PROJECT_FILES = [
    "app.py",
    "requirements.txt",
    ".env",
    "parsers/cv_parser.py",
    "parsers/job_parser.py",
    "services/analysis_service.py",
    "services/local_ai_service.py",
    "services/job_tracker.py",
    "services/sheets.py",
    "ui/analysis_results.py",
    "ui/application_form.py",
    "ui/tracker_view.py",
    "ui/dashboard.py",
]


def load_settings() -> dict[str, Any]:
    """
    Load application settings from the .env file.
    """

    load_dotenv(
        dotenv_path=ENV_PATH,
        override=True,
    )

    return {
        "ollama_model": os.getenv(
            "OLLAMA_MODEL",
            "llama3.2",
        ).strip(),
        "google_sheets_enabled": os.getenv(
            "GOOGLE_SHEETS_ENABLED",
            "false",
        ).strip().lower()
        in {
            "true",
            "1",
            "yes",
            "on",
        },
        "google_spreadsheet_id": os.getenv(
            "GOOGLE_SPREADSHEET_ID",
            "",
        ).strip(),
        "google_sheet_name": os.getenv(
            "GOOGLE_SHEET_NAME",
            "Applications",
        ).strip(),
        "google_credentials_path": os.getenv(
            "GOOGLE_CREDENTIALS_PATH",
            (
                "credentials/"
                "google-service-account.json"
            ),
        ).strip(),
    }


def save_ollama_model(
    model_name: str,
) -> None:
    """
    Save the selected Ollama model inside .env.
    """

    cleaned_model_name = model_name.strip()

    if not cleaned_model_name:
        raise ValueError(
            "The Ollama model name cannot be empty."
        )

    if not ENV_PATH.exists():
        ENV_PATH.touch()

    set_key(
        dotenv_path=str(ENV_PATH),
        key_to_set="OLLAMA_MODEL",
        value_to_set=cleaned_model_name,
        quote_mode="never",
    )

    os.environ[
        "OLLAMA_MODEL"
    ] = cleaned_model_name


def get_ollama_models() -> list[str]:
    """
    Return the names of locally installed Ollama models.
    """

    response = list_models()

    installed_models = []

    models = getattr(
        response,
        "models",
        [],
    )

    for model in models:
        model_name = getattr(
            model,
            "model",
            "",
        )

        if not model_name:
            model_name = getattr(
                model,
                "name",
                "",
            )

        if model_name:
            installed_models.append(
                str(model_name)
            )

    return sorted(
        set(installed_models)
    )


def test_ollama_connection(
    model_name: str,
) -> dict[str, Any]:
    """
    Test whether Ollama is running and the selected model exists.
    """

    try:
        installed_models = get_ollama_models()

        model_available = any(
            installed_model == model_name
            or installed_model.startswith(
                f"{model_name}:"
            )
            or model_name.startswith(
                f"{installed_model}:"
            )
            for installed_model in installed_models
        )

        running_response = ps()

        running_models = []

        for model in getattr(
            running_response,
            "models",
            [],
        ):
            running_name = getattr(
                model,
                "model",
                "",
            )

            if not running_name:
                running_name = getattr(
                    model,
                    "name",
                    "",
                )

            if running_name:
                running_models.append(
                    str(running_name)
                )

        if not model_available:
            return {
                "success": False,
                "message": (
                    f"The model '{model_name}' is not "
                    "installed in Ollama."
                ),
                "installed_models": installed_models,
                "running_models": running_models,
            }

        return {
            "success": True,
            "message": (
                "Ollama is available and the selected "
                "model is installed."
            ),
            "installed_models": installed_models,
            "running_models": running_models,
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error),
            "installed_models": [],
            "running_models": [],
        }


def get_database_health() -> dict[str, Any]:
    """
    Check whether the SQLite database is usable.
    """

    try:
        applications = get_all_applications()

        absolute_database_path = (
            DATABASE_PATH.resolve()
        )

        database_exists = (
            DATABASE_PATH.exists()
        )

        database_size = (
            DATABASE_PATH.stat().st_size
            if database_exists
            else 0
        )

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        try:
            integrity_result = (
                connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()
            )

        finally:
            connection.close()

        integrity_status = (
            integrity_result[0]
            if integrity_result
            else "Unknown"
        )

        return {
            "success": (
                integrity_status.lower()
                == "ok"
            ),
            "path": str(
                absolute_database_path
            ),
            "exists": database_exists,
            "size_bytes": database_size,
            "application_count": len(
                applications
            ),
            "integrity_status": (
                integrity_status
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "path": str(
                DATABASE_PATH.resolve()
            ),
            "exists": (
                DATABASE_PATH.exists()
            ),
            "size_bytes": 0,
            "application_count": 0,
            "integrity_status": (
                f"Error: {error}"
            ),
        }


def check_required_files() -> list[dict[str, Any]]:
    """
    Check whether important project files exist.
    """

    results = []

    for relative_path in REQUIRED_PROJECT_FILES:
        full_path = (
            PROJECT_ROOT
            / relative_path
        )

        results.append(
            {
                "file": relative_path,
                "exists": full_path.exists(),
                "absolute_path": str(
                    full_path
                ),
            }
        )

    return results


def get_python_information() -> dict[str, str]:
    """
    Return basic Python and operating-system details.
    """

    return {
        "python_version": (
            sys.version.split()[0]
        ),
        "python_executable": (
            sys.executable
        ),
        "operating_system": (
            platform.platform()
        ),
        "machine": (
            platform.machine()
        ),
        "project_root": str(
            PROJECT_ROOT
        ),
    }


def get_google_health() -> dict[str, Any]:
    """
    Return Google configuration and connection information.
    """

    settings = get_google_settings()

    configuration = {
        "enabled": settings[
            "enabled"
        ],
        "sheet_name": settings[
            "sheet_name"
        ],
        "spreadsheet_id_present": bool(
            settings[
                "spreadsheet_id"
            ]
        ),
        "credentials_path": str(
            settings[
                "credentials_path"
            ]
        ),
        "credentials_exist": (
            settings[
                "credentials_path"
            ].exists()
        ),
    }

    if not settings["enabled"]:
        return {
            "success": False,
            "configured": False,
            "message": (
                "Google Sheets synchronization "
                "is disabled."
            ),
            "configuration": configuration,
        }

    result = (
        test_google_sheets_connection()
    )

    return {
        "success": result[
            "success"
        ],
        "configured": True,
        "message": result[
            "message"
        ],
        "rows_read": result.get(
            "rows_read",
            0,
        ),
        "configuration": configuration,
    }


def run_complete_health_check() -> dict[str, Any]:
    """
    Run all system-health tests.
    """

    settings = load_settings()

    ollama_result = (
        test_ollama_connection(
            settings[
                "ollama_model"
            ]
        )
    )

    database_result = (
        get_database_health()
    )

    google_result = (
        get_google_health()
    )

    file_results = (
        check_required_files()
    )

    missing_files = [
        result["file"]
        for result in file_results
        if not result["exists"]
    ]

    files_success = (
        len(missing_files) == 0
    )

    essential_success = (
        ollama_result["success"]
        and database_result["success"]
        and files_success
    )

    return {
        "overall_success": (
            essential_success
        ),
        "ollama": ollama_result,
        "database": database_result,
        "google": google_result,
        "files": file_results,
        "missing_files": missing_files,
        "python": (
            get_python_information()
        ),
    }


def export_health_report(
    health_result: dict[str, Any],
) -> str:
    """
    Convert health-check results to formatted JSON.
    """

    return json.dumps(
        health_result,
        indent=2,
        ensure_ascii=False,
        default=str,
    )