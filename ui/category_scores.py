import streamlit as st


CATEGORY_LABELS = {
    "required_skills": "Required Skills",
    "preferred_skills": "Preferred Skills",
    "experience": "Experience",
    "education": "Education",
    "languages": "Languages",
    "responsibilities": "Responsibilities",
    "ats_readability": "ATS Readability",
}


def render_category_detail(
    category_name: str,
    category_result: dict,
    weight: float,
) -> None:
    """
    Display one job-match category.
    """

    label = CATEGORY_LABELS.get(
        category_name,
        category_name.replace(
            "_",
            " ",
        ).title(),
    )

    score = float(
        category_result.get(
            "score",
            0.0,
        )
    )

    status = category_result.get(
        "status",
        "not_specified",
    )

    st.write(f"### {label}")

    if status == "not_specified":
        st.caption(
            "Not specified in the job description. "
            "This category is excluded from the total score."
        )
        return

    progress_value = min(
        max(
            score / 100,
            0.0,
        ),
        1.0,
    )

    st.progress(
        progress_value
    )

    st.write(
        f"**Score:** {score}%"
    )

    st.caption(
        f"Configured weighting: "
        f"{round(weight * 100)}%"
    )

    matched = category_result.get(
        "matched",
        [],
    )

    missing = category_result.get(
        "missing",
        [],
    )

    if matched:
        with st.expander(
            f"Matched {label.lower()} "
            f"({len(matched)})"
        ):
            for item in matched:
                st.success(
                    f"✓ {item}"
                )

    if missing:
        with st.expander(
            f"Missing or not evidenced "
            f"({len(missing)})"
        ):
            for item in missing:
                st.error(
                    f"✗ {item}"
                )

    if not matched and not missing:
        st.caption(
            "No individual evidence items are "
            "available for this category."
        )


def render_category_scores(
    category_match_result: dict,
) -> None:
    """
    Display the complete multi-category match report.
    """

    st.divider()
    st.header(
        "Detailed Job Match Breakdown"
    )

    st.caption(
        "A missing item means that it was not evidenced "
        "in the submitted CV. It does not prove that the "
        "candidate does not possess it."
    )

    overall_score = float(
        category_match_result.get(
            "overall_score",
            0.0,
        )
    )

    rating = category_match_result.get(
        "rating",
        "Not calculated",
    )

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Multi-category Job Match",
            f"{overall_score}%",
        )

    with metric_col2:
        st.metric(
            "Match Rating",
            rating,
        )

    categories = category_match_result.get(
        "categories",
        {},
    )

    weights = category_match_result.get(
        "weights",
        {},
    )

    category_names = [
        "required_skills",
        "preferred_skills",
        "experience",
        "education",
        "languages",
        "responsibilities",
        "ats_readability",
    ]

    left_column, right_column = (
        st.columns(2)
    )

    for index, category_name in enumerate(
        category_names
    ):
        category_result = categories.get(
            category_name,
            {
                "score": 0.0,
                "matched": [],
                "missing": [],
                "status": "not_specified",
            },
        )

        weight = float(
            weights.get(
                category_name,
                0.0,
            )
        )

        target_column = (
            left_column
            if index % 2 == 0
            else right_column
        )

        with target_column:
            render_category_detail(
                category_name=category_name,
                category_result=category_result,
                weight=weight,
            )

            st.write("")