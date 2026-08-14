from datetime import date

import pandas as pd
import streamlit as st

from services.job_tracker import (
    delete_application,
    get_all_applications,
    get_application_by_id,
    update_application,
)


APPLICATION_STATUSES = [
    "Discovered",
    "Analysed",
    "Preparing",
    "Applied",
    "Assessment",
    "Interview",
    "Second Interview",
    "Offer",
    "Rejected",
    "Withdrawn",
    "No Response",
]


APPLICATION_SOURCES = [
    "",
    "LinkedIn",
    "Indeed",
    "StepStone",
    "XING",
    "Bundesagentur für Arbeit",
    "Company Website",
    "Ausbildung.de",
    "Referral",
    "Recruiter",
    "University",
    "Other",
]


CLOSED_STATUSES = {
    "Offer",
    "Rejected",
    "Withdrawn",
}


DISPLAY_COLUMNS = {
    "id": "ID",
    "company": "Company",
    "job_title": "Job Title",
    "location": "Location",
    "application_date": "Application Date",
    "status": "Status",
    "application_source": "Source",
    "last_follow_up_date": "Last Follow-up",
    "next_follow_up_date": "Next Follow-up",
    "job_url": "Job URL",
    "contact_name": "Contact Name",
    "contact_email": "Contact Email",
    "contact_phone": "Contact Phone",
    "skill_match_score": "Skill Match",
    "ats_score": "ATS Score",
    "overall_match_score": "Overall Match",
    "cv_version": "CV Version",
    "cover_letter_version": "Cover Letter Version",
    "target_company_id": "Target Company ID",
    "career_target_role": "Career Target Role",
    "preparation_stage": "Career Prep Stage",
    "tailored_cv_ready": "Tailored CV Ready",
    "interview_pack_ready": "Interview Pack Ready",
    "interview_pack_language": "Interview Pack Language",
    "career_next_action": "Career Next Action",
    "career_notes": "Career Notes",
    "last_career_sync_at": "Career Sync",
    "notes": "Notes",
    "created_at": "Created At",
    "updated_at": "Updated At",
}


def parse_optional_date(
    value: str | None,
) -> date | None:
    """
    Convert an ISO date string into a date object.
    """

    if not value:
        return None

    try:
        return date.fromisoformat(
            value
        )

    except ValueError:
        return None


def get_form_date(
    value: str | None,
) -> date:
    """
    Return a valid date for a required date input.
    """

    parsed_date = parse_optional_date(
        value
    )

    if parsed_date:
        return parsed_date

    return date.today()


def calculate_follow_up_state(
    application: dict,
) -> str:
    """
    Return the current follow-up state for one application.
    """

    status = application.get(
        "status",
        "",
    )

    if status in CLOSED_STATUSES:
        return "Closed"

    next_follow_up = parse_optional_date(
        application.get(
            "next_follow_up_date"
        )
    )

    if next_follow_up is None:
        return "Not planned"

    today = date.today()

    if next_follow_up < today:
        return "Overdue"

    if next_follow_up == today:
        return "Due today"

    return "Upcoming"


def add_follow_up_state(
    applications: list[dict],
) -> list[dict]:
    """
    Add a calculated follow-up state to every application.
    """

    updated_applications = []

    for application in applications:
        application_copy = (
            application.copy()
        )

        application_copy[
            "follow_up_state"
        ] = calculate_follow_up_state(
            application
        )

        updated_applications.append(
            application_copy
        )

    return updated_applications


def prepare_tracker_dataframe(
    applications: list[dict],
) -> pd.DataFrame:
    """
    Convert saved applications into a display-ready table.
    """

    dataframe = pd.DataFrame(
        applications
    )

    if dataframe.empty:
        return dataframe

    dataframe = dataframe.rename(
        columns={
            **DISPLAY_COLUMNS,
            "follow_up_state": "Follow-up State",
        }
    )

    preferred_order = [
        "ID",
        "Company",
        "Job Title",
        "Location",
        "Application Date",
        "Status",
        "Follow-up State",
        "Next Follow-up",
        "Last Follow-up",
        "Source",
        "Overall Match",
        "Skill Match",
        "ATS Score",
        "Contact Name",
        "Contact Email",
        "Contact Phone",
        "Job URL",
        "CV Version",
        "Cover Letter Version",
        "Notes",
        "Created At",
        "Updated At",
    ]

    available_columns = [
        column
        for column in preferred_order
        if column in dataframe.columns
    ]

    return dataframe[
        available_columns
    ]


