from __future__ import annotations

import streamlit as st

from career.bilingual import (
    join_items,
    split_items,
)
from career.star_story import (
    StarStory,
)
from career.star_story_database import (
    delete_star_story,
    get_star_stories,
    save_star_story,
)


CATEGORIES = [
    "",
    "Problem Solving",
    "Leadership",
    "Teamwork",
    "Conflict",
    "Failure / Mistake",
    "Technical Challenge",
    "Learning Quickly",
    "Stakeholder Management",
    "Customer Focus",
    "Ownership / Initiative",
    "Pressure / Deadline",
    "Process Improvement",
    "Achievement",
    "Communication",
    "Adaptability",
    "Other",
]


SOURCE_TYPES = [
    "",
    "Work Experience",
    "Project",
    "Education",
    "Achievement",
    "Volunteer Experience",
    "Other",
]


def _language_view() -> str:
    return st.session_state.get(
        "career_profile_output_language",
        "Both / Beide",
    )


def _safe_index(
    options: list[str],
    value: str,
) -> int:
    try:
        return options.index(
            value
        )
    except ValueError:
        return 0


def _render_summary(
    record: StarStory,
) -> None:
    language = _language_view()

    st.write(
        f"**{record.display_title()}**"
    )

    st.caption(
        " | ".join(
            item
            for item in [
                record.category,
                record.source_type,
                record.source_name,
            ]
            if item
        )
    )

    if language in (
        "Both / Beide",
        "English",
    ):
        if record.title_en:
            st.markdown(
                f"**EN: {record.title_en}**"
            )

        if record.situation_en:
            st.markdown(
                "**Situation**"
            )
            st.write(
                record.situation_en
            )

        if record.task_en:
            st.markdown(
                "**Task**"
            )
            st.write(
                record.task_en
            )

        if record.action_en:
            st.markdown(
                "**Action**"
            )
            st.write(
                record.action_en
            )

        if record.result_en:
            st.markdown(
                "**Result**"
            )
            st.write(
                record.result_en
            )

        if record.lesson_en:
            st.markdown(
                "**Lesson / Reflection**"
            )
            st.write(
                record.lesson_en
            )

    if language in (
        "Both / Beide",
        "Deutsch",
    ):
        if record.title_de:
            st.markdown(
                f"**DE: {record.title_de}**"
            )

        if record.situation_de:
            st.markdown(
                "**Situation**"
            )
            st.write(
                record.situation_de
            )

        if record.task_de:
            st.markdown(
                "**Aufgabe**"
            )
            st.write(
                record.task_de
            )

        if record.action_de:
            st.markdown(
                "**Vorgehen / Handlung**"
            )
            st.write(
                record.action_de
            )

        if record.result_de:
            st.markdown(
                "**Ergebnis**"
            )
            st.write(
                record.result_de
            )

        if record.lesson_de:
            st.markdown(
                "**Lerneffekt / Reflexion**"
            )
            st.write(
                record.lesson_de
            )

    if record.metric_value:
        st.metric(
            "Measured Result / Messbares Ergebnis",
            record.metric_value,
        )

    if record.competencies:
        st.write(
            "**Competencies / Kompetenzen:** "
            + ", ".join(
                record.competencies
            )
        )

    if record.technologies:
        st.write(
            "**Technologies / Technologien:** "
            + ", ".join(
                record.technologies
            )
        )

    if record.question_tags:
        st.write(
            "**Question Tags / Fragetypen:** "
            + ", ".join(
                record.question_tags
            )
        )

    if record.verified:
        st.success(
            "Verified STAR story / Verifizierte STAR-Story"
        )
    else:
        st.warning(
            "Not verified / Noch nicht verifiziert"
        )


