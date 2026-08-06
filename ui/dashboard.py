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
        "contact_email",
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


def get_score_label(
    score: float,
) -> str:
    """
    Convert a numeric score into an easy-to-read label.
    """

    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Moderate"
    return "Needs work"


def get_interview_chance_label(
    dataframe: pd.DataFrame,
) -> str:
    """
    Estimate a simple interview-readiness label from saved outcomes.
    """

    if dataframe.empty:
        return "Not enough data"

    average_match = float(
        dataframe["overall_match_score"].mean()
    )

    interview_rate = safe_percentage(
        int(
            dataframe["status"].isin(
                INTERVIEW_STATUSES
            ).sum()
        ),
        len(dataframe),
    )

    if average_match >= 80 and interview_rate >= 25:
        return "High"
    if average_match >= 65 or interview_rate >= 10:
        return "Medium"
    return "Low"


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


def get_strongest_application(
    dataframe: pd.DataFrame,
) -> dict | None:
    """
    Return the highest-scoring application.
    """

    if dataframe.empty:
        return None

    row = dataframe.sort_values(
        "overall_match_score",
        ascending=False,
    ).iloc[0]

    return row.to_dict()


def get_weakest_application(
    dataframe: pd.DataFrame,
) -> dict | None:
    """
    Return the lowest-scoring application.
    """

    if dataframe.empty:
        return None

    row = dataframe.sort_values(
        "overall_match_score",
        ascending=True,
    ).iloc[0]

    return row.to_dict()


def build_next_action(
    dataframe: pd.DataFrame,
) -> str:
    """
    Generate one clear next action from current tracker data.
    """

    follow_up_summary = calculate_follow_up_summary(
        dataframe
    )

    overdue = follow_up_summary["overdue"]
    due_today = follow_up_summary["due_today"]

    if not overdue.empty:
        first = overdue.iloc[0]

        return (
            "Follow up with "
            f"{first.get('company', 'an employer')} "
            f"about the {first.get('job_title', 'role')} application."
        )

    if not due_today.empty:
        first = due_today.iloc[0]

        return (
            "Complete today's follow-up for "
            f"{first.get('company', 'an employer')}."
        )

    weak_applications = dataframe[
        dataframe["overall_match_score"] < 65
    ].sort_values(
        "overall_match_score",
        ascending=True,
    )

    if not weak_applications.empty:
        first = weak_applications.iloc[0]

        return (
            "Review and strengthen the application for "
            f"{first.get('company', 'the employer')} — "
            f"{first.get('job_title', 'target role')}."
        )

    preparing = dataframe[
        dataframe["status"].isin(
            {
                "Discovered",
                "Analysed",
                "Preparing",
            }
        )
    ]

    if not preparing.empty:
        first = preparing.iloc[0]

        return (
            "Finish preparing and submit the application for "
            f"{first.get('company', 'the employer')}."
        )

    return (
        "Your tracker has no urgent issues. "
        "Add a new target role or prepare for upcoming interviews."
    )


