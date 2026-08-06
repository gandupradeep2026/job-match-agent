import streamlit as st


PRIORITY_LABELS = {
    "high": "High priority",
    "medium": "Medium priority",
    "low": "Low priority",
}


def _render_decision_banner(
    report: dict,
) -> None:
    """
    Display the recruiter-style decision.
    """

    decision = report.get(
        "decision",
        "Not calculated",
    )

    summary = report.get(
        "summary",
        "",
    )

    level = report.get(
        "decision_level",
        "mixed",
    )

    if level == "positive":
        st.success(
            f"**Recruiter's decision: {decision}**\n\n"
            f"{summary}"
        )
    elif level == "negative":
        st.error(
            f"**Recruiter's decision: {decision}**\n\n"
            f"{summary}"
        )
    else:
        st.warning(
            f"**Recruiter's decision: {decision}**\n\n"
            f"{summary}"
        )


def render_recruiter_decision(
    report: dict,
) -> None:
    """
    Render the complete recruiter decision simulator.
    """

    if not report:
        return

    st.divider()
    st.header(
        "AI Recruiter Decision"
    )

    st.caption(
        "See how a recruiter may interpret the current CV-job fit. "
        "The result is an estimate and must not be treated as an "
        "actual employer decision."
    )

    company = report.get(
        "company",
        "",
    )

    job_title = report.get(
        "job_title",
        "",
    )

    if company or job_title:
        st.write(
            f"**Target:** "
            f"{job_title or 'Role not detected'}"
            f"{' at ' + company if company else ''}"
        )

    _render_decision_banner(
        report
    )

    probability = report.get(
        "interview_probability",
        0,
    )

    score_data = report.get(
        "scores",
        {},
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:
        st.metric(
            "Interview-readiness estimate",
            f"{probability}%",
        )

    with metric_col2:
        st.metric(
            "Overall match",
            f"{score_data.get('overall_match', 0)}%",
        )

    with metric_col3:
        st.metric(
            "Skill match",
            f"{score_data.get('skill_match', 0)}%",
        )

    with metric_col4:
        st.metric(
            "ATS score",
            f"{score_data.get('ats_score', 0)}%",
        )

    st.progress(
        min(
            max(
                probability / 100,
                0.0,
            ),
            1.0,
        )
    )

    priority_col1, priority_col2 = (
        st.columns(2)
    )

    with priority_col1:
        st.metric(
            "High-priority concerns",
            report.get(
                "high_priority_count",
                0,
            ),
        )

    with priority_col2:
        st.metric(
            "Medium-priority concerns",
            report.get(
                "medium_priority_count",
                0,
            ),
        )

    rejection_reasons = report.get(
        "rejection_reasons",
        [],
    )

    st.subheader(
        "Why a recruiter may hesitate"
    )

    if rejection_reasons:
        for index, reason in enumerate(
            rejection_reasons,
            start=1,
        ):
            priority = reason.get(
                "priority",
                "medium",
            )

            label = PRIORITY_LABELS.get(
                priority,
                "Medium priority",
            )

            title = reason.get(
                "title",
                f"Concern {index}",
            )

            with st.expander(
                f"{index}. {title} — {label}"
            ):
                explanation = reason.get(
                    "explanation",
                    "",
                )

                if explanation:
                    st.write(
                        f"**Why it matters:** {explanation}"
                    )

                cv_evidence = reason.get(
                    "cv_evidence",
                    "",
                )

                if cv_evidence:
                    st.write(
                        "**CV evidence:**"
                    )
                    st.write(
                        cv_evidence
                    )

                job_evidence = reason.get(
                    "job_evidence",
                    "",
                )

                if job_evidence:
                    st.write(
                        "**Job-description evidence:**"
                    )
                    st.write(
                        job_evidence
                    )

                source = reason.get(
                    "source",
                    "",
                )

                if source:
                    st.caption(
                        f"Source: {source}"
                    )
    else:
        st.success(
            "No major recruiter concerns were identified."
        )

    st.subheader(
        "What could convince the recruiter"
    )

    actions = report.get(
        "convincing_actions",
        [],
    )

    if actions:
        for index, action in enumerate(
            actions,
            start=1,
        ):
            st.write(
                f"**{index}.** {action}"
            )
    else:
        st.info(
            "Keep the CV truthful, concise, and tailored "
            "to the specific role."
        )

    st.warning(
        "Never add a missing skill, responsibility, achievement, "
        "certificate, or language level unless it is true and you "
        "can support it."
    )

    disclaimer = report.get(
        "disclaimer",
        "",
    )

    if disclaimer:
        st.caption(
            disclaimer
        )
