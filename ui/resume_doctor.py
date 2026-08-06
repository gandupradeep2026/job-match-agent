import streamlit as st


PRIORITY_ICONS = {
    "high": "🔴",
    "medium": "🟠",
    "low": "🟡",
}


def render_resume_doctor(
    report: dict,
) -> None:
    """Render the explainable Resume Doctor report."""

    st.divider()
    st.header("AI Resume Doctor")
    st.caption(
        "This panel combines ATS problems, job-specific gaps, "
        "local-AI feedback, and German recruiter recommendations."
    )

    if not report:
        st.info("No Resume Doctor report is available.")
        return

    summary = report.get("summary", {}) or {}
    problems = report.get("problems", []) or []
    top_actions = report.get("top_actions", []) or []

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total issues",
            summary.get("total_problems", 0),
        )

    with col2:
        st.metric(
            "High priority",
            summary.get("high_priority", 0),
        )

    with col3:
        st.metric(
            "Medium priority",
            summary.get("medium_priority", 0),
        )

    with col4:
        st.metric(
            "Low priority",
            summary.get("low_priority", 0),
        )

    readiness = summary.get(
        "readiness",
        "Not calculated",
    )

    if readiness == "Generally ready":
        st.success(f"Readiness: {readiness}")
    elif readiness == "Some improvements recommended":
        st.info(f"Readiness: {readiness}")
    elif readiness == "Important improvements needed":
        st.warning(f"Readiness: {readiness}")
    else:
        st.error(f"Readiness: {readiness}")

    st.subheader("What to fix first")

    if top_actions:
        for index, action in enumerate(
            top_actions,
            start=1,
        ):
            st.write(f"**{index}.** {action}")
    else:
        st.success(
            "No major corrective actions were identified."
        )

    st.subheader("Detailed diagnosis")

    if not problems:
        st.success("No problems were identified.")
        return

    filter_value = st.selectbox(
        "Show priority",
        [
            "All",
            "High",
            "Medium",
            "Low",
        ],
        key="resume_doctor_priority_filter",
    )

    selected_priority = (
        ""
        if filter_value == "All"
        else filter_value.lower()
    )

    visible_problems = [
        problem
        for problem in problems
        if not selected_priority
        or problem.get("priority") == selected_priority
    ]

    for index, problem in enumerate(
        visible_problems,
        start=1,
    ):
        priority = problem.get("priority", "medium")
        icon = PRIORITY_ICONS.get(priority, "⚪")
        category = problem.get("category", "General")
        title = problem.get("title", "Issue")
        impact = problem.get("impact", "")

        label = f"{icon} {index}. {title} — {category}"

        with st.expander(label):
            if impact:
                st.write(f"**Impact:** {impact}")

            why_it_matters = problem.get(
                "why_it_matters",
                "",
            )

            if why_it_matters:
                st.write(
                    f"**Why it matters:** {why_it_matters}"
                )

            evidence = problem.get("evidence", []) or []

            if evidence:
                st.write("**Evidence:**")
                for item in evidence:
                    st.write(f"- {item}")

            recommended_action = problem.get(
                "recommended_action",
                "",
            )

            if recommended_action:
                st.write(
                    "**Recommended action:** "
                    f"{recommended_action}"
                )

            if problem.get(
                "requires_user_confirmation",
                False,
            ):
                st.warning(
                    "This recommendation requires your confirmation. "
                    "Do not add anything that is not fully true."
                )

    st.warning(
        "Resume Doctor recommendations are advisory. "
        "Review every suggestion before changing your CV."
    )
