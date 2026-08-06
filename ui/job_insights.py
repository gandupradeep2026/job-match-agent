import streamlit as st


def display_text_value(
    label: str,
    value: str,
) -> None:
    """
    Display a label and a text value.
    """

    st.write(f"**{label}:**")

    if value:
        st.write(value)
    else:
        st.caption("Not mentioned in the job description.")


def display_list_value(
    title: str,
    values: list[str],
    empty_message: str,
) -> None:
    """
    Display a list of extracted values.
    """

    st.subheader(title)

    if values:
        for value in values:
            st.write(f"- {value}")
    else:
        st.caption(empty_message)


def render_job_insights(
    extracted_job_details: dict,
) -> None:
    """
    Display information extracted from the job description
    by the local AI model.
    """

    st.divider()
    st.header("AI Job Insights")

    st.caption(
        "These details were extracted from the job description. "
        "Always verify them against the original advertisement."
    )

    summary = extracted_job_details.get(
        "summary",
        "",
    )

    if summary:
        st.subheader("Job Summary")
        st.info(summary)

    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:
        display_text_value(
            "Company",
            extracted_job_details.get(
                "company",
                "",
            ),
        )

        display_text_value(
            "Job title",
            extracted_job_details.get(
                "job_title",
                "",
            ),
        )

        display_text_value(
            "Location",
            extracted_job_details.get(
                "location",
                "",
            ),
        )

    with detail_col2:
        display_text_value(
            "Employment type",
            extracted_job_details.get(
                "employment_type",
                "",
            ),
        )

        display_text_value(
            "Work mode",
            extracted_job_details.get(
                "work_mode",
                "",
            ),
        )

        display_text_value(
            "Salary",
            extracted_job_details.get(
                "salary",
                "",
            ),
        )

    with detail_col3:
        display_text_value(
            "Application deadline",
            extracted_job_details.get(
                "application_deadline",
                "",
            ),
        )

        display_text_value(
            "Experience requirement",
            extracted_job_details.get(
                "experience_requirement",
                "",
            ),
        )

        display_text_value(
            "Visa sponsorship",
            extracted_job_details.get(
                "visa_sponsorship",
                "",
            ),
        )

    list_col1, list_col2 = st.columns(2)

    with list_col1:
        display_list_value(
            title="Required Skills",
            values=extracted_job_details.get(
                "required_skills",
                [],
            ),
            empty_message=(
                "No required skills were clearly extracted."
            ),
        )

    with list_col2:
        display_list_value(
            title="Preferred Skills",
            values=extracted_job_details.get(
                "preferred_skills",
                [],
            ),
            empty_message=(
                "No preferred skills were clearly extracted."
            ),
        )

    responsibility_col, language_col = st.columns(2)

    with responsibility_col:
        display_list_value(
            title="Responsibilities",
            values=extracted_job_details.get(
                "responsibilities",
                [],
            ),
            empty_message=(
                "No responsibilities were clearly extracted."
            ),
        )

    with language_col:
        display_list_value(
            title="Language Requirements",
            values=extracted_job_details.get(
                "required_languages",
                [],
            ),
            empty_message=(
                "No language requirements were mentioned."
            ),
        )

        st.subheader("Education Requirement")

        education_requirement = extracted_job_details.get(
            "education_requirement",
            "",
        )

        if education_requirement:
            st.write(education_requirement)
        else:
            st.caption(
                "No education requirement was clearly mentioned."
            )

    with st.expander(
        "Show extracted contact and application details"
    ):
        contact_col1, contact_col2 = st.columns(2)

        with contact_col1:
            display_text_value(
                "Contact name",
                extracted_job_details.get(
                    "contact_name",
                    "",
                ),
            )

            display_text_value(
                "Contact email",
                extracted_job_details.get(
                    "contact_email",
                    "",
                ),
            )

            display_text_value(
                "Contact phone",
                extracted_job_details.get(
                    "contact_phone",
                    "",
                ),
            )

        with contact_col2:
            display_text_value(
                "Job URL",
                extracted_job_details.get(
                    "job_url",
                    "",
                ),
            )