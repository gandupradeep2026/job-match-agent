import streamlit as st


def render_score_summary(
    match_result: dict,
    ats_result: dict,
    job_match_result: dict,
) -> None:
    """
    Display the main scores and overall rating.
    """

    st.divider()
    st.header("Analysis Results")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            label="Overall Job Match",
            value=f"{job_match_result['score']}%",
        )

    with metric_col2:
        st.metric(
            label="Skill Match",
            value=f"{match_result['score']}%",
        )

    with metric_col3:
        st.metric(
            label="Estimated ATS Score",
            value=f"{ats_result['score']}%",
        )

    st.subheader(job_match_result["rating"])

    score = job_match_result["score"]
    explanation = job_match_result["explanation"]

    if score >= 80:
        st.success(explanation)
    elif score >= 65:
        st.info(explanation)
    elif score >= 50:
        st.warning(explanation)
    else:
        st.error(explanation)

    st.caption(
        "These are estimated compatibility scores. "
        "They are not official employer ATS scores."
    )


def render_score_breakdown(
    match_result: dict,
    ats_result: dict,
    job_match_result: dict,
) -> None:
    """
    Display the weighted components of the overall score.
    """

    st.subheader("Score Breakdown")

    breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)

    with breakdown_col1:
        st.write("**Skill compatibility**")

        st.progress(
            min(max(match_result["score"] / 100, 0.0), 1.0)
        )

        st.write(
            f"{match_result['score']}% × 60% weighting"
        )

    with breakdown_col2:
        st.write("**ATS readability**")

        st.progress(
            min(max(ats_result["score"] / 100, 0.0), 1.0)
        )

        st.write(
            f"{ats_result['score']}% × 30% weighting"
        )

    with breakdown_col3:
        profile_score = job_match_result[
            "profile_completeness_score"
        ]

        st.write("**Profile completeness**")

        st.progress(
            min(max(profile_score / 100, 0.0), 1.0)
        )

        st.write(
            f"{profile_score}% × 10% weighting"
        )


def render_skill_details(
    match_result: dict,
) -> None:
    """
    Display matched, missing and additional skills.
    """

    st.divider()
    st.subheader("Skill Match Details")

    skill_col1, skill_col2 = st.columns(2)

    with skill_col1:
        st.write("### Matched skills")

        matched_skills = match_result.get(
            "matched_keywords",
            [],
        )

        if matched_skills:
            for skill in matched_skills:
                st.success(f"✓ {skill}")
        else:
            st.write(
                "No matching technical skills were detected."
            )

    with skill_col2:
        st.write("### Missing skills")

        missing_skills = match_result.get(
            "missing_keywords",
            [],
        )

        frequency_data = match_result.get(
            "job_skill_frequency",
            {},
        )

        if missing_skills:
            for skill in missing_skills:
                frequency = frequency_data.get(
                    skill,
                    1,
                )

                st.error(
                    f"✗ {skill} — mentioned "
                    f"{frequency} time(s)"
                )
        else:
            st.write(
                "No missing technical skills were detected."
            )

    with st.expander(
        "Additional skills found in your CV"
    ):
        additional_skills = match_result.get(
            "additional_cv_skills",
            [],
        )

        if additional_skills:
            st.write(", ".join(additional_skills))
        else:
            st.write(
                "No additional recognised skills were detected."
            )

    with st.expander(
        "Show all detected skills"
    ):
        detected_col1, detected_col2 = st.columns(2)

        with detected_col1:
            st.write("**Skills detected in CV:**")

            cv_keywords = match_result.get(
                "cv_keywords",
                [],
            )

            if cv_keywords:
                st.write(", ".join(cv_keywords))
            else:
                st.write(
                    "No recognised skills detected."
                )

        with detected_col2:
            st.write(
                "**Skills detected in job description:**"
            )

            job_keywords = match_result.get(
                "job_keywords",
                [],
            )

            if job_keywords:
                st.write(", ".join(job_keywords))
            else:
                st.write(
                    "No recognised skills detected."
                )


def render_ats_details(
    ats_result: dict,
) -> None:
    """
    Display ATS checks and CV statistics.
    """

    st.divider()
    st.subheader("ATS Readability Details")

    checks = ats_result.get(
        "checks",
        [],
    )

    for check in checks:
        if check["passed"]:
            st.success(
                f"✓ {check['name']} "
                f"(+{check['points']} points): "
                f"{check['message']}"
            )
        else:
            st.error(
                f"✗ {check['name']}: "
                f"{check['message']}"
            )

    with st.expander("Show CV statistics"):
        st.write(
            f"Word count: "
            f"{ats_result.get('word_count', 0)}"
        )

        st.write(
            f"Character count: "
            f"{ats_result.get('text_length', 0)}"
        )

        st.write("**Detected sections:**")

        headings = ats_result.get(
            "headings",
            {},
        )

        for heading, detected in headings.items():
            status = "Yes" if detected else "No"

            st.write(
                f"- {heading.title()}: {status}"
            )


def render_extracted_text(
    cv_text: str,
    job_text: str,
) -> None:
    """
    Display the extracted source text.
    """

    with st.expander(
        "Show extracted document text"
    ):
        text_col1, text_col2 = st.columns(2)

        with text_col1:
            st.subheader("Extracted CV text")

            st.text_area(
                "CV result",
                value=cv_text,
                height=400,
                disabled=True,
                key="display_cv_result",
            )

        with text_col2:
            st.subheader(
                "Extracted job description"
            )

            st.text_area(
                "Job description result",
                value=job_text,
                height=400,
                disabled=True,
                key="display_job_result",
            )


def render_analysis_results(
    match_result: dict,
    ats_result: dict,
    job_match_result: dict,
    cv_text: str,
    job_text: str,
) -> None:
    """
    Render the complete analysis-result interface.
    """

    render_score_summary(
        match_result=match_result,
        ats_result=ats_result,
        job_match_result=job_match_result,
    )

    render_score_breakdown(
        match_result=match_result,
        ats_result=ats_result,
        job_match_result=job_match_result,
    )

    render_skill_details(
        match_result=match_result,
    )

    render_ats_details(
        ats_result=ats_result,
    )

    render_extracted_text(
        cv_text=cv_text,
        job_text=job_text,
    )