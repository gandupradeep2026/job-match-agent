import streamlit as st

from parsers.cv_parser import (
    extract_document_text_with_details,
)
from services.analysis_service import (
    analyse_application,
)
from services.job_tracker import (
    create_applications_table,
)
from services.logging_service import (
    configure_logging,
    get_logger,
    log_event,
    log_exception,
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
from ui.interview_coach import (
    render_interview_coach,
)
from ui.job_input import (
    render_job_description_input,
)
from ui.job_insights import (
    render_job_insights,
)
from ui.recruiter_decision import (
    render_recruiter_decision,
)
from ui.settings_page import (
    render_settings_page,
)
from ui.tracker_view import (
    render_tracker,
)


# ==================================================
# LOGGING
# ==================================================
configure_logging()

logger = get_logger(
    "app"
)


# ==================================================
# STREAMLIT CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Job Match Agent",
    page_icon="📄",
    layout="wide",
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================
def build_manual_extraction_details(
    method: str,
) -> dict:
    """
    Build extraction diagnostics for text that did
    not come from an uploaded document.
    """

    return {
        "method": method,
        "ocr_used": False,
        "warnings": [],
        "page_count": 0,
        "processed_pages": 0,
        "failed_pages": [],
        "languages": "",
        "dpi": 0,
        "filename": "",
        "file_type": "",
    }


def format_ocr_languages(
    language_codes: str,
) -> str:
    """
    Convert OCR language codes into readable labels.
    """

    language_labels = {
        "eng": "English",
        "deu": "German",
        "osd": "Orientation detection",
    }

    codes = [
        code.strip()
        for code in language_codes.split(
            "+"
        )
        if code.strip()
    ]

    readable_languages = [
        language_labels.get(
            code,
            code,
        )
        for code in codes
    ]

    return ", ".join(
        readable_languages
    )


def render_extraction_status(
    label: str,
    details: dict,
) -> None:
    """
    Display document extraction information.
    """

    if not details:
        st.caption(
            f"{label}: No extraction details are available."
        )

        return

    method = details.get(
        "method",
        "",
    )

    filename = details.get(
        "filename",
        "",
    )

    if filename:
        st.write(
            f"**File:** {filename}"
        )

    if details.get(
        "ocr_used",
        False,
    ):
        st.success(
            f"{label}: Tesseract OCR was used "
            "to read the scanned PDF."
        )

        processed_pages = details.get(
            "processed_pages",
            0,
        )

        total_pages = details.get(
            "page_count",
            0,
        )

        if total_pages:
            st.write(
                f"**Pages processed:** "
                f"{processed_pages} of {total_pages}"
            )

        elif processed_pages:
            st.write(
                f"**Pages processed:** "
                f"{processed_pages}"
            )

        language_codes = details.get(
            "languages",
            "",
        )

        if language_codes:
            st.write(
                f"**OCR languages:** "
                f"{format_ocr_languages(language_codes)}"
            )

        dpi = details.get(
            "dpi",
            0,
        )

        if dpi:
            st.write(
                f"**OCR resolution:** {dpi} DPI"
            )

        failed_pages = details.get(
            "failed_pages",
            [],
        )

        if failed_pages:
            with st.expander(
                f"{label}: Show failed OCR pages"
            ):
                for failed_page in failed_pages:
                    st.write(
                        f"Page "
                        f"{failed_page.get('page', '?')}: "
                        f"{failed_page.get('error', '')}"
                    )

    elif method == "direct_pdf_text":
        st.info(
            f"{label}: Selectable PDF text "
            "was extracted directly."
        )

    elif method == "docx":
        st.info(
            f"{label}: DOCX text was extracted."
        )

    elif method == "txt":
        st.info(
            f"{label}: TXT content was read."
        )

    elif method == "pasted_text":
        st.info(
            f"{label}: Text was pasted manually."
        )

    elif method == "imported_url":
        st.info(
            f"{label}: Text was imported from "
            "a public job URL."
        )

    else:
        st.info(
            f"{label}: Text extraction completed."
        )

    warnings = details.get(
        "warnings",
        [],
    ) or []

    for warning in warnings:
        st.warning(
            f"{label}: {warning}"
        )


# ==================================================
# DATABASE INITIALIZATION
# ==================================================
try:
    create_applications_table()

except Exception as error:
    log_exception(
        logger=logger,
        error=error,
        message=(
            "Database initialization failed."
        ),
    )

    st.error(
        "The local application database "
        "could not be initialized."
    )

    st.code(
        f"{type(error).__name__}: {error}"
    )

    st.stop()


# Log startup only once per Streamlit session.
if not st.session_state.get(
    "application_start_logged",
    False,
):
    log_event(
        logger=logger,
        message=(
            "Streamlit application started."
        ),
    )

    st.session_state[
        "application_start_logged"
    ] = True


# ==================================================
# PAGE HEADER
# ==================================================
st.title(
    "Job Match Agent"
)

st.write(
    "Analyse your CV against a job description, "
    "read scanned PDFs with OCR, import public job "
    "pages, receive local AI recommendations, "
    "generate tailored application documents, "
    "prepare for interviews and track your applications."
)


saved_message = st.session_state.pop(
    "application_saved_message",
    None,
)

if saved_message:
    st.success(
        saved_message
    )


# ==================================================
# MAIN TABS
# ==================================================
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
    # ==================================================
    # CV INPUT
    # ==================================================
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

        st.caption(
            "Scanned PDFs are read automatically "
            "with English and German OCR."
        )

    else:
        cv_text = st.text_area(
            "Paste your CV text",
            height=300,
            key="cv_text",
            placeholder=(
                "Paste the complete text "
                "of your CV here..."
            ),
        )

    # ==================================================
    # JOB DESCRIPTION INPUT
    # ==================================================
    job_input = (
        render_job_description_input()
    )

    job_input_method = job_input[
        "method"
    ]

    job_file = job_input[
        "file"
    ]

    job_text = job_input[
        "text"
    ]

    imported_job_url = job_input[
        "job_url"
    ]

    # ==================================================
    # ANALYSE BUTTON
    # ==================================================
    if st.button(
        "Analyse",
        type="primary",
        width="stretch",
        key="analyse_application_button",
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

                with st.spinner(
                    "Reading the CV document..."
                ):
                    cv_extraction_result = (
                        extract_document_text_with_details(
                            cv_file
                        )
                    )

                final_cv_text = (
                    cv_extraction_result[
                        "text"
                    ]
                )

                cv_extraction_details = (
                    cv_extraction_result[
                        "details"
                    ]
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

                cv_extraction_details = (
                    build_manual_extraction_details(
                        "pasted_text"
                    )
                )

            if not final_cv_text.strip():
                st.error(
                    "No readable text was extracted "
                    "from the CV."
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

                with st.spinner(
                    "Reading the job-description document..."
                ):
                    job_extraction_result = (
                        extract_document_text_with_details(
                            job_file
                        )
                    )

                final_job_text = (
                    job_extraction_result[
                        "text"
                    ]
                )

                job_extraction_details = (
                    job_extraction_result[
                        "details"
                    ]
                )

            else:
                final_job_text = (
                    job_text.strip()
                )

                if not final_job_text:
                    if (
                        job_input_method
                        == "Import public job URL"
                    ):
                        st.error(
                            "Please import a public "
                            "job page first."
                        )

                    else:
                        st.error(
                            "Please paste the "
                            "job description."
                        )

                    st.stop()

                if (
                    job_input_method
                    == "Import public job URL"
                ):
                    job_extraction_method = (
                        "imported_url"
                    )

                else:
                    job_extraction_method = (
                        "pasted_text"
                    )

                job_extraction_details = (
                    build_manual_extraction_details(
                        job_extraction_method
                    )
                )

            if not final_job_text.strip():
                st.error(
                    "No readable text was extracted "
                    "from the job description."
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
            # PRESERVE IMPORTED JOB URL
            # --------------------------------------
            if imported_job_url:
                extracted_details = (
                    analysis_result.get(
                        "extracted_job_details",
                        {},
                    )
                    or {}
                )

                extracted_details[
                    "job_url"
                ] = imported_job_url

                analysis_result[
                    "extracted_job_details"
                ] = extracted_details

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
                "recruiter_decision": (
                    "recruiter_decision"
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
                "cv_extraction_details"
            ] = cv_extraction_details

            st.session_state[
                "job_extraction_details"
            ] = job_extraction_details

            st.session_state[
                "analysis_complete"
            ] = True

            st.session_state[
                "analysis_source_method"
            ] = job_input_method

            st.session_state[
                "analysis_imported_job_url"
            ] = imported_job_url

            # Clear generated results from the previous analysis.
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
                "interview_coach_result",
            ]

            for key in keys_to_clear:
                st.session_state.pop(
                    key,
                    None,
                )

            extracted_details = (
                analysis_result.get(
                    "extracted_job_details",
                    {},
                )
                or {}
            )

            log_event(
                logger=logger,
                message=(
                    "Application analysis completed."
                ),
                context={
                    "job_input_method": (
                        job_input_method
                    ),
                    "cv_extraction_method": (
                        cv_extraction_details.get(
                            "method",
                            "",
                        )
                    ),
                    "cv_ocr_used": (
                        cv_extraction_details.get(
                            "ocr_used",
                            False,
                        )
                    ),
                    "job_extraction_method": (
                        job_extraction_details.get(
                            "method",
                            "",
                        )
                    ),
                    "job_ocr_used": (
                        job_extraction_details.get(
                            "ocr_used",
                            False,
                        )
                    ),
                    "company": (
                        extracted_details.get(
                            "company",
                            "",
                        )
                    ),
                    "job_title": (
                        extracted_details.get(
                            "job_title",
                            "",
                        )
                    ),
                    "ai_extraction_used": (
                        analysis_result.get(
                            "ai_extraction_used",
                            False,
                        )
                    ),
                    "ai_recommendations_used": (
                        analysis_result.get(
                            "ai_recommendations_used",
                            False,
                        )
                    ),
                },
            )

            st.success(
                "Analysis completed successfully."
            )

        except Exception as error:
            log_exception(
                logger=logger,
                error=error,
                message=(
                    "Application analysis failed."
                ),
                context={
                    "cv_input_method": (
                        cv_input_method
                    ),
                    "job_input_method": (
                        job_input_method
                    ),
                    "imported_job_url": (
                        imported_job_url
                    ),
                },
            )

            st.error(
                "The analysis could not be completed."
            )

            st.code(
                f"{type(error).__name__}: {error}"
            )

            st.info(
                "More diagnostic information was saved "
                "in Settings → Logs."
            )

    # ==================================================
    # DISPLAY ANALYSIS
    # ==================================================
    if st.session_state.get(
        "analysis_complete"
    ):
        match_result = (
            st.session_state.get(
                "match_result",
                {},
            )
            or {}
        )

        ats_result = (
            st.session_state.get(
                "ats_result",
                {},
            )
            or {}
        )

        job_match_result = (
            st.session_state.get(
                "job_match_result",
                {},
            )
            or {}
        )

        category_match_result = (
            st.session_state.get(
                "category_match_result",
                {},
            )
            or {}
        )

        german_recruiter_report = (
            st.session_state.get(
                "german_recruiter_report",
                {},
            )
            or {}
        )

        recruiter_decision = (
            st.session_state.get(
                "recruiter_decision",
                {},
            )
            or {}
        )

        final_cv_text = (
            st.session_state.get(
                "final_cv_text",
                "",
            )
            or ""
        )

        final_job_text = (
            st.session_state.get(
                "final_job_text",
                "",
            )
            or ""
        )

        extracted_job_details = (
            st.session_state.get(
                "extracted_job_details",
                {},
            )
            or {}
        )

        cv_recommendations = (
            st.session_state.get(
                "cv_recommendations",
                {},
            )
            or {}
        )

        analysis_warnings = (
            st.session_state.get(
                "analysis_warnings",
                [],
            )
            or []
        )

        analysis_source_method = (
            st.session_state.get(
                "analysis_source_method",
                "",
            )
        )

        analysis_imported_job_url = (
            st.session_state.get(
                "analysis_imported_job_url",
                "",
            )
        )

        cv_extraction_details = (
            st.session_state.get(
                "cv_extraction_details",
                {},
            )
            or {}
        )

        job_extraction_details = (
            st.session_state.get(
                "job_extraction_details",
                {},
            )
            or {}
        )

        # ------------------------------------------
        # DOCUMENT EXTRACTION STATUS
        # ------------------------------------------
        st.divider()

        st.subheader(
            "Document Extraction Status"
        )

        extraction_col1, extraction_col2 = (
            st.columns(2)
        )

        with extraction_col1:
            render_extraction_status(
                label="CV",
                details=(
                    cv_extraction_details
                ),
            )

        with extraction_col2:
            render_extraction_status(
                label="Job description",
                details=(
                    job_extraction_details
                ),
            )

        # ------------------------------------------
        # INPUT SOURCE STATUS
        # ------------------------------------------
        st.divider()

        if analysis_source_method:
            st.info(
                f"Job-description source: "
                f"{analysis_source_method}"
            )

        if analysis_imported_job_url:
            st.write(
                f"**Imported job URL:** "
                f"{analysis_imported_job_url}"
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
        # GENERAL ANALYSIS
        # ------------------------------------------
        render_analysis_results(
            match_result=match_result,
            ats_result=ats_result,
            job_match_result=job_match_result,
            cv_text=final_cv_text,
            job_text=final_job_text,
        )

        # ------------------------------------------
        # AI RECRUITER DECISION
        # ------------------------------------------
        render_recruiter_decision(
            report=recruiter_decision
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
        # AI INTERVIEW COACH
        # ------------------------------------------
        render_interview_coach(
            cv_text=final_cv_text,
            job_text=final_job_text,
            extracted_job_details=(
                extracted_job_details
            ),
            match_result=match_result,
            category_match_result=(
                category_match_result
            ),
            german_recruiter_report=(
                german_recruiter_report
            ),
        )

        # ------------------------------------------
        # AI CV RECOMMENDATIONS
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

    # ==================================================
    # SAVED APPLICATIONS
    # ==================================================
    st.divider()

    try:
        render_tracker(
            title="Saved Applications",
            show_heading=True,
            component_key="analysis_page",
        )

    except Exception as error:
        log_exception(
            logger=logger,
            error=error,
            message=(
                "Saved applications could not be rendered."
            ),
            context={
                "component": "analysis_page",
            },
        )

        st.error(
            "Saved applications could not be displayed."
        )


# ==================================================
# TRACKER TAB
# ==================================================
with tracker_tab:
    try:
        render_tracker(
            title="Application Tracker",
            show_heading=True,
            component_key="tracker_tab",
        )

    except Exception as error:
        log_exception(
            logger=logger,
            error=error,
            message=(
                "Application tracker could not be rendered."
            ),
            context={
                "component": "tracker_tab",
            },
        )

        st.error(
            "The application tracker could not be displayed."
        )

        st.info(
            "See Settings → Logs for diagnostic information."
        )


# ==================================================
# DASHBOARD TAB
# ==================================================
with dashboard_tab:
    try:
        render_dashboard()

    except Exception as error:
        log_exception(
            logger=logger,
            error=error,
            message=(
                "Dashboard rendering failed."
            ),
            context={
                "component": "dashboard",
            },
        )

        st.error(
            "The dashboard could not be displayed."
        )

        st.info(
            "See Settings → Logs for diagnostic information."
        )


# ==================================================
# GOOGLE SHEETS TAB
# ==================================================
with cloud_tab:
    try:
        render_google_sheets_sync(
            component_key="google_tab",
        )

    except Exception as error:
        log_exception(
            logger=logger,
            error=error,
            message=(
                "Google Sheets interface failed."
            ),
            context={
                "component": "google_sheets",
            },
        )

        st.error(
            "The Google Sheets interface "
            "could not be displayed."
        )

        st.info(
            "See Settings → Logs for diagnostic information."
        )


# ==================================================
# SETTINGS TAB
# ==================================================
with settings_tab:
    try:
        render_settings_page()

    except Exception as error:
        log_exception(
            logger=logger,
            error=error,
            message=(
                "Settings page rendering failed."
            ),
            context={
                "component": "settings",
            },
        )

        st.error(
            "The settings page could not be displayed."
        )

        st.code(
            f"{type(error).__name__}: {error}"
        )