def render_professional_overview(
    dataframe: pd.DataFrame,
) -> None:
    """
    Render a concise executive-style summary.
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

    average_overall = round(
        float(
            dataframe[
                "overall_match_score"
            ].mean()
        ),
        1,
    )

    average_ats = round(
        float(
            dataframe[
                "ats_score"
            ].mean()
        ),
        1,
    )

    interview_chance = (
        get_interview_chance_label(
            dataframe
        )
    )

    st.subheader(
        "Today's Summary"
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:
        st.metric(
            "Active Applications",
            active_count,
            help=(
                f"{total_applications} application(s) "
                "are stored in total."
            ),
        )

    with metric_col2:
        st.metric(
            "Average Match",
            f"{average_overall}%",
            get_score_label(
                average_overall
            ),
        )

    with metric_col3:
        st.metric(
            "Average ATS",
            f"{average_ats}%",
            get_score_label(
                average_ats
            ),
        )

    with metric_col4:
        st.metric(
            "Interview Outlook",
            interview_chance,
            help=(
                "This is a simple estimate based on saved "
                "scores and tracker outcomes, not a guarantee."
            ),
        )

    outcome_col1, outcome_col2, outcome_col3 = (
        st.columns(3)
    )

    with outcome_col1:
        st.metric(
            "Interviews",
            interview_count,
        )

    with outcome_col2:
        st.metric(
            "Offers",
            offer_count,
        )

    with outcome_col3:
        st.metric(
            "Interview Rate",
            (
                f"{safe_percentage(
                    interview_count,
                    total_applications,
                )}%"
            ),
        )


def render_next_best_action(
    dataframe: pd.DataFrame,
) -> None:
    """
    Show one recommended action.
    """

    st.subheader(
        "Next Best Action"
    )

    st.info(
        build_next_action(
            dataframe
        )
    )


def render_best_and_weakest(
    dataframe: pd.DataFrame,
) -> None:
    """
    Show strongest and weakest saved applications.
    """

    strongest = get_strongest_application(
        dataframe
    )

    weakest = get_weakest_application(
        dataframe
    )

    st.subheader(
        "Application Priority"
    )

    strong_col, weak_col = st.columns(2)

    with strong_col:
        st.write(
            "### Strongest application"
        )

        if strongest:
            st.success(
                f"**{strongest.get('company', '')} — "
                f"{strongest.get('job_title', '')}**\n\n"
                f"Overall match: "
                f"{strongest.get('overall_match_score', 0):.1f}%\n\n"
                f"Status: {strongest.get('status', '') or 'Not specified'}"
            )
        else:
            st.caption(
                "No application data is available."
            )

    with weak_col:
        st.write(
            "### Application needing attention"
        )

        if weakest:
            st.warning(
                f"**{weakest.get('company', '')} — "
                f"{weakest.get('job_title', '')}**\n\n"
                f"Overall match: "
                f"{weakest.get('overall_match_score', 0):.1f}%\n\n"
                f"Status: {weakest.get('status', '') or 'Not specified'}"
            )
        else:
            st.caption(
                "No application data is available."
            )


def render_follow_up_snapshot(
    dataframe: pd.DataFrame,
) -> None:
    """
    Show urgent follow-up information.
    """

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

    st.subheader(
        "Follow-up Snapshot"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Overdue",
            len(overdue),
        )

    with col2:
        st.metric(
            "Due Today",
            len(due_today),
        )

    with col3:
        st.metric(
            "Next 7 Days",
            len(upcoming),
        )

    urgent = pd.concat(
        [
            overdue,
            due_today,
            upcoming,
        ],
        ignore_index=True,
    )

    if urgent.empty:
        st.success(
            "No follow-ups are currently due."
        )
        return

    display_data = urgent[
        [
            "company",
            "job_title",
            "status",
            "next_follow_up_date",
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
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
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
        float(
            dataframe[
                "skill_match_score"
            ].mean()
        ),
        1,
    )

    average_ats = round(
        float(
            dataframe[
                "ats_score"
            ].mean()
        ),
        1,
    )

    average_overall = round(
        float(
            dataframe[
                "overall_match_score"
            ].mean()
        ),
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

    with st.expander(
        "Dashboard Filters",
        expanded=False,
    ):
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
    Render the professional application dashboard.
    """

    st.header(
        "Job Search Command Center"
    )

    st.caption(
        "A clear summary of your applications, scores, "
        "follow-ups and next actions."
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

    render_professional_overview(
        filtered_dataframe
    )

    st.divider()

    render_next_best_action(
        filtered_dataframe
    )

    st.divider()

    render_best_and_weakest(
        filtered_dataframe
    )

    st.divider()

    render_follow_up_snapshot(
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

    render_top_match_applications(
        filtered_dataframe
    )