def _render_form(
    *,
    form_key: str,
    record: StarStory | None = None,
    submit_label: str,
) -> bool:
    original = (
        record
        or StarStory()
    )

    with st.form(
        form_key,
        clear_on_submit=False,
    ):
        st.markdown(
            "#### Story Identity / Story-Informationen"
        )

        col1, col2 = st.columns(2)

        with col1:
            title_en = st.text_input(
                "Story Title — English *",
                value=original.title_en,
                key=f"{form_key}_title_en",
            )

            category = st.selectbox(
                "Primary Category / Hauptkategorie",
                CATEGORIES,
                index=_safe_index(
                    CATEGORIES,
                    original.category,
                ),
                key=f"{form_key}_category",
            )

            source_type = st.selectbox(
                "Source / Quelle",
                SOURCE_TYPES,
                index=_safe_index(
                    SOURCE_TYPES,
                    original.source_type,
                ),
                key=f"{form_key}_source_type",
            )

        with col2:
            title_de = st.text_input(
                "Story-Titel — Deutsch",
                value=original.title_de,
                key=f"{form_key}_title_de",
            )

            source_name = st.text_input(
                "Related Employer / Project / Source",
                value=original.source_name,
                placeholder=(
                    "Employer, project or education name"
                ),
                key=f"{form_key}_source_name",
            )

            metric_value = st.text_input(
                "Measured Result / Messbares Ergebnis",
                value=original.metric_value,
                placeholder=(
                    "30% faster / 20% fewer errors / 5-person team"
                ),
                key=f"{form_key}_metric_value",
            )

        st.markdown(
            "#### STAR — English"
        )

        situation_en = st.text_area(
            "Situation — English",
            value=original.situation_en,
            height=110,
            key=f"{form_key}_situation_en",
        )

        task_en = st.text_area(
            "Task — English",
            value=original.task_en,
            height=100,
            key=f"{form_key}_task_en",
        )

        action_en = st.text_area(
            "Action — English",
            value=original.action_en,
            height=150,
            key=f"{form_key}_action_en",
        )

        result_en = st.text_area(
            "Result — English",
            value=original.result_en,
            height=110,
            key=f"{form_key}_result_en",
        )

        lesson_en = st.text_area(
            "Lesson / Reflection — English",
            value=original.lesson_en,
            height=90,
            key=f"{form_key}_lesson_en",
        )

        st.markdown(
            "#### STAR — Deutsch"
        )

        situation_de = st.text_area(
            "Situation — Deutsch",
            value=original.situation_de,
            height=110,
            key=f"{form_key}_situation_de",
        )

        task_de = st.text_area(
            "Aufgabe — Deutsch",
            value=original.task_de,
            height=100,
            key=f"{form_key}_task_de",
        )

        action_de = st.text_area(
            "Vorgehen / Handlung — Deutsch",
            value=original.action_de,
            height=150,
            key=f"{form_key}_action_de",
        )

        result_de = st.text_area(
            "Ergebnis — Deutsch",
            value=original.result_de,
            height=110,
            key=f"{form_key}_result_de",
        )

        lesson_de = st.text_area(
            "Lerneffekt / Reflexion — Deutsch",
            value=original.lesson_de,
            height=90,
            key=f"{form_key}_lesson_de",
        )

        st.markdown(
            "#### Interview Tags / Interview-Schlagwörter"
        )

        col3, col4, col5 = (
            st.columns(3)
        )

        with col3:
            competencies_text = (
                st.text_area(
                    "Competencies / Kompetenzen",
                    value=join_items(
                        original.competencies
                    ),
                    height=140,
                    placeholder=(
                        "Problem Solving\nLeadership\nCommunication"
                    ),
                    key=(
                        f"{form_key}_competencies"
                    ),
                )
            )

        with col4:
            technologies_text = (
                st.text_area(
                    "Technologies / Technologien",
                    value=join_items(
                        original.technologies
                    ),
                    height=140,
                    placeholder=(
                        "Python\nSQL\nGCP\nSpark"
                    ),
                    key=(
                        f"{form_key}_technologies"
                    ),
                )
            )

        with col5:
            question_tags_text = (
                st.text_area(
                    "Question Tags / Fragetypen",
                    value=join_items(
                        original.question_tags
                    ),
                    height=140,
                    placeholder=(
                        "Tell me about a challenge\n"
                        "Tell me about a failure\n"
                        "Describe a time you led a team"
                    ),
                    key=(
                        f"{form_key}_question_tags"
                    ),
                )
            )

        verified = st.checkbox(
            "I confirm this STAR story is accurate. / "
            "Ich bestätige, dass diese STAR-Story korrekt ist.",
            value=original.verified,
            key=f"{form_key}_verified",
        )

        submitted = (
            st.form_submit_button(
                submit_label,
                type="primary",
                use_container_width=True,
            )
        )

    if not submitted:
        return False

    candidate = StarStory(
        id=original.id,
        title_en=title_en,
        title_de=title_de,
        category=category,
        source_type=source_type,
        source_name=source_name,
        situation_en=situation_en,
        situation_de=situation_de,
        task_en=task_en,
        task_de=task_de,
        action_en=action_en,
        action_de=action_de,
        result_en=result_en,
        result_de=result_de,
        lesson_en=lesson_en,
        lesson_de=lesson_de,
        metric_value=metric_value,
        competencies=split_items(
            competencies_text
        ),
        technologies=split_items(
            technologies_text
        ),
        question_tags=split_items(
            question_tags_text
        ),
        verified=verified,
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Add a story title and complete Situation, Task, Action and "
            "Result in at least one language. / Bitte einen Story-Titel "
            "angeben und Situation, Aufgabe, Vorgehen und Ergebnis in "
            "mindestens einer Sprache vollständig ausfüllen."
        )

        return False

    save_star_story(
        candidate
    )

    st.success(
        "STAR story saved. / STAR-Story gespeichert."
    )

    return True


