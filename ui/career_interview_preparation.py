from __future__ import annotations

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
from services.interview_preparation_service import (
    generate_interview_preparation_pack,
)


def _render_prepared_answer(
    title: str,
    answer,
    key: str,
) -> None:
    st.markdown(
        f"### {title}"
    )

    st.write(
        f"**{answer.question}**"
    )

    for warning in (
        answer.warnings
        or []
    ):
        st.warning(
            warning
        )

    if answer.answer:
        st.text_area(
            "Prepared Answer / Vorbereitete Antwort",
            value=answer.answer,
            height=220,
            key=key,
        )

    if answer.source_summary:
        st.caption(
            "Source / Quelle: "
            + answer.source_summary
        )


def _build_download_text(
    pack,
) -> str:
    lines = []

    heading = (
        "INTERVIEW PREPARATION"
        if pack.language == "English"
        else "INTERVIEWVORBEREITUNG"
    )

    lines.extend(
        [
            heading,
            "=" * len(
                heading
            ),
            "",
            (
                f"Target role: {pack.target_role}"
                if pack.language == "English"
                else (
                    f"Zielrolle: {pack.target_role}"
                )
            ),
        ]
    )

    if pack.company_name:
        lines.append(
            (
                f"Company: {pack.company_name}"
                if pack.language == "English"
                else (
                    f"Unternehmen: {pack.company_name}"
                )
            )
        )

    lines.append("")

    answer_sections = [
        (
            "Tell Me About Yourself",
            pack.tell_me_about_yourself,
        ),
        (
            "Why This Role?",
            pack.why_this_role,
        ),
        (
            "Why This Company?",
            pack.why_this_company,
        ),
        (
            "Strengths",
            pack.strengths,
        ),
        (
            "Development Area / Weakness",
            pack.weakness,
        ),
    ]

    for section_title, answer in answer_sections:
        if answer is None:
            continue

        lines.extend(
            [
                section_title.upper(),
                answer.question,
                answer.answer
                or "[Needs input]",
                "",
            ]
        )

    lines.append(
        "BEHAVIORAL / STAR"
    )
    lines.append(
        "=" * 17
    )

    for item in (
        pack.behavioral_answers
    ):
        lines.extend(
            [
                "",
                item.category,
                item.question,
                item.answer,
            ]
        )

    lines.extend(
        [
            "",
            "TECHNICAL FOCUS",
            "=" * 15,
        ]
    )

    for item in pack.technical_focus:
        lines.append(
            f"- {item}"
        )

    if pack.warnings:
        lines.extend(
            [
                "",
                "WARNINGS",
                "=" * 8,
            ]
        )

        for warning in pack.warnings:
            lines.append(
                f"- {warning}"
            )

    return "\n".join(
        lines
    )


def _render_pack(
    language: str,
) -> None:
    session_key = (
        "career_interview_prep_"
        + language.lower()
    )

    pack = (
        st.session_state.get(
            session_key
        )
    )

    if pack is None:
        return

    st.markdown(
        f"## {language}"
    )

    for warning in (
        pack.warnings
        or []
    ):
        st.warning(
            warning
        )

    _render_prepared_answer(
        (
            "Tell Me About Yourself"
            if language == "English"
            else "Erzählen Sie mir etwas über sich"
        ),
        pack.tell_me_about_yourself,
        (
            f"career_interview_about_"
            f"{language.lower()}"
        ),
    )

    _render_prepared_answer(
        (
            "Why This Role?"
            if language == "English"
            else "Warum diese Position?"
        ),
        pack.why_this_role,
        (
            f"career_interview_role_"
            f"{language.lower()}"
        ),
    )

    _render_prepared_answer(
        (
            "Why This Company?"
            if language == "English"
            else "Warum dieses Unternehmen?"
        ),
        pack.why_this_company,
        (
            f"career_interview_company_"
            f"{language.lower()}"
        ),
    )

    _render_prepared_answer(
        (
            "Strengths"
            if language == "English"
            else "Stärken"
        ),
        pack.strengths,
        (
            f"career_interview_strengths_"
            f"{language.lower()}"
        ),
    )

    _render_prepared_answer(
        (
            "Development Area / Weakness"
            if language == "English"
            else "Entwicklungsbereich / Schwäche"
        ),
        pack.weakness,
        (
            f"career_interview_weakness_"
            f"{language.lower()}"
        ),
    )

    st.markdown(
        (
            "### Behavioral Answers from STAR Stories"
            if language == "English"
            else "### Antworten aus verifizierten STAR-Stories"
        )
    )

    if not pack.behavioral_answers:
        st.info(
            (
                "Add and verify STAR stories to prepare behavioral answers."
                if language == "English"
                else (
                    "Fügen Sie STAR-Stories hinzu und verifizieren Sie "
                    "diese, um Antworten auf Verhaltensfragen vorzubereiten."
                )
            )
        )

    for index, item in enumerate(
        pack.behavioral_answers,
        start=1,
    ):
        with st.expander(
            f"{index}. {item.category} — {item.story_title}"
        ):
            st.write(
                f"**{item.question}**"
            )

            st.text_area(
                "STAR Answer / STAR-Antwort",
                value=item.answer,
                height=260,
                key=(
                    f"career_interview_star_"
                    f"{language.lower()}_{index}"
                ),
            )

    st.markdown(
        (
            "### Technical Interview Focus"
            if language == "English"
            else "### Technische Interview-Schwerpunkte"
        )
    )

    if pack.technical_focus:
        st.write(
            ", ".join(
                pack.technical_focus
            )
        )
    else:
        st.info(
            (
                "No verified technical skills are available yet."
                if language == "English"
                else (
                    "Noch keine verifizierten technischen "
                    "Kenntnisse verfügbar."
                )
            )
        )

    download_text = (
        _build_download_text(
            pack
        )
    )

    st.download_button(
        (
            "Download Interview Preparation"
            if language == "English"
            else "Interviewvorbereitung herunterladen"
        ),
        data=download_text.encode(
            "utf-8"
        ),
        file_name=(
            "interview_preparation_en.txt"
            if language == "English"
            else "interview_preparation_de.txt"
        ),
        mime="text/plain",
        use_container_width=True,
        key=(
            f"career_interview_download_"
            f"{language.lower()}"
        ),
    )


