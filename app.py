import streamlit as st

from parsers.cv_parser import extract_document_text
from services.analysis_service import analyse_application
from services.job_tracker import (
    create_applications_table,
)
from ui.ai_recommendations import (
    render_ai_recommendations,
)
from ui.analysis_results import (
    render_analysis_results,
)
from ui.application_form import (
    render_application_form,
)
from ui.category_scores import (
    render_category_scores,
)
from ui.cover_letter_generator import (
    render_cover_letter_generator,
)
from ui.cv_generator import (
    render_cv_generator,
)
from ui.dashboard import (
    render_dashboard,
)
from ui.german_recruiter import (
    render_german_recruiter_report,
)
from ui.google_sheets_sync import (
    render_google_sheets_sync,
)
from ui.job_insights import (
    render_job_insights,
)
from ui.settings_page import (
    render_settings_page,
)
from ui.tracker_view import (
    render_tracker,
)


st.set_page_config(
    page_title="Job Match Agent",
    page_icon="📄",
    layout="wide",
)


create_applications_table()


st.title(
    "Job Match Agent"
)

st.write(
    "Analyse your CV against a job description, "
    "receive local AI recommendations, generate "
    "tailored application documents and track "
    "your applications."
)


saved_message = st.session_state.pop(
    "application_saved_message",
    None,
)

if saved_message:
    st.success(
        saved_message
    )


(
    analysis_tab,
    tracker_tab,
    dashboard_tab,
    cloud_tab,
    settings_tab,
) = st.tabs(
    [
        "Analyse Job",
        "Application Tracker",
        "Dashboard",
        "Google Sheets",
        "Settings",
    ]
)


