from pathlib import Path

import pandas as pd
import streamlit as st

from services.backup_service import (
    create_database_backup,
    delete_local_backup,
    list_local_backups,
    read_backup_bytes,
    restore_database_from_backup,
    save_uploaded_backup,
    validate_sqlite_database,
)
from services.logging_service import (
    get_logger,
    log_event,
    log_exception,
)


logger = get_logger(
    "backup_restore"
)


def format_file_size(
    size_bytes: int,
) -> str:
    """
    Convert bytes into a readable file size.
    """

    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    if size_bytes < 1024**2:
        return (
            f"{size_bytes / 1024:.1f} KB"
        )

    return (
        f"{size_bytes / (1024**2):.1f} MB"
    )


def render_create_backup() -> None:
    """
    Display backup creation and download controls.
    """

    st.subheader(
        "Create Database Backup"
    )

    st.write(
        "Create a complete copy of your local "
        "application tracker."
    )

    st.info(
        "The backup contains application details, "
        "statuses, scores, notes, contacts and "
        "follow-up information."
    )

    if st.button(
        "Create New Backup",
        type="primary",
        width="stretch",
        key="create_database_backup",
    ):
        try:
            with st.spinner(
                "Creating and validating the database backup..."
            ):
                backup_result = (
                    create_database_backup()
                )

            st.session_state[
                "latest_database_backup"
            ] = {
                "path": str(
                    backup_result["path"]
                ),
                "filename": (
                    backup_result["filename"]
                ),
                "size_bytes": (
                    backup_result[
                        "size_bytes"
                    ]
                ),
                "application_count": (
                    backup_result[
                        "application_count"
                    ]
                ),
            }

            log_event(
                logger=logger,
                message=(
                    "Database backup created."
                ),
                context={
                    "filename": (
                        backup_result[
                            "filename"
                        ]
                    ),
                    "application_count": (
                        backup_result[
                            "application_count"
                        ]
                    ),
                },
            )

            st.success(
                "The database backup was created successfully."
            )

        except Exception as error:
            log_exception(
                logger=logger,
                error=error,
                message=(
                    "Database backup creation failed."
                ),
            )

            st.error(
                "The database backup could not be created."
            )

            st.code(
                f"{type(error).__name__}: {error}"
            )

    latest_backup = st.session_state.get(
        "latest_database_backup"
    )

    if not latest_backup:
        return

    latest_backup_path = Path(
        latest_backup["path"]
    )

    if not latest_backup_path.exists():
        st.warning(
            "The latest backup file is no longer available."
        )

        return

    metric_col1, metric_col2 = (
        st.columns(2)
    )

    with metric_col1:
        st.metric(
            "Applications",
            latest_backup[
                "application_count"
            ],
        )

    with metric_col2:
        st.metric(
            "Backup Size",
            format_file_size(
                latest_backup[
                    "size_bytes"
                ]
            ),
        )

    try:
        backup_bytes = read_backup_bytes(
            latest_backup_path
        )

        st.download_button(
            label="Download Latest Backup",
            data=backup_bytes,
            file_name=latest_backup[
                "filename"
            ],
            mime="application/x-sqlite3",
            width="stretch",
            key="download_latest_database_backup",
        )

    except Exception as error:
        st.error(
            "The latest backup could not be prepared "
            "for downloading."
        )

        st.code(
            f"{type(error).__name__}: {error}"
        )


