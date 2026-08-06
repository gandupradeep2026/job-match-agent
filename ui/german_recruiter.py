import streamlit as st


COMPONENT_LABELS = {
    "job_match": "Job Match",
    "ats_compatibility": "ATS Compatibility",
    "german_cv_quality": "German CV Quality",
    "experience_evidence": "Experience Evidence",
    "professional_branding": "Professional Branding",
    "language_profile": "Language Profile",
}


def render_recruiter_decision(
    recommendation: dict,
) -> None:
    """
    Display the overall recruiter recommendation.
    """

    decision = recommendation.get(
        "decision",
        "Not calculated",
    )

    explanation = recommendation.get(
        "explanation",
        "",
    )

    level = recommendation.get(
        "level",
        "moderate",
    )

    st.subheader(
        decision
    )

    if level == "strong":
        st.success(
            explanation
        )

    elif level == "positive":
        st.info(
            explanation
        )

    elif level == "moderate":
        st.warning(
            explanation
        )

    else:
        st.error(
            explanation
        )


def render_component_scores(
    components: dict,
    weights: dict,
) -> None:
    """
    Display all recruiter-score components.
    """

    st.subheader(
        "Recruiter Score Breakdown"
    )

    component_names = [
        "job_match",
        "ats_compatibility",
        "german_cv_quality",
        "experience_evidence",
        "professional_branding",
        "language_profile",
    ]

    left_column, right_column = (
        st.columns(2)
    )

    for index, component_name in enumerate(
        component_names
    ):
        score = float(
            components.get(
                component_name,
                0.0,
            )
        )

        weight = float(
            weights.get(
                component_name,
                0.0,
            )
        )

        label = COMPONENT_LABELS.get(
            component_name,
            component_name.replace(
                "_",
                " ",
            ).title(),
        )

        target_column = (
            left_column
            if index % 2 == 0
            else right_column
        )

        with target_column:
            st.write(
                f"**{label}**"
            )

            st.progress(
                min(
                    max(
                        score / 100,
                        0.0,
                    ),
                    1.0,
                )
            )

            st.write(
                f"{score}%"
            )

            st.caption(
                f"Weight: "
                f"{round(weight * 100)}%"
            )

            st.write("")


def render_text_list(
    title: str,
    items: list[str],
    empty_message: str,
) -> None:
    """
    Display a heading followed by text items.
    """

    st.subheader(
        title
    )

    if not items:
        st.caption(
            empty_message
        )
        return

    for item in items:
        st.write(
            f"- {item}"
        )


def render_detailed_cv_checks(
    cv_checks: dict,
) -> None:
    """
    Display the deterministic German CV checks.
    """

    with st.expander(
        "Show Detailed German CV Checks"
    ):
        contact = cv_checks.get(
            "contact",
            {},
        )

        structure = cv_checks.get(
            "structure",
            {},
        )

        language = cv_checks.get(
            "language",
            {},
        )

        achievements = cv_checks.get(
            "achievements",
            {},
        )

        german_market = cv_checks.get(
            "german_market",
            {},
        )

        length = cv_checks.get(
            "length",
            {},
        )

        metric_col1, metric_col2, metric_col3 = (
            st.columns(3)
        )

        with metric_col1:
            st.metric(
                "Contact and Branding",
                f"{contact.get('score', 0.0)}%",
            )

            st.metric(
                "CV Structure",
                f"{structure.get('score', 0.0)}%",
            )

        with metric_col2:
            st.metric(
                "Language Profile",
                f"{language.get('score', 0.0)}%",
            )

            st.metric(
                "Achievement Quality",
                f"{achievements.get('score', 0.0)}%",
            )

        with metric_col3:
            st.metric(
                "German-Market Details",
                f"{german_market.get('score', 0.0)}%",
            )

            st.metric(
                "CV Length",
                f"{length.get('score', 0.0)}%",
            )

        st.write(
            f"**Detected German level:** "
            f"{language.get('german_level') or 'Not detected'}"
        )

        st.write(
            f"**Detected English level:** "
            f"{language.get('english_level') or 'Not detected'}"
        )

        st.write(
            f"**Word count:** "
            f"{length.get('word_count', 0)}"
        )

        st.write(
            f"**Action verbs detected:** "
            f"{achievements.get('action_verb_count', 0)}"
        )

        st.write(
            f"**Bullet points detected:** "
            f"{achievements.get('bullet_count', 0)}"
        )

        st.write(
            f"**Lines containing numbers:** "
            f"{achievements.get('numeric_achievement_count', 0)}"
        )

        st.write(
            f"**CV length assessment:** "
            f"{length.get('message', '')}"
        )

        st.write(
            "**Detected sections:**"
        )

        sections = structure.get(
            "sections",
            {},
        )

        for section, detected in sections.items():
            status = (
                "Yes"
                if detected
                else "No"
            )

            readable_section = section.replace(
                "_",
                " ",
            ).title()

            st.write(
                f"- {readable_section}: {status}"
            )


def render_german_recruiter_report(
    report: dict,
) -> None:
    """
    Display the complete German recruiter report.
    """

    st.divider()

    st.header(
        "German Recruiter Report"
    )

    st.caption(
        "This is an estimated internal assessment. "
        "It is not a guarantee of an interview or "
        "an employer decision."
    )

    if not report:
        st.info(
            "No German recruiter report is available."
        )
        return

    metric_col1, metric_col2, metric_col3 = (
        st.columns(3)
    )

    with metric_col1:
        st.metric(
            "German Recruiter Score",
            (
                f"{report.get('recruiter_score', 0.0)}%"
            ),
        )

    with metric_col2:
        st.metric(
            "Estimated Interview Chance",
            (
                f"{report.get('interview_probability', 0.0)}%"
            ),
        )

    with metric_col3:
        st.metric(
            "Required-Skill Evidence",
            (
                f"{report.get('required_skill_score', 0.0)}%"
            ),
        )

    render_recruiter_decision(
        report.get(
            "recommendation",
            {},
        )
    )

    st.divider()

    render_component_scores(
        components=report.get(
            "components",
            {},
        ),
        weights=report.get(
            "weights",
            {},
        ),
    )

    st.divider()

    strengths_column, improvements_column = (
        st.columns(2)
    )

    with strengths_column:
        render_text_list(
            title="Recruiter Strengths",
            items=report.get(
                "strengths",
                [],
            ),
            empty_message=(
                "No major strengths were identified."
            ),
        )

    with improvements_column:
        render_text_list(
            title="Priority Improvements",
            items=report.get(
                "priority_improvements",
                [],
            ),
            empty_message=(
                "No priority improvements were identified."
            ),
        )

    st.divider()

    notes_column, german_column = (
        st.columns(2)
    )

    with notes_column:
        render_text_list(
            title="Recruiter Notes",
            items=report.get(
                "recruiter_notes",
                [],
            ),
            empty_message=(
                "No recruiter notes are available."
            ),
        )

    with german_column:
        render_text_list(
            title="German-Market Suggestions",
            items=report.get(
                "german_suggestions",
                [],
            ),
            empty_message=(
                "No additional German-market "
                "suggestions were generated."
            ),
        )

    st.divider()

    render_text_list(
        title="Recommended Next Actions",
        items=report.get(
            "next_actions",
            [],
        ),
        empty_message=(
            "No next actions were generated."
        ),
    )

    render_detailed_cv_checks(
        report.get(
            "cv_checks",
            {},
        )
    )