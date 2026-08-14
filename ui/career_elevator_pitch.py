from __future__ import annotations

import streamlit as st

from career.database import load_profile
from career.elevator_pitch import (
    ElevatorPitchRequest,
)
from services.elevator_pitch_service import (
    generate_personal_elevator_pitch,
)


AUDIENCES = [
    "Recruiter",
    "Hiring Manager",
    "Technical Manager",
    "Networking",
]


def _render_result(
    language: str,
) -> None:
    key = (
        "career_elevator_pitch_"
        + language.lower()
    )

    result = (
        st.session_state.get(
            key
        )
    )

    if result is None:
        return

    st.markdown(
        f"### {language}"
    )

    for warning in result.warnings:
        st.warning(
            warning
        )

    edited = st.text_area(
        (
            "My Elevator Pitch — English"
            if language == "English"
            else "Mein Elevator Pitch — Deutsch"
        ),
        value=result.text,
        height=260,
        key=(
            f"career_elevator_pitch_edit_"
            f"{language.lower()}"
        ),
    )

    st.caption(
        f"Target: {result.duration_seconds} seconds | "
        f"Audience: {result.audience} | "
        f"Verified evidence items used: {result.evidence_count}"
    )

    st.download_button(
        (
            "Download English Pitch"
            if language == "English"
            else "Deutschen Pitch herunterladen"
        ),
        data=edited.encode(
            "utf-8"
        ),
        file_name=(
            "personal_elevator_pitch_en.txt"
            if language == "English"
            else "personal_elevator_pitch_de.txt"
        ),
        mime="text/plain",
        use_container_width=True,
        key=(
            f"career_elevator_pitch_download_"
            f"{language.lower()}"
        ),
    )


def render_elevator_pitch_section() -> None:
    st.divider()

    st.subheader(
        "Personal Elevator Pitch / Persönlicher Elevator Pitch"
    )

    st.caption(
        "Generate your own spoken introduction from verified career data. "
        "This is your candidate pitch — not a pitch about the employer."
    )

    profile = load_profile()

    target_role_options = [
        role
        for role in (
            profile.target_roles
            or []
        )
        if role.strip()
    ]

    if not target_role_options:
        target_role_options = [
            "Data Engineer"
        ]

    col1, col2 = st.columns(2)

    with col1:
        target_role = st.selectbox(
            "Target Role / Zielrolle",
            target_role_options,
            key=(
                "career_elevator_pitch_target_role"
            ),
        )

        duration = st.radio(
            "Length / Länge",
            [
                30,
                60,
                90,
            ],
            horizontal=True,
            format_func=lambda value: (
                f"{value} sec"
            ),
            key=(
                "career_elevator_pitch_duration"
            ),
        )

    with col2:
        audience = st.selectbox(
            "Audience / Gesprächspartner",
            AUDIENCES,
            key=(
                "career_elevator_pitch_audience"
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
                "career_elevator_pitch_language"
            ),
        )

    st.info(
        "Truth Lock: this first version uses only verified profile, "
        "experience, education, project and achievement data. "
        "It does not invent missing facts."
    )

    if st.button(
        "Generate My Elevator Pitch / Meinen Elevator Pitch erstellen",
        type="primary",
        use_container_width=True,
        key=(
            "career_generate_elevator_pitch"
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
                    generate_personal_elevator_pitch(
                        ElevatorPitchRequest(
                            language=language,
                            duration_seconds=duration,
                            audience=audience,
                            target_role=target_role,
                        )
                    )
                )

                st.session_state[
                    "career_elevator_pitch_"
                    + language.lower()
                ] = result

            except Exception as error:
                st.error(
                    f"{language}: "
                    f"{type(error).__name__}: {error}"
                )

        st.success(
            "Personal elevator pitch generated. / "
            "Persönlicher Elevator Pitch erstellt."
        )

    if language_mode in (
        "Both / Beide",
        "English",
    ):
        _render_result(
            "English"
        )

    if language_mode in (
        "Both / Beide",
        "Deutsch",
    ):
        _render_result(
            "Deutsch"
        )

    st.caption(
        "Next refinement: we can add optional local-LLM polishing "
        "while keeping the same verified-fact Truth Lock."
    )
