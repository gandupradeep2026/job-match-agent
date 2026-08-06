import streamlit as st

from services.settings_service import (
    check_required_files,
    export_health_report,
    get_database_health,
    get_google_health,
    get_ollama_models,
    get_python_information,
    load_settings,
    run_complete_health_check,
    save_ollama_model,
    test_ollama_connection,
)
from ui.backup_restore import (
    render_backup_restore,
)
from ui.log_viewer import (
    render_log_viewer,
)


def format_file_size(
    size_bytes: int,
) -> str:
    """
    Convert bytes into a readable value.
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


def render_ollama_settings() -> None:
    """
    Display Ollama model settings and health controls.
    """

    st.subheader(
        "Local AI — Ollama"
    )

    settings = load_settings()

    current_model = settings[
        "ollama_model"
    ]

    try:
        installed_models = (
            get_ollama_models()
        )

    except Exception as error:
        installed_models = []

        st.error(
            "Could not retrieve Ollama models."
        )

        st.code(
            str(error)
        )

    model_options = (
        installed_models.copy()
    )

    if (
        current_model
        and current_model
        not in model_options
    ):
        model_options.insert(
            0,
            current_model,
        )

    if not model_options:
        model_options = [
            current_model
            or "llama3.2"
        ]

    current_index = (
        model_options.index(
            current_model
        )
        if current_model
        in model_options
        else 0
    )

    selected_model = st.selectbox(
        "Selected Ollama model",
        options=model_options,
        index=current_index,
        key="settings_ollama_model",
    )

    button_col1, button_col2 = (
        st.columns(2)
    )

    with button_col1:
        if st.button(
            "Save Model Setting",
            width="stretch",
            key="save_ollama_setting",
        ):
            try:
                save_ollama_model(
                    selected_model
                )

                st.success(
                    "Ollama model setting saved."
                )

            except Exception as error:
                st.error(
                    "The model setting could not be saved."
                )

                st.code(
                    str(error)
                )

    with button_col2:
        if st.button(
            "Test Ollama",
            width="stretch",
            key="test_ollama_settings",
        ):
            with st.spinner(
                "Testing Ollama..."
            ):
                result = (
                    test_ollama_connection(
                        selected_model
                    )
                )

            st.session_state[
                "settings_ollama_result"
            ] = result

    ollama_result = (
        st.session_state.get(
            "settings_ollama_result"
        )
    )

    if not ollama_result:
        return

    if ollama_result[
        "success"
    ]:
        st.success(
            ollama_result[
                "message"
            ]
        )

    else:
        st.error(
            ollama_result[
                "message"
            ]
        )

    installed = ollama_result.get(
        "installed_models",
        [],
    )

    running = ollama_result.get(
        "running_models",
        [],
    )

    with st.expander(
        "Ollama model information"
    ):
        st.write(
            "**Installed models:**"
        )

        if installed:
            for model in installed:
                st.write(
                    f"- {model}"
                )

        else:
            st.write(
                "No installed models were detected."
            )

        st.write(
            "**Models currently loaded:**"
        )

        if running:
            for model in running:
                st.write(
                    f"- {model}"
                )

        else:
            st.write(
                "No model is currently loaded. "
                "This is normal when Ollama is idle."
            )


def render_database_health() -> None:
    """
    Display SQLite database health.
    """

    st.subheader(
        "Local Database"
    )

    result = get_database_health()

    metric_col1, metric_col2 = (
        st.columns(2)
    )

    with metric_col1:
        st.metric(
            "Saved Applications",
            result[
                "application_count"
            ],
        )

    with metric_col2:
        st.metric(
            "Database Size",
            format_file_size(
                result[
                    "size_bytes"
                ]
            ),
        )

    if result["success"]:
        st.success(
            "SQLite database integrity check passed."
        )

    else:
        st.error(
            "SQLite database integrity check failed."
        )

    st.write(
        f"**Integrity status:** "
        f"{result['integrity_status']}"
    )

    with st.expander(
        "Database location"
    ):
        st.code(
            result["path"]
        )


def render_google_health() -> None:
    """
    Display Google Sheets configuration and health.
    """

    st.subheader(
        "Google Sheets"
    )

    if st.button(
        "Test Google Sheets",
        width="stretch",
        key="settings_test_google",
    ):
        with st.spinner(
            "Testing Google Sheets..."
        ):
            result = get_google_health()

        st.session_state[
            "settings_google_result"
        ] = result

    result = st.session_state.get(
        "settings_google_result"
    )

    if not result:
        result = get_google_health()

    configuration = result.get(
        "configuration",
        {},
    )

    config_col1, config_col2 = (
        st.columns(2)
    )

    with config_col1:
        st.write(
            "**Synchronization enabled:** "
            f"{'Yes' if configuration.get('enabled') else 'No'}"
        )

        st.write(
            "**Spreadsheet ID configured:** "
            f"{'Yes' if configuration.get('spreadsheet_id_present') else 'No'}"
        )

    with config_col2:
        st.write(
            "**Credentials found:** "
            f"{'Yes' if configuration.get('credentials_exist') else 'No'}"
        )

        st.write(
            "**Sheet name:** "
            f"{configuration.get('sheet_name', '')}"
        )

    if result["success"]:
        st.success(
            result["message"]
        )

    elif configuration.get(
        "enabled"
    ):
        st.error(
            result["message"]
        )

    else:
        st.info(
            result["message"]
        )

    with st.expander(
        "Google credentials location"
    ):
        st.code(
            configuration.get(
                "credentials_path",
                "",
            )
        )


def render_file_health() -> None:
    """
    Display required project-file status.
    """

    st.subheader(
        "Project Files"
    )

    results = check_required_files()

    existing_count = sum(
        result["exists"]
        for result in results
    )

    st.write(
        f"{existing_count} of "
        f"{len(results)} required files found."
    )

    missing_files = [
        result
        for result in results
        if not result["exists"]
    ]

    if not missing_files:
        st.success(
            "All required project files were found."
        )

    else:
        st.error(
            f"{len(missing_files)} required "
            "file(s) are missing."
        )

    with st.expander(
        "Show project-file checks"
    ):
        for result in results:
            status = (
                "✓"
                if result["exists"]
                else "✗"
            )

            st.write(
                f"{status} {result['file']}"
            )


def render_python_information() -> None:
    """
    Display Python and operating-system information.
    """

    st.subheader(
        "Runtime Information"
    )

    information = (
        get_python_information()
    )

    st.write(
        f"**Python version:** "
        f"{information['python_version']}"
    )

    st.write(
        f"**Operating system:** "
        f"{information['operating_system']}"
    )

    st.write(
        f"**Machine:** "
        f"{information['machine']}"
    )

    with st.expander(
        "Show runtime paths"
    ):
        st.write(
            "**Python executable:**"
        )

        st.code(
            information[
                "python_executable"
            ]
        )

        st.write(
            "**Project root:**"
        )

        st.code(
            information[
                "project_root"
            ]
        )


def render_complete_health_check() -> None:
    """
    Display complete system-health controls.
    """

    st.divider()

    st.subheader(
        "Complete System Test"
    )

    if st.button(
        "Run Complete Health Check",
        type="primary",
        width="stretch",
        key="run_complete_health_check",
    ):
        with st.spinner(
            "Testing Ollama, SQLite, Google "
            "Sheets and project files..."
        ):
            result = (
                run_complete_health_check()
            )

        st.session_state[
            "complete_health_result"
        ] = result

    result = st.session_state.get(
        "complete_health_result"
    )

    if not result:
        return

    if result[
        "overall_success"
    ]:
        st.success(
            "All essential systems are healthy."
        )

    else:
        st.error(
            "One or more essential systems need attention."
        )

    health_col1, health_col2, health_col3 = (
        st.columns(3)
    )

    with health_col1:
        st.metric(
            "Ollama",
            (
                "Healthy"
                if result[
                    "ollama"
                ][
                    "success"
                ]
                else "Problem"
            ),
        )

    with health_col2:
        st.metric(
            "SQLite",
            (
                "Healthy"
                if result[
                    "database"
                ][
                    "success"
                ]
                else "Problem"
            ),
        )

    with health_col3:
        google_configuration = result[
            "google"
        ].get(
            "configuration",
            {},
        )

        if not google_configuration.get(
            "enabled"
        ):
            google_status = "Disabled"

        elif result[
            "google"
        ][
            "success"
        ]:
            google_status = "Healthy"

        else:
            google_status = "Problem"

        st.metric(
            "Google Sheets",
            google_status,
        )

    report_text = export_health_report(
        result
    )

    st.download_button(
        label="Download Health Report",
        data=report_text.encode(
            "utf-8"
        ),
        file_name=(
            "job_match_agent_health_report.json"
        ),
        mime="application/json",
        width="stretch",
        key="download_health_report",
    )

    with st.expander(
        "Show complete diagnostic report"
    ):
        st.code(
            report_text,
            language="json",
        )


def render_settings_page() -> None:
    """
    Render settings, health, backups and logs.
    """

    st.header(
        "Settings and System Health"
    )

    st.caption(
        "Configure the local AI model, test services, "
        "manage database backups and inspect logs."
    )

    (
        settings_tab,
        health_tab,
        backup_tab,
        logs_tab,
    ) = st.tabs(
        [
            "Settings",
            "System Health",
            "Backup and Restore",
            "Logs",
        ]
    )

    with settings_tab:
        render_ollama_settings()

        st.divider()

        st.info(
            "Model changes are saved in the .env file. "
            "New AI requests use the selected model."
        )

    with health_tab:
        health_col1, health_col2 = (
            st.columns(2)
        )

        with health_col1:
            render_database_health()

            st.divider()

            render_file_health()

        with health_col2:
            render_google_health()

            st.divider()

            render_python_information()

        render_complete_health_check()

    with backup_tab:
        render_backup_restore()

    with logs_tab:
        render_log_viewer()