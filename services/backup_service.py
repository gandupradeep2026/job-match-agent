import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from services.job_tracker import (
    DATABASE_PATH,
    create_applications_table,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIRECTORY = PROJECT_ROOT / "backups"

MAX_BACKUP_SIZE_BYTES = 50 * 1024 * 1024

REQUIRED_APPLICATION_COLUMNS = {
    "id",
    "company",
    "job_title",
    "application_date",
    "status",
    "created_at",
}


class BackupError(Exception):
    """
    Raised when a database backup or restoration fails.
    """


def ensure_backup_directory() -> Path:
    """
    Create and return the local backup directory.
    """

    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    return BACKUP_DIRECTORY


def create_backup_filename(
    prefix: str = "applications_backup",
) -> str:
    """
    Create a timestamped SQLite backup filename.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    return f"{prefix}_{timestamp}.db"


def validate_sqlite_database(
    database_path: Path,
) -> dict[str, Any]:
    """
    Validate that a file is a usable SQLite database
    containing the required applications table.
    """

    if not database_path.exists():
        raise BackupError(
            "The database file does not exist."
        )

    if not database_path.is_file():
        raise BackupError(
            "The selected path is not a file."
        )

    file_size = database_path.stat().st_size

    if file_size <= 0:
        raise BackupError(
            "The database file is empty."
        )

    if file_size > MAX_BACKUP_SIZE_BYTES:
        raise BackupError(
            "The database file is larger than the "
            "maximum permitted backup size."
        )

    connection = None

    try:
        connection = sqlite3.connect(
            str(database_path)
        )

        integrity_row = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        integrity_status = (
            integrity_row[0]
            if integrity_row
            else "unknown"
        )

        if (
            str(integrity_status).lower()
            != "ok"
        ):
            raise BackupError(
                "SQLite integrity validation failed: "
                f"{integrity_status}"
            )

        table_row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'applications'
            """
        ).fetchone()

        if table_row is None:
            raise BackupError(
                "The backup does not contain "
                "an applications table."
            )

        column_rows = connection.execute(
            "PRAGMA table_info(applications)"
        ).fetchall()

        available_columns = {
            row[1]
            for row in column_rows
        }

        missing_columns = (
            REQUIRED_APPLICATION_COLUMNS
            - available_columns
        )

        if missing_columns:
            raise BackupError(
                "The applications table is missing "
                "required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        application_count_row = (
            connection.execute(
                """
                SELECT COUNT(*)
                FROM applications
                """
            ).fetchone()
        )

        application_count = (
            int(application_count_row[0])
            if application_count_row
            else 0
        )

    except BackupError:
        raise

    except sqlite3.DatabaseError as error:
        raise BackupError(
            "The selected file is not a valid "
            "SQLite database."
        ) from error

    finally:
        if connection is not None:
            connection.close()

    return {
        "valid": True,
        "path": str(
            database_path.resolve()
        ),
        "size_bytes": file_size,
        "integrity_status": (
            integrity_status
        ),
        "application_count": (
            application_count
        ),
        "columns": sorted(
            available_columns
        ),
    }


