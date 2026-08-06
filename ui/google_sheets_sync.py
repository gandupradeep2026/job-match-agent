import streamlit as st

from services.job_tracker import (
    get_all_applications,
)
from services.sheets import (
    get_google_settings,
    sync_all_applications,
    sync_application,
    test_google_sheets_connection,
)


def build_application_options(
    applications: list[dict],
) -> dict[str, int]:
    """
    Create readable select-box options.
    """

    return {
        (
            f"ID {application['id']} — "
            f"{application['company']} — "
            f"{application['job_title']}"
        ): application["id"]
        for application in applications
    }


def render_connection_status() -> None:
    """
    Display Google Sheets configuration status.
    """

    settings = get_google_settings()

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        enabled_status = (
            "Enabled"
            if settings["enabled"]
            else "Disabled"
        )

        st.write(
            f"**Google Sheets:** "
            f"{enabled_status}"
        )

    with status_col2:
        st.write(
            f"**Sheet name:** "
            f"{settings['sheet_name']}"
        )


def render_google_sheets_sync(
    component_key: str = "main",
) -> None:
    """
    Display Google Sheets synchronization controls.
    """

    st.divider()
    st.header(
        "Google Sheets Synchronization"
    )

    st.caption(
        "SQLite remains the primary local database. "
        "Google Sheets is an optional synchronized copy."
    )

    render_connection_status()

    connection_key = (
        f"google_connection_result_"
        f"{component_key}"
    )

    if st.button(
        "Test Google Sheets Connection",
        use_container_width=True,
        key=(
            f"test_google_connection_"
            f"{component_key}"
        ),
    ):
        with st.spinner(
            "Testing Google Sheets connection..."
        ):
            result = (
                test_google_sheets_connection()
            )

        st.session_state[
            connection_key
        ] = result

    connection_result = (
        st.session_state.get(
            connection_key
        )
    )

    if connection_result:
        if connection_result[
            "success"
        ]:
            st.success(
                connection_result[
                    "message"
                ]
            )

            st.write(
                f"Rows read: "
                f"{connection_result['rows_read']}"
            )

        else:
            st.error(
                "Google Sheets connection failed."
            )

            st.code(
                connection_result[
                    "message"
                ]
            )

    applications = get_all_applications()

    if not applications:
        st.info(
            "There are no local applications to synchronize."
        )
        return

    st.subheader(
        "Synchronize One Application"
    )

    application_options = (
        build_application_options(
            applications
        )
    )

    selected_label = st.selectbox(
        "Select a local application",
        options=list(
            application_options.keys()
        ),
        key=(
            f"google_sync_application_"
            f"{component_key}"
        ),
    )

    selected_application_id = (
        application_options[
            selected_label
        ]
    )

    selected_application = next(
        (
            application
            for application in applications
            if application["id"]
            == selected_application_id
        ),
        None,
    )

    if st.button(
        "Sync Selected Application",
        type="primary",
        use_container_width=True,
        key=(
            f"sync_selected_google_"
            f"{component_key}"
        ),
    ):
        if selected_application is None:
            st.error(
                "The selected application could not be found."
            )

        else:
            try:
                with st.spinner(
                    "Synchronizing the selected application..."
                ):
                    result = sync_application(
                        selected_application
                    )

                if result["action"] == "created":
                    st.success(
                        "Application added to Google Sheets."
                    )

                else:
                    st.success(
                        "Existing Google Sheets row updated."
                    )

                st.write(
                    f"Application ID: "
                    f"{result['application_id']}"
                )

            except Exception as error:
                st.error(
                    "Synchronization failed."
                )

                st.code(
                    str(error)
                )

    st.subheader(
        "Synchronize All Applications"
    )

    st.write(
        f"{len(applications)} local application(s) "
        "are available."
    )

    confirm_sync_all = st.checkbox(
        (
            "I want to synchronize all local "
            "applications with Google Sheets."
        ),
        key=(
            f"confirm_google_sync_all_"
            f"{component_key}"
        ),
    )

    if st.button(
        "Sync All Applications",
        use_container_width=True,
        disabled=not confirm_sync_all,
        key=(
            f"sync_all_google_"
            f"{component_key}"
        ),
    ):
        try:
            with st.spinner(
                "Synchronizing all applications..."
            ):
                result = sync_all_applications(
                    applications
                )

            result_col1, result_col2, result_col3 = (
                st.columns(3)
            )

            with result_col1:
                st.metric(
                    "Created",
                    result["created"],
                )

            with result_col2:
                st.metric(
                    "Updated",
                    result["updated"],
                )

            with result_col3:
                st.metric(
                    "Failed",
                    result["failed"],
                )

            if result["success"]:
                st.success(
                    "All applications synchronized successfully."
                )

            else:
                st.warning(
                    "Synchronization completed with some errors."
                )

                with st.expander(
                    "Show synchronization errors"
                ):
                    for error_item in result[
                        "errors"
                    ]:
                        st.write(
                            f"Application ID "
                            f"{error_item['application_id']}: "
                            f"{error_item['error']}"
                        )

        except Exception as error:
            st.error(
                "Full synchronization failed."
            )

            st.code(
                str(error)
            )