# ==================================================
# ANALYSIS TAB
# ==================================================
with analysis_tab:
    st.subheader(
        "1. Provide your CV"
    )

    cv_input_method = st.radio(
        "Choose how you want to provide your CV:",
        [
            "Upload document",
            "Paste as text",
        ],
        horizontal=True,
        key="cv_input_method",
    )

    cv_file = None
    cv_text = ""

    if cv_input_method == "Upload document":
        cv_file = st.file_uploader(
            "Upload your CV",
            type=[
                "pdf",
                "docx",
                "txt",
            ],
            key="cv_file",
        )

    else:
        cv_text = st.text_area(
            "Paste your CV text",
            height=250,
            key="cv_text",
            placeholder=(
                "Paste the complete text "
                "of your CV here..."
            ),
        )

    st.subheader(
        "2. Provide the job description"
    )

    job_input_method = st.radio(
        (
            "Choose how you want to provide "
            "the job description:"
        ),
        [
            "Upload document",
            "Paste as text",
        ],
        horizontal=True,
        key="job_input_method",
    )

    job_file = None
    job_text = ""

    if job_input_method == "Upload document":
        job_file = st.file_uploader(
            "Upload the job description",
            type=[
                "pdf",
                "docx",
                "txt",
            ],
            key="job_file",
        )

    else:
        job_text = st.text_area(
            "Paste the job description",
            height=250,
            key="job_text",
            placeholder=(
                "Paste the complete job "
                "description here..."
            ),
        )

    if st.button(
        "Analyse",
        type="primary",
        use_container_width=True,
    ):
        try:
            # --------------------------------------
            # READ CV
            # --------------------------------------
            if cv_input_method == "Upload document":
                if cv_file is None:
                    st.error(
                        "Please upload your CV."
                    )
                    st.stop()

                final_cv_text = (
                    extract_document_text(
                        cv_file
                    )
                )

            else:
                final_cv_text = (
                    cv_text.strip()
                )

                if not final_cv_text:
                    st.error(
                        "Please paste your CV text."
                    )
                    st.stop()

            # --------------------------------------
            # READ JOB DESCRIPTION
            # --------------------------------------
            if job_input_method == "Upload document":
                if job_file is None:
                    st.error(
                        "Please upload the "
                        "job description."
                    )
                    st.stop()

                final_job_text = (
                    extract_document_text(
                        job_file
                    )
                )

            else:
                final_job_text = (
                    job_text.strip()
                )

                if not final_job_text:
                    st.error(
                        "Please paste the "
                        "job description."
                    )
                    st.stop()

            # --------------------------------------
            # RUN COMPLETE ANALYSIS
            # --------------------------------------
            with st.spinner(
                "Running skill analysis, ATS checks, "
                "German recruiter checks, job extraction "
                "and local AI recommendations..."
            ):
                analysis_result = (
                    analyse_application(
                        cv_text=final_cv_text,
                        job_text=final_job_text,
                    )
                )

            # --------------------------------------
            # STORE ANALYSIS RESULTS
            # --------------------------------------
            session_field_mapping = {
                "cv_text": "final_cv_text",
                "job_text": "final_job_text",
                "match_result": "match_result",
                "ats_result": "ats_result",
                "job_match_result": (
                    "job_match_result"
                ),
                "category_match_result": (
                    "category_match_result"
                ),
                "german_recruiter_report": (
                    "german_recruiter_report"
                ),
                "extracted_job_details": (
                    "extracted_job_details"
                ),
                "cv_recommendations": (
                    "cv_recommendations"
                ),
                "warnings": (
                    "analysis_warnings"
                ),
                "ai_extraction_used": (
                    "ai_extraction_used"
                ),
                "ai_extraction_error": (
                    "ai_extraction_error"
                ),
                "ai_recommendations_used": (
                    "ai_recommendations_used"
                ),
                "ai_recommendations_error": (
                    "ai_recommendations_error"
                ),
            }

            for result_key, session_key in (
                session_field_mapping.items()
            ):
                st.session_state[
                    session_key
                ] = analysis_result.get(
                    result_key
                )

            st.session_state[
                "analysis_complete"
            ] = True

            # Clear documents generated for an older analysis.
            keys_to_clear = [
                "generated_cover_letter",
                "cover_letter_warnings",
                "cover_letter_filename",
                "editable_cover_letter",
                "tailored_cv_text",
                "tailored_cv_docx",
                "tailored_cv_warnings",
                "tailored_cv_txt_filename",
                "tailored_cv_docx_filename",
                "editable_tailored_cv",
            ]

            for key in keys_to_clear:
                st.session_state.pop(
                    key,
                    None,
                )

            st.success(
                "Analysis completed successfully."
            )

        except Exception as error:
            st.error(
                f"Something went wrong: {error}"
            )

    # ----------------------------------------------
    # DISPLAY ANALYSIS
    # ----------------------------------------------
    if st.session_state.get(
        "analysis_complete"
    ):
        match_result = (
            st.session_state.get(
                "match_result",
                {},
            )
        )

        ats_result = (
            st.session_state.get(
                "ats_result",
                {},
            )
        )

        job_match_result = (
            st.session_state.get(
                "job_match_result",
                {},
            )
        )

        category_match_result = (
            st.session_state.get(
                "category_match_result",
                {},
            )
        )

        german_recruiter_report = (
            st.session_state.get(
                "german_recruiter_report",
                {},
            )
        )

        final_cv_text = (
            st.session_state.get(
                "final_cv_text",
                "",
            )
        )

        final_job_text = (
            st.session_state.get(
                "final_job_text",
                "",
            )
        )

        extracted_job_details = (
            st.session_state.get(
                "extracted_job_details",
                {},
            )
        )

        cv_recommendations = (
            st.session_state.get(
                "cv_recommendations",
                {},
            )
        )

        analysis_warnings = (
            st.session_state.get(
                "analysis_warnings",
                [],
            )
            or []
        )

        # ------------------------------------------
        # WARNINGS
        # ------------------------------------------
        for warning in analysis_warnings:
            st.warning(
                warning
            )

        # ------------------------------------------
        # AI EXTRACTION STATUS
        # ------------------------------------------
        ai_extraction_used = (
            st.session_state.get(
                "ai_extraction_used",
                False,
            )
        )

        if ai_extraction_used:
            st.success(
                "Local AI successfully extracted "
                "the job details."
            )

        else:
            st.warning(
                "Rule-based job extraction was used."
            )

            ai_extraction_error = (
                st.session_state.get(
                    "ai_extraction_error",
                    "",
                )
            )

            if ai_extraction_error:
                with st.expander(
                    "Show job-extraction error"
                ):
                    st.code(
                        ai_extraction_error
                    )

        # ------------------------------------------
        # JOB INSIGHTS
        # ------------------------------------------
        render_job_insights(
            extracted_job_details=(
                extracted_job_details
            )
        )

        # ------------------------------------------
        # GENERAL SCORES
        # ------------------------------------------
        render_analysis_results(
            match_result=match_result,
            ats_result=ats_result,
            job_match_result=job_match_result,
            cv_text=final_cv_text,
            job_text=final_job_text,
        )

        # ------------------------------------------
        # CATEGORY SCORES
        # ------------------------------------------
        render_category_scores(
            category_match_result=(
                category_match_result
            )
        )

        # ------------------------------------------
        # GERMAN RECRUITER REPORT
        # ------------------------------------------
        render_german_recruiter_report(
            report=(
                german_recruiter_report
            )
        )

        # ------------------------------------------
        # AI RECOMMENDATIONS
        # ------------------------------------------
        ai_recommendations_used = (
            st.session_state.get(
                "ai_recommendations_used",
                False,
            )
        )

        if ai_recommendations_used:
            render_ai_recommendations(
                recommendations=(
                    cv_recommendations
                )
            )

        else:
            st.warning(
                "Local AI CV recommendations "
                "were unavailable."
            )

            recommendation_error = (
                st.session_state.get(
                    "ai_recommendations_error",
                    "",
                )
            )

            if recommendation_error:
                with st.expander(
                    "Show recommendation error"
                ):
                    st.code(
                        recommendation_error
                    )

        # ------------------------------------------
        # TAILORED CV GENERATOR
        # ------------------------------------------
        render_cv_generator(
            cv_text=final_cv_text,
            job_text=final_job_text,
            extracted_job_details=(
                extracted_job_details
            ),
        )

        # ------------------------------------------
        # COVER-LETTER GENERATOR
        # ------------------------------------------
        render_cover_letter_generator(
            cv_text=final_cv_text,
            job_text=final_job_text,
            extracted_job_details=(
                extracted_job_details
            ),
        )

        # ------------------------------------------
        # VERIFY AND SAVE APPLICATION
        # ------------------------------------------
        render_application_form(
            extracted_job_details=(
                extracted_job_details
            ),
            match_result=match_result,
            ats_result=ats_result,
            job_match_result=job_match_result,
        )

    # ----------------------------------------------
    # SAVED APPLICATIONS
    # ----------------------------------------------
    st.divider()

    render_tracker(
        title="Saved Applications",
        show_heading=True,
        component_key="analysis_page",
    )


# ==================================================
# TRACKER TAB
# ==================================================
with tracker_tab:
    render_tracker(
        title="Application Tracker",
        show_heading=True,
        component_key="tracker_tab",
    )


# ==================================================
# DASHBOARD TAB
# ==================================================
with dashboard_tab:
    render_dashboard()


# ==================================================
# GOOGLE SHEETS TAB
# ==================================================
with cloud_tab:
    render_google_sheets_sync(
        component_key="google_tab",
    )


# ==================================================
# SETTINGS TAB
# ==================================================
with settings_tab:
    render_settings_page()