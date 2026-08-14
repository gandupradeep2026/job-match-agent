from __future__ import annotations

import re

import streamlit as st

from career.database import (
    load_profile,
)
from career.interview_preparation import (
    InterviewPreparationRequest,
)
from career.target_company_database import (
    get_target_companies,
)
from services.interview_pack_service import (
    generate_complete_interview_pack_files,
)


def _safe_filename(
    company_name: str,
    language: str,
    extension: str,
) -> str:
    language_code = (
        "en"
        if language == "English"
        else "de"
    )

    base = (
        "complete_interview_pack"
    )

    if company_name:
        base += (
            "_"
            + company_name
        )

    base += (
        "_"
        + language_code
    )

    base = re.sub(
        r"[^a-zA-Z0-9äöüÄÖÜß]+",
        "_",
        base,
    ).strip("_").lower()

    return (
        f"{base}.{extension}"
    )


def _render_pack(
    language: str,
) -> None:
    key = (
        "career_complete_interview_pack_"
        + language.lower()
    )

    result = (
        st.session_state.get(
            key
        )
    )

    if result is None:
        return

    pack = result["pack"]
    text = result["text"]
    docx = result["docx"]

    st.markdown(
        f"## {language}"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:
        st.metric(
            "STAR Answers",
            len(
                pack.behavioral_answers
            ),
        )

    with col2:
        st.metric(
            "Technical Topics",
            len(
                pack.technical_focus
            ),
        )

    with col3:
        st.metric(
            "Employer Questions",
            len(
                pack.employer_questions
            ),
        )

    for warning in (
        pack.warnings
    ):
        st.warning(
            warning
        )

    st.text_area(
        (
            "Complete Interview Pack"
            if language == "English"
            else "Komplettes Interview-Paket"
        ),
        value=text,
        height=750,
        key=(
            "career_complete_pack_text_"
            + language.lower()
        ),
    )

    download_col1, download_col2 = (
        st.columns(2)
    )

    with download_col1:
        st.download_button(
            "Download TXT",
            data=text.encode(
                "utf-8"
            ),
            file_name=_safe_filename(
                pack.company_name,
                language,
                "txt",
            ),
            mime="text/plain",
            use_container_width=True,
            key=(
                "career_complete_pack_txt_"
                + language.lower()
            ),
        )

    with download_col2:
        st.download_button(
            "Download DOCX",
            data=docx,
            file_name=_safe_filename(
                pack.company_name,
                language,
                "docx",
            ),
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
            key=(
                "career_complete_pack_docx_"
                + language.lower()
            ),
        )


def render_complete_interview_pack_section() -> None:
    st.divider()

    st.subheader(
        "Complete Interview Pack / Komplettes Interview-Paket"
    )

    st.caption(
        "Combine your verified elevator pitches, core interview answers, "
        "STAR stories, technical focus areas and employer questions into "
        "one downloadable preparation package."
    )

    profile = load_profile()

    roles = [
        item
        for item in (
            profile.target_roles
            or []
        )
        if item.strip()
    ]

    if not roles:
        roles = [
            "Data Engineer"
        ]

    companies = (
        get_target_companies()
    )

    company_options = [
        (
            None,
            "No company selected / Kein Unternehmen ausgewählt",
        ),
        *[
            (
                item.id,
                item.company_name,
            )
            for item in companies
        ],
    ]

    label_to_id = {
        label: company_id
        for company_id, label
        in company_options
    }

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        target_role = st.selectbox(
            "Target Role / Zielrolle",
            roles,
            key=(
                "career_complete_pack_role"
            ),
        )

        language_mode = st.radio(
            "Language / Sprache",
            [
                "Both / Beide",
                "English",
                "Deutsch",
            ],
            horizontal=True,
            key=(
                "career_complete_pack_language"
            ),
        )

    with col2:
        company_label = st.selectbox(
            "Target Company / Zielunternehmen",
            [
                label
                for _, label
                in company_options
            ],
            key=(
                "career_complete_pack_company"
            ),
        )

        company_id = (
            label_to_id[
                company_label
            ]
        )

    st.markdown(
        "#### Development Area / Entwicklungsbereich"
    )

    development_area = st.text_input(
        "Development Area / Entwicklungsbereich",
        key=(
            "career_complete_pack_development_area"
        ),
    )

    improvement_action = st.text_area(
        "Improvement Action / Verbesserungsmaßnahme",
        height=90,
        key=(
            "career_complete_pack_improvement_action"
        ),
    )

    improvement_evidence = st.text_input(
        "Evidence of Progress / Fortschrittsnachweis",
        key=(
            "career_complete_pack_improvement_evidence"
        ),
    )

    st.info(
        "Truth Lock remains active. The complete pack reuses verified "
        "Career Profile records, verified STAR stories, saved target-company "
        "research and your explicitly entered development area."
    )

    if st.button(
        "Generate Complete Interview Pack / Komplettes Interview-Paket erstellen",
        type="primary",
        use_container_width=True,
        key=(
            "career_generate_complete_interview_pack"
        ),
    ):
        languages = (
            [
                "English",
                "Deutsch",
            ]
            if language_mode
            == "Both / Beide"
            else [
                language_mode
            ]
        )

        for language in languages:
            try:
                result = (
                    generate_complete_interview_pack_files(
                        InterviewPreparationRequest(
                            language=language,
                            target_role=target_role,
                            company_id=company_id,
                            development_area=(
                                development_area
                            ),
                            improvement_action=(
                                improvement_action
                            ),
                            improvement_evidence=(
                                improvement_evidence
                            ),
                        )
                    )
                )

                st.session_state[
                    "career_complete_interview_pack_"
                    + language.lower()
                ] = result

            except Exception as error:
                st.error(
                    f"{language}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        st.success(
            "Complete interview pack generated. / "
            "Komplettes Interview-Paket erstellt."
        )

    if language_mode in (
        "Both / Beide",
        "English",
    ):
        _render_pack(
            "English"
        )

    if language_mode in (
        "Both / Beide",
        "Deutsch",
    ):
        _render_pack(
            "Deutsch"
        )
