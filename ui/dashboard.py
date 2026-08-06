from datetime import date, timedelta

import pandas as pd
import streamlit as st

from services.job_tracker import get_all_applications


CLOSED_STATUSES = {
    "Offer",
    "Rejected",
    "Withdrawn",
}


INTERVIEW_STATUSES = {
    "Interview",
    "Second Interview",
    "Offer",
}


ACTIVE_STATUSES = {
    "Discovered",
    "Analysed",
    "Preparing",
    "Applied",
    "Assessment",
    "Interview",
    "Second Interview",
    "No Response",
}


def safe_percentage(
    numerator: int,
    denominator: int,
) -> float:
    """
    Calculate a percentage without division-by-zero errors.
    """

    if denominator <= 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        1,
    )


def prepare_dashboard_dataframe(
    applications: list[dict],
) -> pd.DataFrame:
    """
    Convert application records into a DataFrame
    suitable for dashboard calculations.
    """

    dataframe = pd.DataFrame(
        applications
    )

    if dataframe.empty:
        return dataframe

    text_columns = [
        "company",
        "job_title",
        "location",
        "status",
        "application_source",
        "next_follow_up_date",
    ]

    for column in text_columns:
        if column not in dataframe.columns:
            dataframe[column] = ""

        dataframe[column] = (
            dataframe[column]
            .fillna("")
            .astype(str)
        )

    score_columns = [
        "skill_match_score",
        "ats_score",
        "overall_match_score",
    ]

    for column in score_columns:
        if column not in dataframe.columns:
            dataframe[column] = 0.0

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        ).fillna(0.0)

    if "application_date" not in dataframe.columns:
        dataframe["application_date"] = ""

    dataframe["application_date_parsed"] = pd.to_datetime(
        dataframe["application_date"],
        errors="coerce",
    )

    dataframe["next_follow_up_parsed"] = pd.to_datetime(
        dataframe["next_follow_up_date"],
        errors="coerce",
    )

    return dataframe


