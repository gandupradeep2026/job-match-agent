from datetime import date, timedelta

import streamlit as st

from services.job_tracker import (
    find_possible_duplicates,
    save_application,
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


def render_duplicate_warning(
    duplicates: list[dict],
) -> None:
    """
    Display possible duplicate application records.
    """

    if not duplicates:
        return

    st.error(
        "This application may already exist "
        "in your tracker."
    )

    for duplicate in duplicates:
        application = duplicate[
            "application"
        ]

        confidence = duplicate[
            "confidence"
        ].title()

        reasons = ", ".join(
            duplicate[
                "reasons"
            ]
        )

        st.write(
            f"**ID {application.get('id')} — "
            f"{application.get('company')} — "
            f"{application.get('job_title')}**"
        )

        st.write(
            f"Confidence: {confidence}"
        )

        st.write(
            f"Matched because: "
            f"{reasons or 'Similar information'}"
        )

        st.write(
            "Existing application date: "
            f"{application.get('application_date', '')}"
        )

        st.write(
            "Existing status: "
            f"{application.get('status', '')}"
        )

        st.divider()


def render_application_form(
    extracted_job_details: dict,
    match_result: dict,
    ats_result: dict,
    job_match_result: dict,
) -> None:
    """
    Display the verification form.

    Nothing is saved until the user verifies the
    application and presses the save button.
    """

    st.divider()

    st.subheader(
        "Verify Extracted Job Details"
    )

    st.info(
        "Review and correct the information below. "
        "Nothing enters the tracker until you save it."
    )

    with st.form(
        "verify_and_save_application_form"
    ):
        form_col1, form_col2 = (
            st.columns(2)
        )

        with form_col1:
            company = st.text_input(
                "Company name *",
                value=(
                    extracted_job_details.get(
                        "company",
                        "",
                    )
                    or ""
                ),
            )

            job_title = st.text_input(
                "Job title *",
                value=(
                    extracted_job_details.get(
                        "job_title",
                        "",
                    )
                    or ""
                ),
            )

            location = st.text_input(
                "Location",
                value=(
                    extracted_job_details.get(
                        "location",
                        "",
                    )
                    or ""
                ),
            )

            application_date = (
                st.date_input(
                    "Application date",
                    value=date.today(),
                )
            )

            status = st.selectbox(
                "Application status",
                APPLICATION_STATUSES,
                index=1,
            )

            application_source = (
                st.selectbox(
                    "Application source",
                    APPLICATION_SOURCES,
                )
            )

        with form_col2:
            job_url = st.text_input(
                "Job URL",
                value=(
                    extracted_job_details.get(
                        "job_url",
                        "",
                    )
                    or ""
                ),
            )

            contact_name = st.text_input(
                "Contact name",
                value=(
                    extracted_job_details.get(
                        "contact_name",
                        "",
                    )
                    or ""
                ),
            )

            contact_email = st.text_input(
                "Contact email",
                value=(
                    extracted_job_details.get(
                        "contact_email",
                        "",
                    )
                    or ""
                ),
            )

            contact_phone = st.text_input(
                "Contact phone",
                value=(
                    extracted_job_details.get(
                        "contact_phone",
                        "",
                    )
                    or ""
                ),
            )

            cv_version = st.text_input(
                "CV version used",
                placeholder=(
                    "Example: "
                    "CV_Systemintegration_v2"
                ),
            )

            cover_letter_version = (
                st.text_input(
                    "Cover-letter version used",
                    placeholder=(
                        "Example: "
                        "Anschreiben_Company_v1"
                    ),
                )
            )

        st.write(
            "### Follow-up planning"
        )

        follow_up_col1, follow_up_col2 = (
            st.columns(2)
        )

        with follow_up_col1:
            has_last_follow_up = (
                st.checkbox(
                    "I have already followed up",
                    value=False,
                    key=(
                        "new_has_last_follow_up"
                    ),
                )
            )

            if has_last_follow_up:
                last_follow_up_date = (
                    st.date_input(
                        "Last follow-up date",
                        value=date.today(),
                        key=(
                            "new_last_follow_up_date"
                        ),
                    )
                )

            else:
                last_follow_up_date = (
                    None
                )

        with follow_up_col2:
            plan_follow_up = (
                st.checkbox(
                    "Plan a follow-up",
                    value=True,
                    key=(
                        "new_plan_follow_up"
                    ),
                )
            )

            if plan_follow_up:
                next_follow_up_date = (
                    st.date_input(
                        "Next follow-up date",
                        value=(
                            application_date
                            + timedelta(
                                days=7
                            )
                        ),
                        key=(
                            "new_next_follow_up_date"
                        ),
                    )
                )

            else:
                next_follow_up_date = (
                    None
                )

        notes = st.text_area(
            "Notes",
            height=120,
            placeholder=(
                "Add interview information, "
                "recruiter notes, required documents "
                "or other important details."
            ),
        )

        st.write(
            "### Duplicate protection"
        )

        allow_duplicate = st.checkbox(
            (
                "Save this application even if a "
                "possible duplicate is found"
            ),
            value=False,
            help=(
                "Enable this only when you are intentionally "
                "saving a second application for the same "
                "or a very similar position."
            ),
        )

        save_button = (
            st.form_submit_button(
                "Check and Save Application",
                type="primary",
                width="stretch",
            )
        )

        if save_button:
            if not company.strip():
                st.error(
                    "Please enter the company name."
                )

                return

            if not job_title.strip():
                st.error(
                    "Please enter the job title."
                )

                return

            possible_duplicates = (
                find_possible_duplicates(
                    company=company,
                    job_title=job_title,
                    location=location,
                    job_url=job_url,
                )
            )

            if (
                possible_duplicates
                and not allow_duplicate
            ):
                render_duplicate_warning(
                    possible_duplicates
                )

                st.warning(
                    "Review the existing records above. "
                    "To save anyway, enable the duplicate "
                    "override checkbox and submit again."
                )

                return

            application_id = (
                save_application(
                    company=company,
                    job_title=job_title,
                    location=location,
                    application_date=(
                        application_date.isoformat()
                    ),
                    status=status,
                    job_url=job_url,
                    contact_name=contact_name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    skill_match_score=float(
                        match_result.get(
                            "score",
                            0.0,
                        )
                    ),
                    ats_score=float(
                        ats_result.get(
                            "score",
                            0.0,
                        )
                    ),
                    overall_match_score=float(
                        job_match_result.get(
                            "score",
                            0.0,
                        )
                    ),
                    notes=notes,
                    last_follow_up_date=(
                        last_follow_up_date.isoformat()
                        if last_follow_up_date
                        else ""
                    ),
                    next_follow_up_date=(
                        next_follow_up_date.isoformat()
                        if next_follow_up_date
                        else ""
                    ),
                    application_source=(
                        application_source
                    ),
                    cv_version=cv_version,
                    cover_letter_version=(
                        cover_letter_version
                    ),
                )
            )

            if possible_duplicates:
                saved_message = (
                    "Application saved with duplicate "
                    "override enabled. "
                    f"Application ID: {application_id}"
                )

            else:
                saved_message = (
                    "Application saved successfully. "
                    f"Application ID: {application_id}"
                )

            st.session_state[
                "application_saved_message"
            ] = saved_message

            st.rerun()