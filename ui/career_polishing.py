from __future__ import annotations

import streamlit as st

from career.polishing import (
    CareerPolishRequest,
)
from services.career_polishing_service import (
    polish_career_text,
)


CONTENT_TYPES = [
    "Elevator Pitch",
    "Interview Answer",
    "STAR Story",
    "Why This Role",
    "Why This Company",
    "Master CV Section",
    "Tailored CV Section",
    "Professional Summary",
    "Other",
]


STYLE_OPTIONS = [
    "Natural Professional",
    "Concise Professional",
    "Interview Spoken",
    "CV / ATS",
]


def render_career_polishing_section() -> None:
    st.divider()

    st.subheader(
        "Local-AI Polishing / Lokale KI-Textoptimierung"
    )

    st.caption(
        "Polish verified career text with your local Ollama model while "
        "keeping the original facts as the hard Truth-Lock boundary."
    )

    col1, col2 = st.columns(2)

    with col1:
        language = st.radio(
            "Language / Sprache",
            [
                "English",
                "Deutsch",
            ],
            horizontal=True,
            key=(
                "career_polish_language"
            ),
        )

        content_type = st.selectbox(
            "Content Type / Inhaltstyp",
            CONTENT_TYPES,
            key=(
                "career_polish_content_type"
            ),
        )

    with col2:
        style = st.selectbox(
            "Style / Stil",
            STYLE_OPTIONS,
            key=(
                "career_polish_style"
            ),
        )

        st.info(
            "Runs locally through the Ollama model configured for your app."
        )

    source_text = st.text_area(
        "Verified Source Text / Verifizierter Ausgangstext",
        height=320,
        placeholder=(
            "Paste a generated elevator pitch, interview answer, "
            "STAR story or CV section here."
        ),
        key=(
            "career_polish_source_text"
        ),
    )

    st.warning(
        "Only paste text whose facts you have already verified. "
        "The polishing layer may improve wording, but it is not allowed "
        "to invent new career facts."
    )

    if st.button(
        "Polish with Local AI / Mit lokaler KI optimieren",
        type="primary",
        use_container_width=True,
        key=(
            "career_polish_button"
        ),
    ):
        if not source_text.strip():
            st.error(
                "Please provide verified source text first. / "
                "Bitte zuerst einen verifizierten Ausgangstext eingeben."
            )

        else:
            try:
                with st.spinner(
                    "Polishing locally with Ollama..."
                ):
                    result = polish_career_text(
                        CareerPolishRequest(
                            source_text=source_text,
                            language=language,
                            content_type=(
                                content_type
                            ),
                            style=style,
                        )
                    )

                st.session_state[
                    "career_polish_result"
                ] = result

            except Exception as error:
                st.error(
                    "Local-AI polishing failed: "
                    f"{type(error).__name__}: {error}"
                )

                st.info(
                    "Confirm that Ollama is running and that the configured "
                    "model is available locally."
                )

    result = st.session_state.get(
        "career_polish_result"
    )

    if result is None:
        return

    if result.safety_passed:
        st.success(
            "Truth Lock validation passed. / "
            "Truth-Lock-Prüfung bestanden."
        )
    else:
        st.error(
            "Truth Lock rejected the AI rewrite. "
            "The original verified text has been restored."
        )

    for warning in (
        result.warnings
    ):
        st.warning(
            warning
        )

    polished_text = st.text_area(
        "Polished Text / Optimierter Text",
        value=result.polished_text,
        height=360,
        key=(
            "career_polish_output"
        ),
    )

    if result.changes_made:
        with st.expander(
            "Changes Made / Änderungen"
        ):
            for item in (
                result.changes_made
            ):
                st.write(
                    f"- {item}"
                )

    st.download_button(
        "Download Polished Text / Optimierten Text herunterladen",
        data=polished_text.encode(
            "utf-8"
        ),
        file_name=(
            "career_polished_text.txt"
        ),
        mime="text/plain",
        use_container_width=True,
        key=(
            "career_polish_download"
        ),
    )

    st.caption(
        "Final responsibility remains with the user: review the polished "
        "version before using it in a CV, application or interview."
    )
