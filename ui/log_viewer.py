import streamlit as st

from services.logging_service import (
    clear_log_file,
    get_log_information,
    get_log_text,
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


def render_log_viewer() -> None:
    """
    Display and manage local application logs.
    """

    st.subheader(
        "Application Logs"
    )

    st.caption(
        "Logs contain technical diagnostic information. "
        "CV text, job-description text, credentials and "
        "generated documents are intentionally excluded."
    )

    log_information = (
        get_log_information()
    )

    metric_col1, metric_col2 = (
        st.columns(2)
    )

    with metric_col1:
        st.metric(
            "Log File Size",
            format_file_size(
                log_information[
                    "size_bytes"
                ]
            ),
        )

    with metric_col2:
        st.metric(
            "Rotating Backups",
            log_information[
                "backup_count"
            ],
        )

    with st.expander(
        "Log file location"
    ):
        st.code(
            log_information[
                "path"
            ]
        )

    line_limit = st.select_slider(
        "Number of recent lines",
        options=[
            50,
            100,
            200,
            300,
            500,
            1000,
        ],
        value=300,
        key="log_viewer_line_limit",
    )

    log_text = get_log_text(
        line_limit=line_limit
    )

    if log_text:
        st.text_area(
            "Recent application logs",
            value=log_text,
            height=500,
            disabled=True,
            key="application_log_display",
        )

    else:
        st.info(
            "The active log file is currently empty."
        )

    action_col1, action_col2 = (
        st.columns(2)
    )

    with action_col1:
        st.download_button(
            label="Download Logs",
            data=log_text.encode(
                "utf-8"
            ),
            file_name=(
                "job_match_agent_logs.txt"
            ),
            mime="text/plain",
            width="stretch",
            key="download_application_logs",
        )

    with action_col2:
        confirm_clear = st.checkbox(
            "Allow log deletion",
            value=False,
            key="confirm_clear_logs",
        )

        if st.button(
            "Clear Active Log",
            width="stretch",
            disabled=not confirm_clear,
            key="clear_application_logs",
        ):
            try:
                clear_log_file()

                st.success(
                    "The active log file was cleared."
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "The log file could not be cleared."
                )

                st.code(
                    f"{type(error).__name__}: {error}"
                )