def render_main_metrics(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display the main application-performance metrics.
    """

    total_applications = len(
        dataframe
    )

    active_count = int(
        dataframe["status"].isin(
            ACTIVE_STATUSES
        ).sum()
    )

    interview_count = int(
        dataframe["status"].isin(
            INTERVIEW_STATUSES
        ).sum()
    )

    offer_count = int(
        dataframe["status"]
        .eq("Offer")
        .sum()
    )

    interview_rate = safe_percentage(
        interview_count,
        total_applications,
    )

    offer_rate = safe_percentage(
        offer_count,
        total_applications,
    )

    metric_row1_col1, metric_row1_col2, metric_row1_col3 = (
        st.columns(3)
    )

    with metric_row1_col1:
        st.metric(
            "Total Applications",
            total_applications,
        )

    with metric_row1_col2:
        st.metric(
            "Active Applications",
            active_count,
        )

    with metric_row1_col3:
        st.metric(
            "Interviews",
            interview_count,
        )

    metric_row2_col1, metric_row2_col2, metric_row2_col3 = (
        st.columns(3)
    )

    with metric_row2_col1:
        st.metric(
            "Offers",
            offer_count,
        )

    with metric_row2_col2:
        st.metric(
            "Interview Rate",
            f"{interview_rate}%",
        )

    with metric_row2_col3:
        st.metric(
            "Offer Rate",
            f"{offer_rate}%",
        )


def render_average_scores(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display average compatibility scores.
    """

    st.subheader(
        "Average Analysis Scores"
    )

    average_skill = round(
        dataframe[
            "skill_match_score"
        ].mean(),
        1,
    )

    average_ats = round(
        dataframe[
            "ats_score"
        ].mean(),
        1,
    )

    average_overall = round(
        dataframe[
            "overall_match_score"
        ].mean(),
        1,
    )

    score_col1, score_col2, score_col3 = (
        st.columns(3)
    )

    with score_col1:
        st.metric(
            "Average Skill Match",
            f"{average_skill}%",
        )

        st.progress(
            min(
                max(
                    average_skill / 100,
                    0.0,
                ),
                1.0,
            )
        )

    with score_col2:
        st.metric(
            "Average ATS Score",
            f"{average_ats}%",
        )

        st.progress(
            min(
                max(
                    average_ats / 100,
                    0.0,
                ),
                1.0,
            )
        )

    with score_col3:
        st.metric(
            "Average Overall Match",
            f"{average_overall}%",
        )

        st.progress(
            min(
                max(
                    average_overall / 100,
                    0.0,
                ),
                1.0,
            )
        )


def render_status_chart(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display the number of applications by status.
    """

    st.subheader(
        "Applications by Status"
    )

    status_counts = (
        dataframe["status"]
        .replace("", "Not specified")
        .value_counts()
        .rename_axis("Status")
        .reset_index(
            name="Applications"
        )
    )

    st.bar_chart(
        status_counts,
        x="Status",
        y="Applications",
        use_container_width=True,
    )


def render_application_timeline(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display applications submitted over time.
    """

    st.subheader(
        "Applications Over Time"
    )

    valid_dates = dataframe.dropna(
        subset=[
            "application_date_parsed"
        ]
    ).copy()

    if valid_dates.empty:
        st.info(
            "No valid application dates are available."
        )
        return

    valid_dates["Application Day"] = (
        valid_dates[
            "application_date_parsed"
        ].dt.date
    )

    timeline = (
        valid_dates.groupby(
            "Application Day"
        )
        .size()
        .reset_index(
            name="Applications"
        )
        .sort_values(
            "Application Day"
        )
    )

    st.line_chart(
        timeline,
        x="Application Day",
        y="Applications",
        use_container_width=True,
    )


def render_source_chart(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display the distribution of application sources.
    """

    st.subheader(
        "Applications by Source"
    )

    source_series = dataframe[
        "application_source"
    ].replace(
        "",
        "Not specified",
    )

    source_counts = (
        source_series
        .value_counts()
        .rename_axis("Source")
        .reset_index(
            name="Applications"
        )
    )

    st.bar_chart(
        source_counts,
        x="Source",
        y="Applications",
        use_container_width=True,
    )


def render_average_match_by_status(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display average overall match score for each status.
    """

    st.subheader(
        "Average Match Score by Status"
    )

    score_by_status = (
        dataframe.groupby(
            "status",
            dropna=False,
        )[
            "overall_match_score"
        ]
        .mean()
        .round(1)
        .reset_index()
        .rename(
            columns={
                "status": "Status",
                "overall_match_score": (
                    "Average Match"
                ),
            }
        )
    )

    score_by_status["Status"] = (
        score_by_status["Status"]
        .replace(
            "",
            "Not specified",
        )
    )

    st.bar_chart(
        score_by_status,
        x="Status",
        y="Average Match",
        use_container_width=True,
    )


def calculate_follow_up_summary(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Calculate overdue, due-today and upcoming follow-ups.
    """

    today = pd.Timestamp(
        date.today()
    )

    seven_days_later = pd.Timestamp(
        date.today()
        + timedelta(days=7)
    )

    open_application_mask = (
        ~dataframe["status"].isin(
            CLOSED_STATUSES
        )
    )

    has_follow_up_mask = (
        dataframe[
            "next_follow_up_parsed"
        ].notna()
    )

    overdue_mask = (
        open_application_mask
        & has_follow_up_mask
        & (
            dataframe[
                "next_follow_up_parsed"
            ]
            < today
        )
    )

    due_today_mask = (
        open_application_mask
        & has_follow_up_mask
        & (
            dataframe[
                "next_follow_up_parsed"
            ]
            == today
        )
    )

    upcoming_mask = (
        open_application_mask
        & has_follow_up_mask
        & (
            dataframe[
                "next_follow_up_parsed"
            ]
            > today
        )
        & (
            dataframe[
                "next_follow_up_parsed"
            ]
            <= seven_days_later
        )
    )

    return {
        "overdue": dataframe[
            overdue_mask
        ].copy(),
        "due_today": dataframe[
            due_today_mask
        ].copy(),
        "upcoming": dataframe[
            upcoming_mask
        ].copy(),
    }


def render_follow_up_dashboard(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display follow-up metrics and action lists.
    """

    st.subheader(
        "Follow-up Overview"
    )

    follow_up_summary = (
        calculate_follow_up_summary(
            dataframe
        )
    )

    overdue = follow_up_summary[
        "overdue"
    ]

    due_today = follow_up_summary[
        "due_today"
    ]

    upcoming = follow_up_summary[
        "upcoming"
    ]

    follow_col1, follow_col2, follow_col3 = (
        st.columns(3)
    )

    with follow_col1:
        st.metric(
            "Overdue",
            len(overdue),
        )

    with follow_col2:
        st.metric(
            "Due Today",
            len(due_today),
        )

    with follow_col3:
        st.metric(
            "Next 7 Days",
            len(upcoming),
        )

    if overdue.empty and due_today.empty and upcoming.empty:
        st.info(
            "No follow-up actions are currently scheduled."
        )
        return

    if not overdue.empty:
        with st.expander(
            "Overdue Follow-ups",
            expanded=True,
        ):
            display_follow_up_table(
                overdue
            )

    if not due_today.empty:
        with st.expander(
            "Follow-ups Due Today",
            expanded=True,
        ):
            display_follow_up_table(
                due_today
            )

    if not upcoming.empty:
        with st.expander(
            "Upcoming Follow-ups",
        ):
            display_follow_up_table(
                upcoming
            )


def display_follow_up_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display a compact follow-up action table.
    """

    display_data = dataframe[
        [
            "company",
            "job_title",
            "status",
            "next_follow_up_date",
            "contact_email",
        ]
    ].copy()

    display_data = display_data.rename(
        columns={
            "company": "Company",
            "job_title": "Job Title",
            "status": "Status",
            "next_follow_up_date": (
                "Follow-up Date"
            ),
            "contact_email": (
                "Contact Email"
            ),
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )


def render_top_match_applications(
    dataframe: pd.DataFrame,
) -> None:
    """
    Display applications with the highest overall match score.
    """

    st.subheader(
        "Highest-Match Applications"
    )

    top_matches = (
        dataframe.sort_values(
            "overall_match_score",
            ascending=False,
        )
        .head(10)
        .copy()
    )

    display_columns = [
        "company",
        "job_title",
        "status",
        "overall_match_score",
        "skill_match_score",
        "ats_score",
    ]

    top_matches = top_matches[
        display_columns
    ].rename(
        columns={
            "company": "Company",
            "job_title": "Job Title",
            "status": "Status",
            "overall_match_score": (
                "Overall Match"
            ),
            "skill_match_score": (
                "Skill Match"
            ),
            "ats_score": "ATS Score",
        }
    )

    st.dataframe(
        top_matches,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Overall Match": (
                st.column_config.ProgressColumn(
                    "Overall Match",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
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
        },
    )


def render_dashboard_filters(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Display dashboard filters and return filtered data.
    """

    st.subheader(
        "Dashboard Filters"
    )

    filter_col1, filter_col2 = st.columns(2)

    status_options = sorted(
        status
        for status in dataframe[
            "status"
        ].unique()
        if status
    )

    source_options = sorted(
        source
        for source in dataframe[
            "application_source"
        ].unique()
        if source
    )

    with filter_col1:
        selected_statuses = st.multiselect(
            "Filter by status",
            options=status_options,
            key="dashboard_status_filter",
        )

    with filter_col2:
        selected_sources = st.multiselect(
            "Filter by source",
            options=source_options,
            key="dashboard_source_filter",
        )

    filtered_dataframe = dataframe.copy()

    if selected_statuses:
        filtered_dataframe = (
            filtered_dataframe[
                filtered_dataframe[
                    "status"
                ].isin(
                    selected_statuses
                )
            ]
        )

    if selected_sources:
        filtered_dataframe = (
            filtered_dataframe[
                filtered_dataframe[
                    "application_source"
                ].isin(
                    selected_sources
                )
            ]
        )

    return filtered_dataframe


def render_dashboard() -> None:
    """
    Render the full application analytics dashboard.
    """

    st.header(
        "Application Analytics Dashboard"
    )

    st.caption(
        "The dashboard uses the applications stored "
        "in your local SQLite tracker."
    )

    applications = get_all_applications()

    if not applications:
        st.info(
            "No applications are available yet. "
            "Save at least one verified application "
            "to display dashboard analytics."
        )
        return

    dataframe = prepare_dashboard_dataframe(
        applications
    )

    filtered_dataframe = (
        render_dashboard_filters(
            dataframe
        )
    )

    if filtered_dataframe.empty:
        st.warning(
            "No applications match the selected filters."
        )
        return

    st.write(
        f"Showing analytics for "
        f"{len(filtered_dataframe)} of "
        f"{len(dataframe)} application(s)."
    )

    render_main_metrics(
        filtered_dataframe
    )

    st.divider()

    render_average_scores(
        filtered_dataframe
    )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        render_status_chart(
            filtered_dataframe
        )

    with chart_col2:
        render_source_chart(
            filtered_dataframe
        )

    timeline_col, score_status_col = (
        st.columns(2)
    )

    with timeline_col:
        render_application_timeline(
            filtered_dataframe
        )

    with score_status_col:
        render_average_match_by_status(
            filtered_dataframe
        )

    st.divider()

    render_follow_up_dashboard(
        filtered_dataframe
    )

    st.divider()

    render_top_match_applications(
        filtered_dataframe
    )