def render_interview_preparation_section() -> None:
    st.divider()

    st.subheader(
        "Interview Preparation / Interviewvorbereitung"
    )

    st.caption(
        "Prepare truthful interview answers from your verified Career "
        "Profile, STAR stories and target-company research. This complements "
        "the existing AI Interview Coach by preparing your own answer bank."
    )

    profile = (
        load_profile()
    )

    target_roles = [
        item
        for item in (
            profile.target_roles
            or []
        )
        if item.strip()
    ]

    if not target_roles:
        target_roles = [
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
                company.id,
                company.company_name,
            )
            for company in companies
        ],
    ]

    company_labels = [
        label
        for _, label in company_options
    ]

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        target_role = (
            st.selectbox(
                "Target Role / Zielrolle",
                target_roles,
                key=(
                    "career_interview_target_role"
                ),
            )
        )

        language_mode = (
            st.radio(
                "Language / Sprache",
                [
                    "Both / Beide",
                    "English",
                    "Deutsch",
                ],
                horizontal=True,
                key=(
                    "career_interview_language_mode"
                ),
            )
        )

    with col2:
        selected_company_label = (
            st.selectbox(
                "Target Company / Zielunternehmen",
                company_labels,
                key=(
                    "career_interview_company"
                ),
            )
        )

        selected_company_id = dict(
            (
                label,
                company_id,
            )
            for company_id, label
            in company_options
        )[
            selected_company_label
        ]

    st.markdown(
        "#### Development Area / Entwicklungsbereich"
    )

    st.caption(
        "For weakness questions we deliberately do not invent anything. "
        "Enter a genuine development area and what you are doing about it."
    )

    development_area = (
        st.text_input(
            "Development Area / Entwicklungsbereich",
            placeholder=(
                "Example: presenting complex technical topics concisely"
            ),
            key=(
                "career_interview_development_area"
            ),
        )
    )

    improvement_action = (
        st.text_area(
            "What are you doing to improve? / Was tun Sie zur Verbesserung?",
            height=90,
            key=(
                "career_interview_improvement_action"
            ),
        )
    )

    improvement_evidence = (
        st.text_input(
            "Evidence of progress / Fortschrittsnachweis",
            placeholder=(
                "Optional concrete example"
            ),
            key=(
                "career_interview_improvement_evidence"
            ),
        )
    )

    st.info(
        "Truth Lock: prepared answers use verified career records and "
        "saved target-company notes. The weakness answer uses only the "
        "development area you explicitly provide."
    )

    if st.button(
        "Generate Interview Preparation / Interviewvorbereitung erstellen",
        type="primary",
        use_container_width=True,
        key=(
            "career_generate_interview_preparation"
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
                pack = (
                    generate_interview_preparation_pack(
                        InterviewPreparationRequest(
                            language=language,
                            target_role=target_role,
                            company_id=(
                                selected_company_id
                            ),
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
                    "career_interview_prep_"
                    + language.lower()
                ] = pack

            except Exception as error:
                st.error(
                    f"{language}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        st.success(
            "Interview preparation generated. / "
            "Interviewvorbereitung erstellt."
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

    st.caption(
        "The existing AI Interview Coach can still generate role-specific "
        "questions and run simulations; this Career module prepares your "
        "verified answers before you practice."
    )