def render_upload_restore() -> None:
    """
    Display uploaded backup validation and restore controls.
    """

    st.subheader(
        "Restore an Uploaded Backup"
    )

    st.warning(
        "Restoring replaces the active local tracker. "
        "The app automatically creates a safety backup "
        "before restoration."
    )

    uploaded_backup = st.file_uploader(
        "Upload SQLite backup",
        type=[
            "db",
            "sqlite",
            "sqlite3",
        ],
        key="uploaded_database_backup",
    )

    uploaded_signature = None

    if uploaded_backup is not None:
        uploaded_bytes = (
            uploaded_backup.getvalue()
        )

        uploaded_signature = (
            uploaded_backup.name,
            len(uploaded_bytes),
        )

        previous_signature = (
            st.session_state.get(
                "validated_restore_signature"
            )
        )

        if (
            uploaded_signature
            != previous_signature
        ):
            try:
                uploaded_path = (
                    save_uploaded_backup(
                        uploaded_bytes=(
                            uploaded_bytes
                        ),
                        original_filename=(
                            uploaded_backup.name
                        ),
                    )
                )

                validation = (
                    validate_sqlite_database(
                        uploaded_path
                    )
                )

                old_path = st.session_state.get(
                    "validated_restore_path"
                )

                if old_path:
                    old_path_object = Path(
                        old_path
                    )

                    if (
                        old_path_object.exists()
                        and old_path_object
                        != uploaded_path
                    ):
                        old_path_object.unlink(
                            missing_ok=True
                        )

                st.session_state[
                    "validated_restore_path"
                ] = str(
                    uploaded_path
                )

                st.session_state[
                    "validated_restore_signature"
                ] = uploaded_signature

                st.session_state[
                    "validated_restore_details"
                ] = validation

            except Exception as error:
                st.session_state.pop(
                    "validated_restore_path",
                    None,
                )

                st.session_state.pop(
                    "validated_restore_signature",
                    None,
                )

                st.session_state.pop(
                    "validated_restore_details",
                    None,
                )

                st.error(
                    "The uploaded file is not a valid "
                    "application database backup."
                )

                st.code(
                    f"{type(error).__name__}: {error}"
                )

    validation = st.session_state.get(
        "validated_restore_details"
    )

    validated_restore_path = (
        st.session_state.get(
            "validated_restore_path"
        )
    )

    if not validation or not validated_restore_path:
        return

    st.success(
        "The uploaded backup passed validation."
    )

    metric_col1, metric_col2 = (
        st.columns(2)
    )

    with metric_col1:
        st.metric(
            "Applications in Backup",
            validation[
                "application_count"
            ],
        )

    with metric_col2:
        st.metric(
            "Backup Size",
            format_file_size(
                validation[
                    "size_bytes"
                ]
            ),
        )

    with st.expander(
        "Backup validation details"
    ):
        st.write(
            f"**Integrity status:** "
            f"{validation['integrity_status']}"
        )

        st.write(
            f"**Detected columns:** "
            f"{len(validation['columns'])}"
        )

    confirm_restore = st.checkbox(
        (
            "I understand that restoration replaces "
            "the current application tracker"
        ),
        value=False,
        key="confirm_database_restore",
    )

    if st.button(
        "Restore Uploaded Backup",
        type="primary",
        width="stretch",
        disabled=not confirm_restore,
        key="restore_uploaded_database_backup",
    ):
        try:
            restore_path = Path(
                validated_restore_path
            )

            with st.spinner(
                "Creating a safety backup and restoring "
                "the uploaded database..."
            ):
                restore_result = (
                    restore_database_from_backup(
                        restore_path
                    )
                )

            log_event(
                logger=logger,
                message=(
                    "Database restored from backup."
                ),
                context={
                    "application_count": (
                        restore_result[
                            "application_count"
                        ]
                    ),
                    "safety_backup_created": bool(
                        restore_result[
                            "safety_backup_path"
                        ]
                    ),
                },
            )

            st.session_state[
                "database_restore_message"
            ] = (
                "Database restored successfully. "
                f"{restore_result['application_count']} "
                "application(s) are available."
            )

            restore_path.unlink(
                missing_ok=True
            )

            st.session_state.pop(
                "validated_restore_path",
                None,
            )

            st.session_state.pop(
                "validated_restore_signature",
                None,
            )

            st.session_state.pop(
                "validated_restore_details",
                None,
            )

            st.rerun()

        except Exception as error:
            log_exception(
                logger=logger,
                error=error,
                message=(
                    "Database restoration failed."
                ),
            )

            st.error(
                "The database could not be restored."
            )

            st.code(
                f"{type(error).__name__}: {error}"
            )


