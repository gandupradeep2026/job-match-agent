from __future__ import annotations

import re

import streamlit as st

from services.master_cv_service import (
    create_master_cv,
)


def _safe_filename(
    candidate_name: str,
    language: str,
    extension: str,
) -> str:
    language_code = (
        "en"
        if language == "English"
        else "de"
    )

    base = (
        f"master_cv_"
        f"{candidate_name}_"
        f"{language_code}"
    ).lower()

    base = re.sub(
        r"[^a-z0-9äöüß]+",
        "_",
        base,
    ).strip("_")

    if not base:
        base = (
            f"master_cv_{language_code}"
        )

    return (
        f"{base}.{extension}"
    )


def _render_language_result(
    language: str,
) -> None:
    result_key = (
        "career_master_cv_"
        + language.lower()
    )

    result = (
        st.session_state.get(
            result_key
        )
    )

    if not result:
        return

    for warning in (
        result.get(
            "warnings",
            []
        )
    ):
        st.warning(
            warning
        )

    data = result["data"]
    text = result["text"]
    docx = result["docx"]

    st.markdown(
        f"### {language}"
    )

    edited_text = st.text_area(
        (
            "Master CV text"
            if language == "English"
            else "Master-Lebenslauf Text"
        ),
        value=text,
        height=650,
        key=(
            f"career_master_cv_edit_"
            f"{language.lower()}"
        ),
    )

    candidate_name = (
        data.candidate_name
        or "candidate"
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        st.download_button(
            (
                "Download TXT"
                if language == "English"
                else "TXT herunterladen"
            ),
            data=edited_text.encode(
                "utf-8"
            ),
            file_name=_safe_filename(
                candidate_name,
                language,
                "txt",
            ),
            mime="text/plain",
            use_container_width=True,
            key=(
                f"career_download_master_txt_"
                f"{language.lower()}"
            ),
        )

    with col2:
        st.download_button(
            (
                "Download DOCX"
                if language == "English"
                else "DOCX herunterladen"
            ),
            data=docx,
            file_name=_safe_filename(
                candidate_name,
                language,
                "docx",
            ),
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
            key=(
                f"career_download_master_docx_"
                f"{language.lower()}"
            ),
        )


def render_master_cv_section() -> None:
    st.divider()

    st.subheader(
        "Master CV / Master-Lebenslauf"
    )

    st.caption(
        "Generate a complete source-of-truth CV from your verified "
        "career records. This is your internal Master CV; later the "
        "Career Agent will create job-specific CVs from it."
    )

    language_mode = st.radio(
        "CV Language / Sprache",
        [
            "Both / Beide",
            "English",
            "Deutsch",
        ],
        horizontal=True,
        key=(
            "career_master_cv_language_mode"
        ),
    )

    st.info(
        "Truth Lock is active here: unverified work experience, "
        "education, projects and achievements are excluded automatically."
    )

    if st.button(
        "Generate Master CV / Master-Lebenslauf erstellen",
        type="primary",
        use_container_width=True,
        key="career_generate_master_cv",
    ):
        languages = (
            [
                "English",
                "Deutsch",
            ]
            if language_mode == "Both / Beide"
            else [
                language_mode
            ]
        )

        for language in languages:
            try:
                result = create_master_cv(
                    language
                )

                st.session_state[
                    "career_master_cv_"
                    + language.lower()
                ] = result

            except Exception as error:
                st.error(
                    f"{language}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        st.success(
            "Master CV generated from verified career data. / "
            "Master-Lebenslauf aus verifizierten Karrieredaten erstellt."
        )

    if language_mode in (
        "Both / Beide",
        "English",
    ):
        _render_language_result(
            "English"
        )

    if language_mode in (
        "Both / Beide",
        "Deutsch",
    ):
        _render_language_result(
            "Deutsch"
        )

    st.warning(
        "This is the complete Master CV, not the final CV for every "
        "application. Later we will select and tailor only the most "
        "relevant verified content for each vacancy."
    )
