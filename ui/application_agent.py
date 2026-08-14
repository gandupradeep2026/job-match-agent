from __future__ import annotations

from datetime import date

import streamlit as st

from services.application_answer_service import (
    generate_application_answer,
)
from services.application_browser import (
    open_job_page,
    preview_autofill_job_page,
)
from services.application_review_launcher import (
    launch_application_review,
)
from services.job_tracker import (
    find_possible_duplicates,
    save_application,
)
from services.logging_service import (
    log_event,
    log_exception,
)


PROFILE_MAPPING_OPTIONS = [
    "Auto detect",
    "Do not fill",
    "Custom answer",
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "address",
    "postal_code",
    "city",
    "country",
    "location",
    "linkedin",
    "github",
    "portfolio",
    "work_authorization",
    "visa_sponsorship",
    "salary_expectation",
    "notice_period",
    "availability_date",
    "years_experience",
    "german_level",
    "english_level",
    "resume",
    "cover_letter",
]


def _reset_application_agent_state() -> None:
    prefixes = (
        "application_agent_",
    )

    protected_keys = {
        "application_agent_reset",
        "application_agent_load_latest_job",
    }

    keys_to_remove = [
        key
        for key in st.session_state.keys()
        if (
            key.startswith(
                prefixes
            )
            and key
            not in protected_keys
        )
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None,
        )


def _clear_mapping_state() -> None:
    mapping_prefixes = (
        "application_agent_field_mapping_",
        "application_agent_custom_answer_",
        "application_agent_ai_answer_",
    )

    keys_to_remove = [
        key
        for key in st.session_state.keys()
        if key.startswith(
            mapping_prefixes
        )
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None,
        )

    st.session_state.pop(
        "application_agent_autofill_preview",
        None,
    )


def _build_resume_payload(
    resume_upload,
) -> dict | None:
    if resume_upload is None:
        return None

    return {
        "name": resume_upload.name,
        "mimeType": (
            resume_upload.type
            or "application/octet-stream"
        ),
        "buffer": resume_upload.getvalue(),
    }


def _browser_profile(
    applicant_profile: dict,
) -> dict:
    return {
        key: value
        for key, value
        in applicant_profile.items()
        if key != "resume"
    }


def _extract_numeric_score(
    value,
    candidate_keys: list[str],
) -> float:
    if not isinstance(
        value,
        dict,
    ):
        return 0.0

    for key in candidate_keys:
        candidate = value.get(
            key
        )

        if isinstance(
            candidate,
            (
                int,
                float,
            ),
        ):
            return float(
                candidate
            )

        if isinstance(
            candidate,
            str,
        ):
            cleaned = (
                candidate.strip()
                .replace(
                    "%",
                    "",
                )
            )

            try:
                return float(
                    cleaned
                )

            except ValueError:
                continue

    return 0.0


def _effective_mapping(
    detected_key: str,
    mapping_choice: str,
) -> tuple[str, str | None]:
    if mapping_choice == "Auto detect":
        return (
            detected_key,
            None,
        )

    if mapping_choice == "Do not fill":
        return (
            "skip",
            "__skip__",
        )

    if mapping_choice == "Custom answer":
        return (
            "custom_answer",
            "__custom__",
        )

    return (
        mapping_choice,
        mapping_choice,
    )


def _profile_status(
    effective_key: str,
    applicant_profile: dict,
    custom_answer: str,
) -> str:
    if effective_key == "skip":
        return "Skipped by user"

    if effective_key == "unknown":
        return "Needs review"

    if effective_key == "custom_answer":
        if custom_answer.strip():
            return "Ready"

        return "Missing custom answer"

    if applicant_profile.get(
        effective_key
    ):
        return "Ready"

    return "Missing profile data"