def render_local_backups() -> None:
    """
    Display locally created backup files.
    """

    st.subheader(
        "Local Backup History"
    )

    backups = list_local_backups()

    if not backups:
        st.info(
            "No local database backups are available."
        )

        return

    display_rows = []

    for backup in backups:
        display_rows.append(
            {
                "Filename": (
                    backup["filename"]
                ),
                "Applications": (
                    backup[
                        "application_count"
                    ]
                ),
                "Size": format_file_size(
                    backup["size_bytes"]
                ),
                "Modified": (
                    backup["modified_at"]
                ),
                "Valid": (
                    "Yes"
                    if backup["valid"]
                    else "No"
                ),
                "Error": backup[
                    "error"
                ],
            }
        )

    st.dataframe(
        pd.DataFrame(
            display_rows
        ),
        hide_index=True,
        width="stretch",
    )

    valid_backups = [
        backup
        for backup in backups
        if backup["valid"]
    ]

    if not valid_backups:
        st.warning(
            "No valid local backups are available."
        )

        return

    backup_options = {
        backup["filename"]: backup
        for backup in valid_backups
    }

    selected_filename = st.selectbox(
        "Select a local backup",
        options=list(
            backup_options.keys()
        ),
        key="selected_local_database_backup",
    )

    selected_backup = backup_options[
        selected_filename
    ]

    selected_path = selected_backup[
        "path"
    ]

    selected_col1, selected_col2 = (
        st.columns(2)
    )

    with selected_col1:
        st.metric(
            "Applications",
            selected_backup[
                "application_count"
            ],
        )

    with selected_col2:
        st.metric(
            "Size",
            format_file_size(
                selected_backup[
                    "size_bytes"
                ]
            ),
        )

    try:
        selected_bytes = (
            read_backup_bytes(
                selected_path
            )
        )

        st.download_button(
            label="Download Selected Backup",
            data=selected_bytes,
            file_name=selected_filename,
            mime="application/x-sqlite3",
            width="stretch",
            key="download_selected_database_backup",
        )

    except Exception as error:
        st.error(
            "The selected backup could not be downloaded."
        )

        st.code(
            f"{type(error).__name__}: {error}"
        )

    st.write(
        "### Delete local backup"
    )

    st.warning(
        "Deleting a backup is permanent."
    )

    confirm_delete = st.checkbox(
        (
            "I understand that the selected backup "
            "will be permanently deleted"
        ),
        value=False,
        key="confirm_delete_local_backup",
    )

    if st.button(
        "Delete Selected Backup",
        width="stretch",
        disabled=not confirm_delete,
        key="delete_selected_local_backup",
    ):
        try:
            deleted = delete_local_backup(
                selected_path
            )

            if deleted:
                log_event(
                    logger=logger,
                    message=(
                        "Local database backup deleted."
                    ),
                    context={
                        "filename": (
                            selected_filename
                        ),
                    },
                )

                st.success(
                    "The selected backup was deleted."
                )

                st.rerun()

            else:
                st.warning(
                    "The selected backup no longer exists."
                )

        except Exception as error:
            log_exception(
                logger=logger,
                error=error,
                message=(
                    "Local backup deletion failed."
                ),
                context={
                    "filename": (
                        selected_filename
                    ),
                },
            )

            st.error(
                "The backup could not be deleted."
            )

            st.code(
                f"{type(error).__name__}: {error}"
            )


def render_backup_restore() -> None:
    """
    Render complete backup and restore controls.
    """

    restore_message = st.session_state.pop(
        "database_restore_message",
        None,
    )

    if restore_message:
        st.success(
            restore_message
        )

    create_tab, restore_tab, history_tab = (
        st.tabs(
            [
                "Create Backup",
                "Restore Backup",
                "Backup History",
            ]
        )
    )

    with create_tab:
        render_create_backup()

    with restore_tab:
        render_upload_restore()

    with history_tab:
        render_local_backups()