def create_database_backup(
    prefix: str = "applications_backup",
) -> dict[str, Any]:
    """
    Create a consistent database backup using
    SQLite's built-in backup API.
    """

    create_applications_table()

    if not DATABASE_PATH.exists():
        raise BackupError(
            "The local application database "
            "could not be found."
        )

    backup_directory = (
        ensure_backup_directory()
    )

    backup_path = (
        backup_directory
        / create_backup_filename(
            prefix=prefix
        )
    )

    source_connection = None
    destination_connection = None

    try:
        source_connection = sqlite3.connect(
            str(DATABASE_PATH)
        )

        destination_connection = (
            sqlite3.connect(
                str(backup_path)
            )
        )

        source_connection.backup(
            destination_connection
        )

    except sqlite3.DatabaseError as error:
        backup_path.unlink(
            missing_ok=True
        )

        raise BackupError(
            "The database backup could not be created."
        ) from error

    finally:
        if destination_connection is not None:
            destination_connection.close()

        if source_connection is not None:
            source_connection.close()

    validation = validate_sqlite_database(
        backup_path
    )

    return {
        "success": True,
        "path": backup_path,
        "filename": backup_path.name,
        "size_bytes": validation[
            "size_bytes"
        ],
        "application_count": validation[
            "application_count"
        ],
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def read_backup_bytes(
    backup_path: Path,
) -> bytes:
    """
    Validate and read one backup file.
    """

    validate_sqlite_database(
        backup_path
    )

    return backup_path.read_bytes()


def list_local_backups() -> list[dict[str, Any]]:
    """
    Return all local backup files, newest first.
    """

    backup_directory = (
        ensure_backup_directory()
    )

    backup_items = []

    for backup_path in backup_directory.glob(
        "*.db"
    ):
        try:
            validation = validate_sqlite_database(
                backup_path
            )

            backup_items.append(
                {
                    "filename": backup_path.name,
                    "path": backup_path,
                    "size_bytes": validation[
                        "size_bytes"
                    ],
                    "application_count": (
                        validation[
                            "application_count"
                        ]
                    ),
                    "modified_at": (
                        datetime.fromtimestamp(
                            backup_path.stat().st_mtime
                        ).isoformat(
                            timespec="seconds"
                        )
                    ),
                    "valid": True,
                    "error": "",
                }
            )

        except Exception as error:
            backup_items.append(
                {
                    "filename": backup_path.name,
                    "path": backup_path,
                    "size_bytes": (
                        backup_path.stat().st_size
                    ),
                    "application_count": 0,
                    "modified_at": (
                        datetime.fromtimestamp(
                            backup_path.stat().st_mtime
                        ).isoformat(
                            timespec="seconds"
                        )
                    ),
                    "valid": False,
                    "error": str(error),
                }
            )

    return sorted(
        backup_items,
        key=lambda item: item[
            "modified_at"
        ],
        reverse=True,
    )


def save_uploaded_backup(
    uploaded_bytes: bytes,
    original_filename: str,
) -> Path:
    """
    Save and validate an uploaded backup file.
    """

    if not uploaded_bytes:
        raise BackupError(
            "The uploaded backup is empty."
        )

    if len(uploaded_bytes) > MAX_BACKUP_SIZE_BYTES:
        raise BackupError(
            "The uploaded backup is too large."
        )

    if not original_filename.lower().endswith(
        (
            ".db",
            ".sqlite",
            ".sqlite3",
        )
    ):
        raise BackupError(
            "Upload a .db, .sqlite or .sqlite3 file."
        )

    backup_directory = (
        ensure_backup_directory()
    )

    temporary_path = (
        backup_directory
        / create_backup_filename(
            prefix="uploaded_restore_candidate"
        )
    )

    temporary_path.write_bytes(
        uploaded_bytes
    )

    try:
        validate_sqlite_database(
            temporary_path
        )

    except Exception:
        temporary_path.unlink(
            missing_ok=True
        )

        raise

    return temporary_path


def restore_database_from_backup(
    backup_path: Path,
) -> dict[str, Any]:
    """
    Restore the active database from a validated backup.

    A safety backup of the current database is created first.
    """

    backup_validation = (
        validate_sqlite_database(
            backup_path
        )
    )

    safety_backup = None

    if DATABASE_PATH.exists():
        safety_backup = (
            create_database_backup(
                prefix="before_restore"
            )
        )

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_restore_path = (
        DATABASE_PATH.parent
        / "applications_restore_temp.db"
    )

    temporary_restore_path.unlink(
        missing_ok=True
    )

    try:
        shutil.copy2(
            backup_path,
            temporary_restore_path,
        )

        validate_sqlite_database(
            temporary_restore_path
        )

        temporary_restore_path.replace(
            DATABASE_PATH
        )

        create_applications_table()

        restored_validation = (
            validate_sqlite_database(
                DATABASE_PATH
            )
        )

    except Exception as error:
        temporary_restore_path.unlink(
            missing_ok=True
        )

        raise BackupError(
            "The database could not be restored."
        ) from error

    return {
        "success": True,
        "restored_from": str(
            backup_path.resolve()
        ),
        "application_count": (
            restored_validation[
                "application_count"
            ]
        ),
        "safety_backup_path": (
            str(
                safety_backup["path"].resolve()
            )
            if safety_backup
            else ""
        ),
        "restored_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "source_validation": (
            backup_validation
        ),
    }


def delete_local_backup(
    backup_path: Path,
) -> bool:
    """
    Delete a backup located inside the backup directory.
    """

    backup_directory = (
        ensure_backup_directory().resolve()
    )

    resolved_path = backup_path.resolve()

    if (
        resolved_path.parent
        != backup_directory
    ):
        raise BackupError(
            "Only files directly inside the backup "
            "directory can be deleted."
        )

    if not resolved_path.exists():
        return False

    resolved_path.unlink()

    return True