def _load_latest_analysed_job() -> bool:
    details = (
        st.session_state.get(
            "extracted_job_details",
            {},
        )
        or {}
    )

    if not details:
        return False

    st.session_state[
        "application_agent_company"
    ] = details.get(
        "company",
        "",
    )

    st.session_state[
        "application_agent_job_title"
    ] = details.get(
        "job_title",
        "",
    )

    job_url = (
        details.get(
            "job_url",
            "",
        )
        or st.session_state.get(
            "analysis_imported_job_url",
            "",
        )
        or ""
    )

    if job_url:
        st.session_state[
            "application_agent_job_url"
        ] = job_url

    location = details.get(
        "location",
        "",
    )

    if (
        location
        and not st.session_state.get(
            "application_agent_location"
        )
    ):
        st.session_state[
            "application_agent_location"
        ] = location

    return True


def render_application_agent(
    logger=None,
) -> None:
    st.header(
        "Application Agent"
    )

    st.write(
        "Inspect an application form, map it to your profile, "
        "generate cautious AI answer suggestions, preview the "
        "auto-fill, and open a filled browser for final manual review."
    )

    st.warning(
        "The agent never clicks Submit, Apply, Continue, consent "
        "checkboxes, or radio buttons. You remain responsible for "
        "reviewing every answer and submitting the application manually."
    )

    action_col1, action_col2 = (
        st.columns(2)
    )

    with action_col1:
        if st.button(
            "Load latest analysed job",
            key=(
                "application_agent_load_latest_job"
            ),
            width="stretch",
        ):
            if _load_latest_analysed_job():
                _clear_mapping_state()

                st.success(
                    "Loaded the latest analysed job data."
                )

            else:
                st.info(
                    "No analysed job is available yet."
                )

    with action_col2:
        if st.button(
            "Reset Application Agent",
            key=(
                "application_agent_reset"
            ),
            width="stretch",
        ):
            _reset_application_agent_state()
            st.rerun()

    st.divider()

    # ==================================================
    # 1. JOB
    # ==================================================
    st.subheader(
        "1. Job"
    )

    application_job_url = st.text_input(
        "Job application URL",
        placeholder=(
            "https://company.com/jobs/12345"
        ),
        key="application_agent_job_url",
    )

    job_col1, job_col2 = (
        st.columns(2)
    )

    with job_col1:
        application_company = (
            st.text_input(
                "Company",
                placeholder="Example: Siemens",
                key=(
                    "application_agent_company"
                ),
            )
        )

    with job_col2:
        application_job_title = (
            st.text_input(
                "Job title",
                placeholder=(
                    "Example: Data Engineer"
                ),
                key=(
                    "application_agent_job_title"
                ),
            )
        )

    if (
        application_job_url.strip()
        and application_job_url.strip().startswith(
            (
                "http://",
                "https://",
            )
        )
    ):
        st.link_button(
            "Open job page manually",
            application_job_url.strip(),
        )

    if st.button(
        "Inspect Job Page",
        type="primary",
        key=(
            "application_agent_inspect_job_page"
        ),
    ):
        if not application_job_url.strip():
            st.warning(
                "Enter a job application URL first."
            )

        else:
            try:
                with st.spinner(
                    "Inspecting the job page and form fields..."
                ):
                    page_result = (
                        open_job_page(
                            application_job_url
                        )
                    )

                st.session_state[
                    "application_agent_page_result"
                ] = page_result

                st.session_state[
                    "application_agent_inspected_url"
                ] = (
                    application_job_url.strip()
                )

                _clear_mapping_state()

                if logger is not None:
                    log_event(
                        logger=logger,
                        message=(
                            "Application Agent "
                            "job page inspected."
                        ),
                        context={
                            "job_url": (
                                application_job_url
                            ),
                            "field_count": (
                                page_result.get(
                                    "field_count",
                                    0,
                                )
                            ),
                            "login_required": (
                                page_result.get(
                                    "login_required",
                                    False,
                                )
                            ),
                        },
                    )

            except Exception as error:
                st.session_state.pop(
                    "application_agent_page_result",
                    None,
                )

                if logger is not None:
                    log_exception(
                        logger=logger,
                        error=error,
                        message=(
                            "Application Agent "
                            "job inspection failed."
                        ),
                        context={
                            "job_url": (
                                application_job_url
                            ),
                        },
                    )

                st.error(
                    "The job page could not be inspected."
                )

                st.code(
                    f"{type(error).__name__}: "
                    f"{error}"
                )

    page_result = (
        st.session_state.get(
            "application_agent_page_result"
        )
    )

    inspected_url = (
        st.session_state.get(
            "application_agent_inspected_url",
            "",
        )
    )

    detected_fields = []

    if page_result:
        if (
            application_job_url.strip()
            and inspected_url
            and application_job_url.strip()
            != inspected_url
        ):
            st.warning(
                "The current inspection belongs to a previous URL. "
                "Inspect the new URL before generating a preview."
            )

        if page_result.get(
            "login_required"
        ):
            st.warning(
                "The page redirected to a sign-in screen. "
                "No application fields were inspected or filled."
            )

        else:
            st.success(
                "Job page inspected successfully."
            )

        st.write(
            f"**Page title:** "
            f"{page_result.get('title', '')}"
        )

        st.write(
            f"**Final URL:** "
            f"{page_result.get('url', '')}"
        )

        detected_fields = (
            page_result.get(
                "fields",
                [],
            )
            or []
        )

        if detected_fields:
            st.write(
                f"**Detected fields:** "
                f"{len(detected_fields)}"
            )

            with st.expander(
                "Show detected fields"
            ):
                for field_number, field in enumerate(
                    detected_fields,
                    start=1,
                ):
                    field_label = (
                        field.get(
                            "label",
                            "Unnamed field",
                        )
                    )

                    field_type = (
                        field.get(
                            "type",
                            "unknown",
                        )
                    )

                    field_key = (
                        field.get(
                            "field_key",
                            "unknown",
                        )
                    )

                    required_text = (
                        "Required"
                        if field.get(
                            "required"
                        )
                        else "Optional"
                    )

                    st.write(
                        f"**{field_number}. "
                        f"{field_label}** "
                        f"— `{field_type}` "
                        f"— `{field_key}` "
                        f"— {required_text}"
                    )

        elif not page_result.get(
            "login_required"
        ):
            st.info(
                "No standard HTML application fields were detected."
            )

    st.divider()

    # ==================================================
    # 2. PROFILE
    # ==================================================
    st.subheader(
        "2. Applicant Profile"
    )

    contact_col1, contact_col2 = (
        st.columns(2)
    )

    with contact_col1:
        first_name = st.text_input(
            "First name",
            key=(
                "application_agent_first_name"
            ),
        )

        email = st.text_input(
            "Email",
            key=(
                "application_agent_email"
            ),
        )

        phone = st.text_input(
            "Phone",
            key=(
                "application_agent_phone"
            ),
        )

        address = st.text_input(
            "Street address",
            key=(
                "application_agent_address"
            ),
        )

        postal_code = st.text_input(
            "Postal code",
            key=(
                "application_agent_postal_code"
            ),
        )

    with contact_col2:
        last_name = st.text_input(
            "Last name",
            key=(
                "application_agent_last_name"
            ),
        )

        city = st.text_input(
            "City",
            key=(
                "application_agent_city"
            ),
        )

        country = st.text_input(
            "Country",
            key=(
                "application_agent_country"
            ),
        )

        location = st.text_input(
            "Current location",
            placeholder=(
                "Example: Chemnitz, Germany"
            ),
            key=(
                "application_agent_location"
            ),
        )

    links_col1, links_col2, links_col3 = (
        st.columns(3)
    )

    with links_col1:
        linkedin = st.text_input(
            "LinkedIn URL",
            key=(
                "application_agent_linkedin"
            ),
        )

    with links_col2:
        github = st.text_input(
            "GitHub URL",
            key=(
                "application_agent_github"
            ),
        )

    with links_col3:
        portfolio = st.text_input(
            "Portfolio / Website",
            key=(
                "application_agent_portfolio"
            ),
        )

    employment_col1, employment_col2 = (
        st.columns(2)
    )

    with employment_col1:
        work_authorization_choice = (
            st.selectbox(
                "Authorized to work for this role?",
                [
                    "Not specified",
                    "Yes",
                    "No",
                ],
                key=(
                    "application_agent_"
                    "work_authorization"
                ),
            )
        )

        salary_expectation = (
            st.text_input(
                "Salary expectation",
                placeholder=(
                    "Example: 55,000 EUR gross/year"
                ),
                key=(
                    "application_agent_"
                    "salary_expectation"
                ),
            )
        )

        availability_date = (
            st.text_input(
                "Available start date",
                placeholder="YYYY-MM-DD",
                key=(
                    "application_agent_"
                    "availability_date"
                ),
            )
        )

        german_level = st.text_input(
            "German level",
            placeholder=(
                "Example: B1"
            ),
            key=(
                "application_agent_german_level"
            ),
        )

    with employment_col2:
        visa_sponsorship_choice = (
            st.selectbox(
                "Require visa sponsorship?",
                [
                    "Not specified",
                    "Yes",
                    "No",
                ],
                key=(
                    "application_agent_"
                    "visa_sponsorship"
                ),
            )
        )

        notice_period = st.text_input(
            "Notice period",
            placeholder=(
                "Example: 4 weeks"
            ),
            key=(
                "application_agent_notice_period"
            ),
        )

        years_experience = (
            st.text_input(
                "Years of professional experience",
                placeholder="Example: 3",
                key=(
                    "application_agent_"
                    "years_experience"
                ),
            )
        )

        english_level = st.text_input(
            "English level",
            placeholder=(
                "Example: C1"
            ),
            key=(
                "application_agent_english_level"
            ),
        )

    application_resume = st.file_uploader(
        "Resume / CV",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
        key=(
            "application_agent_resume"
        ),
    )

    cover_letter = st.text_area(
        "Cover letter / motivation text",
        height=180,
        key=(
            "application_agent_cover_letter"
        ),
    )

    application_notes = st.text_area(
        "Private tracker notes",
        height=100,
        key=(
            "application_agent_notes"
        ),
    )

    full_name = " ".join(
        part
        for part in [
            first_name.strip(),
            last_name.strip(),
        ]
        if part.strip()
    )

    work_authorization = (
        ""
        if work_authorization_choice
        == "Not specified"
        else work_authorization_choice
    )

    visa_sponsorship = (
        ""
        if visa_sponsorship_choice
        == "Not specified"
        else visa_sponsorship_choice
    )

    applicant_profile = {
        "first_name": (
            first_name.strip()
        ),
        "last_name": (
            last_name.strip()
        ),
        "full_name": full_name,
        "email": email.strip(),
        "phone": phone.strip(),
        "address": address.strip(),
        "postal_code": (
            postal_code.strip()
        ),
        "city": city.strip(),
        "country": country.strip(),
        "location": (
            location.strip()
        ),
        "linkedin": (
            linkedin.strip()
        ),
        "github": github.strip(),
        "portfolio": (
            portfolio.strip()
        ),
        "work_authorization": (
            work_authorization
        ),
        "visa_sponsorship": (
            visa_sponsorship
        ),
        "salary_expectation": (
            salary_expectation.strip()
        ),
        "notice_period": (
            notice_period.strip()
        ),
        "availability_date": (
            availability_date.strip()
        ),
        "years_experience": (
            years_experience.strip()
        ),
        "german_level": (
            german_level.strip()
        ),
        "english_level": (
            english_level.strip()
        ),
        "resume": (
            application_resume
        ),
        "cover_letter": (
            cover_letter.strip()
        ),
    }

    st.divider()

    # ==================================================
    # 3. MAPPING AND CUSTOM ANSWERS
    # ==================================================
    st.subheader(
        "3. Field Mapping and Application Questions"
    )

    field_mapping_overrides = {}
    custom_answers = {}

    ready_count = 0
    missing_count = 0
    review_count = 0
    skipped_count = 0

    if not page_result:
        st.info(
            "Inspect a job page first."
        )

    elif page_result.get(
        "login_required"
    ):
        st.info(
            "Field mapping is unavailable because the page "
            "requires sign-in."
        )

    elif not detected_fields:
        st.info(
            "No detected application fields are available to map."
        )

    else:
        ai_cv_text = (
            st.session_state.get(
                "final_cv_text",
                "",
            )
            or ""
        )

        ai_job_text = (
            page_result.get(
                "page_text",
                "",
            )
            or st.session_state.get(
                "final_job_text",
                "",
            )
            or ""
        )

        if ai_cv_text:
            st.caption(
                "AI answer suggestions can use the CV text from "
                "your latest Analyse Job result."
            )

        else:
            st.caption(
                "AI answer suggestions currently have no analysed "
                "CV text, so factual answers will rely only on the "
                "profile fields above."
            )

        for field_number, field in enumerate(
            detected_fields,
            start=1,
        ):
            field_index = int(
                field.get(
                    "index",
                    field_number - 1,
                )
            )

            field_label = (
                field.get(
                    "label",
                    "Unnamed field",
                )
            )

            field_type = (
                field.get(
                    "type",
                    "unknown",
                )
            )

            detected_key = (
                field.get(
                    "field_key",
                    "unknown",
                )
            )

            with st.container(
                border=True
            ):
                st.write(
                    f"**{field_number}. "
                    f"{field_label}**"
                )

                st.caption(
                    f"Detected type: {field_type} · "
                    f"Automatic mapping: {detected_key}"
                )

                mapping_choice = (
                    st.selectbox(
                        "Mapping",
                        PROFILE_MAPPING_OPTIONS,
                        key=(
                            "application_agent_"
                            "field_mapping_"
                            f"{field_index}"
                        ),
                    )
                )

                (
                    effective_key,
                    override_value,
                ) = _effective_mapping(
                    detected_key=(
                        detected_key
                    ),
                    mapping_choice=(
                        mapping_choice
                    ),
                )

                if (
                    override_value
                    is not None
                ):
                    field_mapping_overrides[
                        str(
                            field_index
                        )
                    ] = override_value

                custom_answer = ""

                if (
                    effective_key
                    == "custom_answer"
                ):
                    custom_key = (
                        "application_agent_"
                        "custom_answer_"
                        f"{field_index}"
                    )

                    if st.button(
                        "Generate local AI suggestion",
                        key=(
                            "application_agent_"
                            "ai_answer_"
                            f"{field_index}"
                        ),
                    ):
                        try:
                            with st.spinner(
                                "Generating a cautious answer suggestion..."
                            ):
                                suggestion = (
                                    generate_application_answer(
                                        question=(
                                            field_label
                                        ),
                                        applicant_profile=(
                                            applicant_profile
                                        ),
                                        cv_text=(
                                            ai_cv_text
                                        ),
                                        job_text=(
                                            ai_job_text
                                        ),
                                        company=(
                                            application_company
                                        ),
                                        job_title=(
                                            application_job_title
                                        ),
                                    )
                                )

                            st.session_state[
                                custom_key
                            ] = suggestion

                        except Exception as error:
                            if logger is not None:
                                log_exception(
                                    logger=logger,
                                    error=error,
                                    message=(
                                        "Application Agent AI "
                                        "answer generation failed."
                                    ),
                                    context={
                                        "question": (
                                            field_label
                                        ),
                                    },
                                )

                            st.error(
                                "The local AI answer could not "
                                "be generated."
                            )

                            st.code(
                                f"{type(error).__name__}: "
                                f"{error}"
                            )

                    custom_answer = (
                        st.text_area(
                            "Answer",
                            key=custom_key,
                            height=120,
                        )
                    )

                    if custom_answer.strip().startswith(
                        "NEEDS_USER_INPUT:"
                    ):
                        st.warning(
                            custom_answer.strip()
                        )

                    if custom_answer.strip():
                        custom_answers[
                            str(
                                field_index
                            )
                        ] = (
                            custom_answer.strip()
                        )

                mapping_status = (
                    _profile_status(
                        effective_key=(
                            effective_key
                        ),
                        applicant_profile=(
                            applicant_profile
                        ),
                        custom_answer=(
                            custom_answer
                        ),
                    )
                )

                if mapping_status == "Ready":
                    ready_count += 1

                elif (
                    mapping_status
                    == "Skipped by user"
                ):
                    skipped_count += 1

                elif mapping_status in {
                    "Missing profile data",
                    "Missing custom answer",
                }:
                    missing_count += 1

                else:
                    review_count += 1

                st.write(
                    f"Effective mapping: "
                    f"`{effective_key}` "
                    f"→ **{mapping_status}**"
                )

        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )

        with metric_col1:
            st.metric(
                "Ready",
                ready_count,
            )

        with metric_col2:
            st.metric(
                "Missing",
                missing_count,
            )

        with metric_col3:
            st.metric(
                "Needs review",
                review_count,
            )

        with metric_col4:
            st.metric(
                "Skipped",
                skipped_count,
            )

        if review_count:
            st.warning(
                "Some fields still need manual mapping or review."
            )

        if missing_count:
            st.warning(
                "Some mapped fields are missing profile values "
                "or custom answers."
            )

    st.divider()

    # ==================================================
    # 4. SAFE PREVIEW
    # ==================================================
    st.subheader(
        "4. Safe Auto-fill Preview"
    )

    preview_ready = (
        bool(
            application_job_url.strip()
        )
        and bool(
            page_result
        )
        and not page_result.get(
            "login_required",
            False,
        )
        and bool(
            detected_fields
        )
        and (
            not inspected_url
            or inspected_url
            == application_job_url.strip()
        )
    )

    if st.button(
        "Generate Auto-fill Preview",
        type="primary",
        disabled=(
            not preview_ready
        ),
        key=(
            "application_agent_"
            "generate_autofill_preview"
        ),
    ):
        try:
            with st.spinner(
                "Filling a temporary browser and taking a screenshot..."
            ):
                preview_result = (
                    preview_autofill_job_page(
                        job_url=(
                            application_job_url
                        ),
                        applicant_profile=(
                            _browser_profile(
                                applicant_profile
                            )
                        ),
                        resume_file=(
                            _build_resume_payload(
                                application_resume
                            )
                        ),
                        field_mapping_overrides=(
                            field_mapping_overrides
                        ),
                        custom_answers=(
                            custom_answers
                        ),
                    )
                )

            st.session_state[
                "application_agent_"
                "autofill_preview"
            ] = preview_result

            if logger is not None:
                log_event(
                    logger=logger,
                    message=(
                        "Application Agent "
                        "auto-fill preview generated."
                    ),
                    context={
                        "job_url": (
                            application_job_url
                        ),
                        "filled_count": (
                            preview_result.get(
                                "filled_count",
                                0,
                            )
                        ),
                        "skipped_count": (
                            preview_result.get(
                                "skipped_count",
                                0,
                            )
                        ),
                        "error_count": (
                            preview_result.get(
                                "error_count",
                                0,
                            )
                        ),
                    },
                )

        except Exception as error:
            if logger is not None:
                log_exception(
                    logger=logger,
                    error=error,
                    message=(
                        "Application Agent "
                        "auto-fill preview failed."
                    ),
                    context={
                        "job_url": (
                            application_job_url
                        ),
                    },
                )

            st.error(
                "The auto-fill preview could not be generated."
            )

            st.code(
                f"{type(error).__name__}: "
                f"{error}"
            )

    preview_result = (
        st.session_state.get(
            "application_agent_"
            "autofill_preview"
        )
    )

    if preview_result:
        preview_url = (
            preview_result.get(
                "requested_url",
                "",
            )
        )

        current_mappings = (
            field_mapping_overrides
        )

        current_answers = (
            custom_answers
        )

        stale_preview = (
            preview_url
            != application_job_url.strip()
            or preview_result.get(
                "field_mapping_overrides",
                {},
            )
            != current_mappings
            or preview_result.get(
                "custom_answers",
                {},
            )
            != current_answers
        )

        if stale_preview:
            st.warning(
                "The URL, mapping, or custom answers changed "
                "after this preview was generated. Generate a "
                "new preview before opening the review browser."
            )

        elif preview_result.get(
            "login_required"
        ):
            st.warning(
                "The preview reached a sign-in page. "
                "No fields were filled."
            )

        else:
            st.success(
                "Preview generated. No application was submitted."
            )

            preview_col1, preview_col2, preview_col3 = (
                st.columns(3)
            )

            with preview_col1:
                st.metric(
                    "Filled",
                    preview_result.get(
                        "filled_count",
                        0,
                    ),
                )

            with preview_col2:
                st.metric(
                    "Skipped",
                    preview_result.get(
                        "skipped_count",
                        0,
                    ),
                )

            with preview_col3:
                st.metric(
                    "Errors",
                    preview_result.get(
                        "error_count",
                        0,
                    ),
                )

            preview_actions = (
                preview_result.get(
                    "actions",
                    [],
                )
                or []
            )

            if preview_actions:
                with st.expander(
                    "Show fill action report"
                ):
                    for action_number, action in enumerate(
                        preview_actions,
                        start=1,
                    ):
                        st.write(
                            f"**{action_number}. "
                            f"{action.get('label', 'Field')}** "
                            f"→ `{action.get('field_key', 'unknown')}` "
                            f"→ **{action.get('status', 'unknown')}**"
                        )

                        if action.get(
                            "reason"
                        ):
                            st.caption(
                                action[
                                    "reason"
                                ]
                            )

            screenshot = (
                preview_result.get(
                    "screenshot"
                )
            )

            if screenshot:
                st.image(
                    screenshot,
                    caption=(
                        "Temporary auto-fill preview"
                    ),
                )

    st.divider()

    # ==================================================
    # 5. HEADED REVIEW BROWSER
    # ==================================================
    st.subheader(
        "5. Open Filled Browser for Manual Review"
    )

    st.write(
        "This launches a separate Chromium window, fills the "
        "supported fields, and leaves the browser open. "
        "You review the form and submit it yourself."
    )

    review_ack = st.checkbox(
        "I understand that I must review every answer and "
        "submit the application manually.",
        key=(
            "application_agent_review_ack"
        ),
    )

    current_preview_is_ready = (
        bool(
            preview_result
        )
        and not (
            preview_result.get(
                "login_required",
                False,
            )
        )
        and preview_result.get(
            "requested_url",
            "",
        )
        == application_job_url.strip()
        and preview_result.get(
            "field_mapping_overrides",
            {},
        )
        == field_mapping_overrides
        and preview_result.get(
            "custom_answers",
            {},
        )
        == custom_answers
    )

    if st.button(
        "Open Filled Review Browser",
        type="primary",
        disabled=(
            not (
                current_preview_is_ready
                and review_ack
            )
        ),
        key=(
            "application_agent_"
            "launch_review_browser"
        ),
    ):
        try:
            launch_result = (
                launch_application_review(
                    job_url=(
                        application_job_url
                    ),
                    applicant_profile=(
                        _browser_profile(
                            applicant_profile
                        )
                    ),
                    resume_upload=(
                        application_resume
                    ),
                    field_mapping_overrides=(
                        field_mapping_overrides
                    ),
                    custom_answers=(
                        custom_answers
                    ),
                )
            )

            st.session_state[
                "application_agent_"
                "last_review_launch"
            ] = launch_result

            st.success(
                "Review browser launched. "
                "Review the form there and submit manually."
            )

            if logger is not None:
                log_event(
                    logger=logger,
                    message=(
                        "Application Agent headed "
                        "review browser launched."
                    ),
                    context={
                        "job_url": (
                            application_job_url
                        ),
                        "run_id": (
                            launch_result.get(
                                "run_id",
                                "",
                            )
                        ),
                    },
                )

        except Exception as error:
            if logger is not None:
                log_exception(
                    logger=logger,
                    error=error,
                    message=(
                        "Application Agent review "
                        "browser launch failed."
                    ),
                    context={
                        "job_url": (
                            application_job_url
                        ),
                    },
                )

            st.error(
                "The review browser could not be launched."
            )

            st.code(
                f"{type(error).__name__}: "
                f"{error}"
            )

    last_launch = (
        st.session_state.get(
            "application_agent_"
            "last_review_launch"
        )
    )

    if last_launch:
        st.caption(
            f"Last review run: "
            f"{last_launch.get('run_id', '')} "
            f"· process {last_launch.get('pid', '')}"
        )

    st.divider()

    # ==================================================
    # 6. TRACKER
    # ==================================================
    st.subheader(
        "6. Save Submitted Application to Tracker"
    )

    submitted_manually = (
        st.checkbox(
            "I have manually submitted this application.",
            key=(
                "application_agent_"
                "submitted_manually"
            ),
        )
    )

    allow_duplicate = st.checkbox(
        "Allow saving even if a similar application "
        "already exists in the tracker.",
        key=(
            "application_agent_"
            "allow_duplicate"
        ),
    )

    if st.button(
        "Mark as Applied",
        disabled=(
            not submitted_manually
        ),
        key=(
            "application_agent_"
            "mark_as_applied"
        ),
    ):
        company = (
            application_company.strip()
        )

        job_title = (
            application_job_title.strip()
        )

        if not company:
            st.error(
                "Company is required before saving to the tracker."
            )

        elif not job_title:
            st.error(
                "Job title is required before saving to the tracker."
            )

        else:
            tracker_location = (
                location.strip()
                or ", ".join(
                    part
                    for part in [
                        city.strip(),
                        country.strip(),
                    ]
                    if part.strip()
                )
            )

            duplicates = (
                find_possible_duplicates(
                    company=company,
                    job_title=job_title,
                    location=(
                        tracker_location
                    ),
                    job_url=(
                        application_job_url
                    ),
                )
            )

            if (
                duplicates
                and not allow_duplicate
            ):
                st.warning(
                    "A similar application already exists. "
                    "Enable the duplicate override only if "
                    "you really want another tracker entry."
                )

                for duplicate in (
                    duplicates[:3]
                ):
                    existing = (
                        duplicate.get(
                            "application",
                            {},
                        )
                    )

                    st.write(
                        f"- #{existing.get('id')} "
                        f"{existing.get('company', '')} — "
                        f"{existing.get('job_title', '')} "
                        f"({duplicate.get('confidence', '')})"
                    )

            else:
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

                skill_score = (
                    _extract_numeric_score(
                        match_result,
                        [
                            "skill_match_score",
                            "match_score",
                            "score",
                            "percentage",
                        ],
                    )
                )

                ats_score = (
                    _extract_numeric_score(
                        ats_result,
                        [
                            "ats_score",
                            "score",
                            "percentage",
                        ],
                    )
                )

                overall_score = (
                    _extract_numeric_score(
                        job_match_result,
                        [
                            "overall_match_score",
                            "match_score",
                            "score",
                            "percentage",
                        ],
                    )
                )

                notes = (
                    application_notes.strip()
                )

                if notes:
                    notes = (
                        notes
                        + "\n\n"
                    )

                notes += (
                    "Submitted manually after "
                    "Application Agent review."
                )

                try:
                    application_id = (
                        save_application(
                            company=company,
                            job_title=(
                                job_title
                            ),
                            location=(
                                tracker_location
                            ),
                            application_date=(
                                date.today().isoformat()
                            ),
                            status="Applied",
                            job_url=(
                                application_job_url
                            ),
                            contact_name="",
                            contact_email="",
                            contact_phone="",
                            skill_match_score=(
                                skill_score
                            ),
                            ats_score=(
                                ats_score
                            ),
                            overall_match_score=(
                                overall_score
                            ),
                            notes=notes,
                            application_source=(
                                "Application Agent"
                            ),
                            cv_version=(
                                application_resume.name
                                if application_resume
                                is not None
                                else ""
                            ),
                            cover_letter_version=(
                                "Application Agent"
                                if cover_letter.strip()
                                else ""
                            ),
                        )
                    )

                    st.success(
                        f"Saved as Applied in the tracker "
                        f"(ID {application_id})."
                    )

                    if logger is not None:
                        log_event(
                            logger=logger,
                            message=(
                                "Application Agent "
                                "application saved as Applied."
                            ),
                            context={
                                "application_id": (
                                    application_id
                                ),
                                "company": company,
                                "job_title": (
                                    job_title
                                ),
                            },
                        )

                except Exception as error:
                    if logger is not None:
                        log_exception(
                            logger=logger,
                            error=error,
                            message=(
                                "Application Agent "
                                "tracker save failed."
                            ),
                            context={
                                "company": company,
                                "job_title": (
                                    job_title
                                ),
                            },
                        )

                    st.error(
                        "The application could not be saved "
                        "to the tracker."
                    )

                    st.code(
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