def render_tracker_metrics(
    applications: list[dict],
) -> None:
    """
    Display summary metrics for the tracker.
    """

    total_applications = len(
        applications
    )

    applied_count = sum(
        application.get("status")
        in {
            "Applied",
            "Assessment",
            "Interview",
            "Second Interview",
            "Offer",
        }
        for application in applications
    )

    interview_count = sum(
        application.get("status")
        in {
            "Interview",
            "Second Interview",
        }
        for application in applications
    )

    overdue_count = sum(
        application.get(
            "follow_up_state"
        )
        == "Overdue"
        for application in applications
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:
        st.metric(
            "Total Applications",
            total_applications,
        )

    with metric_col2:
        st.metric(
            "Applied or Later",
            applied_count,
        )

    with metric_col3:
        st.metric(
            "Interviews",
            interview_count,
        )

    with metric_col4:
        st.metric(
            "Overdue Follow-ups",
            overdue_count,
        )


def render_follow_up_alerts(
    applications: list[dict],
) -> None:
    """
    Show applications that need immediate follow-up.
    """

    overdue_applications = [
        application
        for application in applications
        if application.get(
            "follow_up_state"
        )
        == "Overdue"
    ]

    due_today_applications = [
        application
        for application in applications
        if application.get(
            "follow_up_state"
        )
        == "Due today"
    ]

    if not overdue_applications and not due_today_applications:
        return

    st.subheader(
        "Follow-up Actions"
    )

    if overdue_applications:
        st.error(
            f"{len(overdue_applications)} application(s) "
            "have an overdue follow-up."
        )

        with st.expander(
            "Show overdue follow-ups"
        ):
            for application in overdue_applications:
                st.write(
                    f"**{application['company']} — "
                    f"{application['job_title']}**"
                )

                st.write(
                    "Follow-up date: "
                    f"{application.get('next_follow_up_date', '')}"
                )

                contact_email = application.get(
                    "contact_email",
                    "",
                )

                if contact_email:
                    st.write(
                        f"Contact: {contact_email}"
                    )

                st.divider()

    if due_today_applications:
        st.warning(
            f"{len(due_today_applications)} application(s) "
            "need follow-up today."
        )

        with st.expander(
            "Show follow-ups due today"
        ):
            for application in due_today_applications:
                st.write(
                    f"**{application['company']} — "
                    f"{application['job_title']}**"
                )

                contact_email = application.get(
                    "contact_email",
                    "",
                )

                if contact_email:
                    st.write(
                        f"Contact: {contact_email}"
                    )

                st.divider()


def render_tracker_filters(
    applications: list[dict],
    component_key: str,
) -> list[dict]:
    """
    Allow the user to filter tracker records.
    """

    st.subheader(
        "Filter Applications"
    )

    filter_col1, filter_col2, filter_col3 = (
        st.columns(3)
    )

    status_options = sorted(
        {
            application.get(
                "status",
                "",
            )
            for application in applications
            if application.get("status")
        }
    )

    source_options = sorted(
        {
            application.get(
                "application_source",
                "",
            )
            for application in applications
            if application.get(
                "application_source"
            )
        }
    )

    follow_up_options = [
        "Overdue",
        "Due today",
        "Upcoming",
        "Not planned",
        "Closed",
    ]

    with filter_col1:
        selected_statuses = st.multiselect(
            "Status",
            status_options,
            key=(
                f"tracker_status_filter_"
                f"{component_key}"
            ),
        )

    with filter_col2:
        selected_sources = st.multiselect(
            "Source",
            source_options,
            key=(
                f"tracker_source_filter_"
                f"{component_key}"
            ),
        )

    with filter_col3:
        selected_follow_up_states = (
            st.multiselect(
                "Follow-up state",
                follow_up_options,
                key=(
                    f"tracker_followup_filter_"
                    f"{component_key}"
                ),
            )
        )

    search_text = st.text_input(
        "Search company, job title or location",
        key=(
            f"tracker_search_"
            f"{component_key}"
        ),
    ).strip().lower()

    filtered_applications = []

    for application in applications:
        if (
            selected_statuses
            and application.get("status")
            not in selected_statuses
        ):
            continue

        if (
            selected_sources
            and application.get(
                "application_source"
            )
            not in selected_sources
        ):
            continue

        if (
            selected_follow_up_states
            and application.get(
                "follow_up_state"
            )
            not in selected_follow_up_states
        ):
            continue

        searchable_text = " ".join(
            [
                str(
                    application.get(
                        "company",
                        "",
                    )
                ),
                str(
                    application.get(
                        "job_title",
                        "",
                    )
                ),
                str(
                    application.get(
                        "location",
                        "",
                    )
                ),
            ]
        ).lower()

        if (
            search_text
            and search_text
            not in searchable_text
        ):
            continue

        filtered_applications.append(
            application
        )

    return filtered_applications


def render_application_editor(
    applications: list[dict],
    component_key: str,
) -> None:
    """
    Display controls for updating or deleting an application.
    """

    st.subheader(
        "Manage Saved Application"
    )

    application_options = {
        (
            f"ID {application['id']} — "
            f"{application['company']} — "
            f"{application['job_title']}"
        ): application["id"]
        for application in applications
    }

    selected_label = st.selectbox(
        "Select an application",
        options=list(
            application_options.keys()
        ),
        key=(
            f"selected_application_"
            f"{component_key}"
        ),
    )

    selected_application_id = (
        application_options[
            selected_label
        ]
    )

    selected_application = (
        get_application_by_id(
            selected_application_id
        )
    )

    if selected_application is None:
        st.error(
            "The selected application could not be found."
        )
        return

    current_status = selected_application.get(
        "status",
        "Discovered",
    )

    if current_status in APPLICATION_STATUSES:
        status_index = (
            APPLICATION_STATUSES.index(
                current_status
            )
        )
    else:
        status_index = 0

    current_source = selected_application.get(
        "application_source",
        "",
    )

    if current_source in APPLICATION_SOURCES:
        source_index = (
            APPLICATION_SOURCES.index(
                current_source
            )
        )
    else:
        source_index = 0

    with st.form(
        f"update_application_form_{component_key}"
    ):
        form_col1, form_col2 = st.columns(2)

        with form_col1:
            updated_company = st.text_input(
                "Company name *",
                value=selected_application.get(
                    "company",
                    "",
                ),
                key=(
                    f"edit_company_"
                    f"{component_key}"
                ),
            )

            updated_job_title = st.text_input(
                "Job title *",
                value=selected_application.get(
                    "job_title",
                    "",
                ),
                key=(
                    f"edit_job_title_"
                    f"{component_key}"
                ),
            )

            updated_location = st.text_input(
                "Location",
                value=selected_application.get(
                    "location",
                    "",
                )
                or "",
                key=(
                    f"edit_location_"
                    f"{component_key}"
                ),
            )

            updated_application_date = (
                st.date_input(
                    "Application date",
                    value=get_form_date(
                        selected_application.get(
                            "application_date"
                        )
                    ),
                    key=(
                        f"edit_application_date_"
                        f"{component_key}"
                    ),
                )
            )

            updated_status = st.selectbox(
                "Application status",
                APPLICATION_STATUSES,
                index=status_index,
                key=(
                    f"edit_status_"
                    f"{component_key}"
                ),
            )

            updated_source = st.selectbox(
                "Application source",
                APPLICATION_SOURCES,
                index=source_index,
                key=(
                    f"edit_source_"
                    f"{component_key}"
                ),
            )

        with form_col2:
            updated_job_url = st.text_input(
                "Job URL",
                value=selected_application.get(
                    "job_url",
                    "",
                )
                or "",
                key=(
                    f"edit_url_"
                    f"{component_key}"
                ),
            )

            updated_contact_name = (
                st.text_input(
                    "Contact name",
                    value=selected_application.get(
                        "contact_name",
                        "",
                    )
                    or "",
                    key=(
                        f"edit_contact_name_"
                        f"{component_key}"
                    ),
                )
            )

            updated_contact_email = (
                st.text_input(
                    "Contact email",
                    value=selected_application.get(
                        "contact_email",
                        "",
                    )
                    or "",
                    key=(
                        f"edit_contact_email_"
                        f"{component_key}"
                    ),
                )
            )

            updated_contact_phone = (
                st.text_input(
                    "Contact phone",
                    value=selected_application.get(
                        "contact_phone",
                        "",
                    )
                    or "",
                    key=(
                        f"edit_contact_phone_"
                        f"{component_key}"
                    ),
                )
            )

            updated_cv_version = st.text_input(
                "CV version used",
                value=selected_application.get(
                    "cv_version",
                    "",
                )
                or "",
                key=(
                    f"edit_cv_version_"
                    f"{component_key}"
                ),
            )

            updated_cover_letter_version = (
                st.text_input(
                    "Cover-letter version used",
                    value=selected_application.get(
                        "cover_letter_version",
                        "",
                    )
                    or "",
                    key=(
                        f"edit_cover_letter_version_"
                        f"{component_key}"
                    ),
                )
            )

        st.write("### Follow-up dates")

        follow_up_col1, follow_up_col2 = (
            st.columns(2)
        )

        current_last_follow_up = (
            parse_optional_date(
                selected_application.get(
                    "last_follow_up_date"
                )
            )
        )

        current_next_follow_up = (
            parse_optional_date(
                selected_application.get(
                    "next_follow_up_date"
                )
            )
        )

        with follow_up_col1:
            has_last_follow_up = st.checkbox(
                "A follow-up has been completed",
                value=(
                    current_last_follow_up
                    is not None
                ),
                key=(
                    f"edit_has_last_followup_"
                    f"{component_key}"
                ),
            )

            if has_last_follow_up:
                updated_last_follow_up = (
                    st.date_input(
                        "Last follow-up date",
                        value=(
                            current_last_follow_up
                            or date.today()
                        ),
                        key=(
                            f"edit_last_followup_"
                            f"{component_key}"
                        ),
                    )
                )
            else:
                updated_last_follow_up = None

        with follow_up_col2:
            has_next_follow_up = st.checkbox(
                "Plan another follow-up",
                value=(
                    current_next_follow_up
                    is not None
                ),
                key=(
                    f"edit_has_next_followup_"
                    f"{component_key}"
                ),
            )

            if has_next_follow_up:
                updated_next_follow_up = (
                    st.date_input(
                        "Next follow-up date",
                        value=(
                            current_next_follow_up
                            or date.today()
                        ),
                        key=(
                            f"edit_next_followup_"
                            f"{component_key}"
                        ),
                    )
                )
            else:
                updated_next_follow_up = None

        updated_notes = st.text_area(
            "Notes",
            value=selected_application.get(
                "notes",
                "",
            )
            or "",
            height=120,
            key=(
                f"edit_notes_"
                f"{component_key}"
            ),
        )

        update_button = (
            st.form_submit_button(
                "Update Application",
                type="primary",
                use_container_width=True,
            )
        )

        if update_button:
            if not updated_company.strip():
                st.error(
                    "Company name is required."
                )

            elif not updated_job_title.strip():
                st.error(
                    "Job title is required."
                )

            else:
                was_updated = (
                    update_application(
                        application_id=(
                            selected_application_id
                        ),
                        company=updated_company,
                        job_title=updated_job_title,
                        location=updated_location,
                        application_date=(
                            updated_application_date.isoformat()
                        ),
                        status=updated_status,
                        job_url=updated_job_url,
                        contact_name=(
                            updated_contact_name
                        ),
                        contact_email=(
                            updated_contact_email
                        ),
                        contact_phone=(
                            updated_contact_phone
                        ),
                        notes=updated_notes,
                        last_follow_up_date=(
                            updated_last_follow_up.isoformat()
                            if updated_last_follow_up
                            else ""
                        ),
                        next_follow_up_date=(
                            updated_next_follow_up.isoformat()
                            if updated_next_follow_up
                            else ""
                        ),
                        application_source=(
                            updated_source
                        ),
                        cv_version=(
                            updated_cv_version
                        ),
                        cover_letter_version=(
                            updated_cover_letter_version
                        ),
                    )
                )

                if was_updated:
                    st.session_state[
                        "tracker_message"
                    ] = (
                        "Application updated successfully."
                    )

                    st.rerun()

                else:
                    st.error(
                        "The application could not be updated."
                    )

    st.write(
        "### Delete application"
    )

    st.warning(
        "Deleting an application is permanent."
    )

    confirm_delete = st.checkbox(
        (
            "I understand that this application "
            "will be permanently deleted."
        ),
        key=(
            f"confirm_delete_"
            f"{component_key}"
        ),
    )

    if st.button(
        "Delete Selected Application",
        use_container_width=True,
        disabled=not confirm_delete,
        key=(
            f"delete_application_"
            f"{component_key}"
        ),
    ):
        was_deleted = delete_application(
            selected_application_id
        )

        if was_deleted:
            st.session_state[
                "tracker_message"
            ] = (
                "Application deleted successfully."
            )

            st.rerun()

        else:
            st.error(
                "The application could not be deleted."
            )


def render_tracker(
    title: str = "Application Tracker",
    show_heading: bool = True,
    component_key: str = "main",
) -> None:
    """
    Display, filter, download, update and delete applications.
    """

    if show_heading:
        st.header(
            title
        )

    tracker_message = st.session_state.pop(
        "tracker_message",
        None,
    )

    if tracker_message:
        st.success(
            tracker_message
        )

    applications = get_all_applications()

    if not applications:
        st.info(
            "No verified applications have been saved yet."
        )
        return

    applications = add_follow_up_state(
        applications
    )

    render_tracker_metrics(
        applications
    )

    render_follow_up_alerts(
        applications
    )

    filtered_applications = (
        render_tracker_filters(
            applications=applications,
            component_key=component_key,
        )
    )

    if not filtered_applications:
        st.info(
            "No applications match the selected filters."
        )
        return

    tracker_dataframe = (
        prepare_tracker_dataframe(
            filtered_applications
        )
    )

    st.write(
        f"Showing {len(filtered_applications)} "
        f"of {len(applications)} application(s)."
    )

    st.dataframe(
        tracker_dataframe,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Job URL": (
                st.column_config.LinkColumn(
                    "Job URL"
                )
            ),
            "Skill Match": (
                st.column_config.NumberColumn(
                    "Skill Match",
                    format="%.1f%%",
                )
            ),
            "ATS Score": (
                st.column_config.NumberColumn(
                    "ATS Score",
                    format="%.1f%%",
                )
            ),
            "Overall Match": (
                st.column_config.NumberColumn(
                    "Overall Match",
                    format="%.1f%%",
                )
            ),
            "Application Date": (
                st.column_config.DateColumn(
                    "Application Date",
                    format="YYYY-MM-DD",
                )
            ),
            "Last Follow-up": (
                st.column_config.DateColumn(
                    "Last Follow-up",
                    format="YYYY-MM-DD",
                )
            ),
            "Next Follow-up": (
                st.column_config.DateColumn(
                    "Next Follow-up",
                    format="YYYY-MM-DD",
                )
            ),
        },
    )

    csv_data = tracker_dataframe.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label=(
            "Download Filtered Tracker as CSV"
        ),
        data=csv_data,
        file_name=(
            "job_application_tracker.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key=(
            f"download_tracker_"
            f"{component_key}"
        ),
    )

    with st.expander(
        "Update or Delete an Application"
    ):
        render_application_editor(
            applications=applications,
            component_key=component_key,
        )