def render_star_story_section() -> None:
    st.divider()

    st.subheader(
        "STAR Story Bank / STAR-Story-Sammlung"
    )

    st.caption(
        "Build reusable verified interview stories for leadership, "
        "problem solving, teamwork, failure, technical challenges and "
        "other behavioral questions."
    )

    records = (
        get_star_stories()
    )

    verified_count = sum(
        1
        for item in records
        if item.verified
    )

    categories = {
        item.category
        for item in records
        if item.category.strip()
    }

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:
        st.metric(
            "STAR Stories",
            len(records),
        )

    with col2:
        st.metric(
            "Verified / Verifiziert",
            verified_count,
        )

    with col3:
        st.metric(
            "Categories / Kategorien",
            len(categories),
        )

    with st.expander(
        "➕ Add STAR Story / STAR-Story hinzufügen",
        expanded=not records,
    ):
        saved = _render_form(
            form_key=(
                "career_add_star_story"
            ),
            submit_label=(
                "Add STAR Story / STAR-Story hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_star_story_id",
                None,
            )

            st.rerun()

    if not records:
        st.info(
            "No STAR stories have been added yet. / "
            "Noch keine STAR-Stories hinzugefügt."
        )

        return

    st.markdown(
        "### Story Bank / Story-Sammlung"
    )

    filter_col1, filter_col2 = (
        st.columns(2)
    )

    category_options = [
        "All / Alle",
        *[
            item
            for item in CATEGORIES
            if item
        ],
    ]

    with filter_col1:
        category_filter = st.selectbox(
            "Filter by Category / Kategorie",
            category_options,
            key=(
                "career_star_category_filter"
            ),
        )

    with filter_col2:
        verification_filter = (
            st.selectbox(
                "Verification / Verifizierung",
                [
                    "All / Alle",
                    "Verified / Verifiziert",
                    "Not Verified / Nicht verifiziert",
                ],
                key=(
                    "career_star_verification_filter"
                ),
            )
        )

    filtered = records

    if category_filter != "All / Alle":
        filtered = [
            item
            for item in filtered
            if item.category
            == category_filter
        ]

    if (
        verification_filter
        == "Verified / Verifiziert"
    ):
        filtered = [
            item
            for item in filtered
            if item.verified
        ]

    elif (
        verification_filter
        == "Not Verified / Nicht verifiziert"
    ):
        filtered = [
            item
            for item in filtered
            if not item.verified
        ]

    edit_id = (
        st.session_state.get(
            "career_edit_star_story_id"
        )
    )

    for record in filtered:
        label = (
            record.display_title()
        )

        if record.category:
            label += (
                f" — {record.category}"
            )

        if record.verified:
            label = (
                "✅ "
                + label
            )

        with st.expander(
            label,
            expanded=(
                edit_id
                == record.id
            ),
        ):
            _render_summary(
                record
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "✏️ Edit / Bearbeiten",
                    key=(
                        f"career_edit_star_story_"
                        f"{record.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_star_story_id"
                    ] = record.id

                    st.rerun()

            with col2:
                confirm_delete = (
                    st.checkbox(
                        "Confirm delete / Löschen bestätigen",
                        key=(
                            "career_confirm_delete_star_story_"
                            f"{record.id}"
                        ),
                    )
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_star_story_"
                        f"{record.id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_star_story(
                        record.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_star_story_id"
                        )
                        == record.id
                    ):
                        st.session_state.pop(
                            "career_edit_star_story_id",
                            None,
                        )

                    st.rerun()

            if edit_id == record.id:
                st.divider()

                st.markdown(
                    "#### Edit STAR Story / STAR-Story bearbeiten"
                )

                saved = _render_form(
                    form_key=(
                        f"career_update_star_story_"
                        f"{record.id}"
                    ),
                    record=record,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_star_story_id",
                        None,
                    )

                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_star_story_"
                        f"{record.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_star_story_id",
                        None,
                    )

                    st.rerun()
