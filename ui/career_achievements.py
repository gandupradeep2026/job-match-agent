from __future__ import annotations

import streamlit as st

from career.achievement import (
    AchievementRecord,
)
from career.achievement_database import (
    delete_achievement_record,
    get_achievement_records,
    save_achievement_record,
)
from career.bilingual import (
    join_items,
    split_items,
)


ACHIEVEMENT_CATEGORIES = [
    "",
    "Business Impact",
    "Technical Impact",
    "Process Improvement",
    "Leadership",
    "Customer Impact",
    "Cost Reduction",
    "Time Saving",
    "Quality Improvement",
    "Automation",
    "Research",
    "Academic",
    "Award",
    "Certification",
    "Other",
]


SOURCE_TYPES = [
    "",
    "Work Experience",
    "Project",
    "Education",
    "Certification",
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
    record: AchievementRecord,
) -> None:
    language = _language_view()

    st.write(
        f"**{record.display_title()}**"
    )

    metadata = [
        record.category,
        record.source_type,
        record.source_name,
        record.achievement_date,
    ]

    st.caption(
        " | ".join(
            item
            for item in metadata
            if item
        )
    )

    if record.metric_value:
        st.metric(
            "Measured Result / Messbares Ergebnis",
            record.metric_value,
        )

    if language in (
        "Both / Beide",
        "English",
    ):
        if record.title_en:
            st.write(
                f"**EN:** {record.title_en}"
            )

        if record.description_en:
            st.write(
                record.description_en
            )

        if record.result_en:
            st.write(
                "**Result:** "
                + record.result_en
            )

    if language in (
        "Both / Beide",
        "Deutsch",
    ):
        if record.title_de:
            st.write(
                f"**DE:** {record.title_de}"
            )

        if record.description_de:
            st.write(
                record.description_de
            )

        if record.result_de:
            st.write(
                "**Ergebnis:** "
                + record.result_de
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

    if record.evidence_url:
        st.write(
            "**Evidence / Nachweis:** "
            + record.evidence_url
        )

    if record.verified:
        st.success(
            "Verified achievement / Verifizierter Erfolg"
        )
    else:
        st.warning(
            "Not verified / Noch nicht verifiziert"
        )


def _render_form(
    *,
    form_key: str,
    record: AchievementRecord | None = None,
    submit_label: str,
) -> bool:
    original = (
        record
        or AchievementRecord()
    )

    with st.form(
        form_key,
        clear_on_submit=False,
    ):
        st.markdown(
            "#### Achievement / Erfolg"
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            title_en = st.text_input(
                "Achievement Title — English *",
                value=original.title_en,
                key=f"{form_key}_title_en",
            )

            category = st.selectbox(
                "Category / Kategorie",
                ACHIEVEMENT_CATEGORIES,
                index=_safe_index(
                    ACHIEVEMENT_CATEGORIES,
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

            achievement_date = st.text_input(
                "Date / Datum *",
                value=(
                    original.achievement_date
                ),
                placeholder="2026-08",
                key=(
                    f"{form_key}_achievement_date"
                ),
            )

        with col2:
            title_de = st.text_input(
                "Erfolgstitel — Deutsch",
                value=original.title_de,
                key=f"{form_key}_title_de",
            )

            source_name = st.text_input(
                "Related Employer / Project / Institution",
                value=original.source_name,
                placeholder=(
                    "Example GmbH / Project name"
                ),
                key=f"{form_key}_source_name",
            )

            metric_value = st.text_input(
                "Measured Result / Messbares Ergebnis",
                value=original.metric_value,
                placeholder=(
                    "30% faster / €20,000 saved / 500 users"
                ),
                key=f"{form_key}_metric_value",
            )

        st.markdown(
            "#### Context and Result / Kontext und Ergebnis"
        )

        description_en = st.text_area(
            "Context / Description — English",
            value=original.description_en,
            height=120,
            key=f"{form_key}_description_en",
        )

        description_de = st.text_area(
            "Kontext / Beschreibung — Deutsch",
            value=original.description_de,
            height=120,
            key=f"{form_key}_description_de",
        )

        result_en = st.text_area(
            "Result — English",
            value=original.result_en,
            height=100,
            placeholder=(
                "What changed because of your work?"
            ),
            key=f"{form_key}_result_en",
        )

        result_de = st.text_area(
            "Ergebnis — Deutsch",
            value=original.result_de,
            height=100,
            placeholder=(
                "Was hat sich durch Ihre Arbeit verbessert?"
            ),
            key=f"{form_key}_result_de",
        )

        col3, col4 = (
            st.columns(2)
        )

        with col3:
            competencies_text = st.text_area(
                "Competencies / Kompetenzen",
                value=join_items(
                    original.competencies
                ),
                height=130,
                placeholder=(
                    "Problem Solving\nLeadership\nCommunication"
                ),
                key=(
                    f"{form_key}_competencies"
                ),
            )

        with col4:
            technologies_text = st.text_area(
                "Technologies / Technologien",
                value=join_items(
                    original.technologies
                ),
                height=130,
                placeholder=(
                    "Python\nSQL\nGCP"
                ),
                key=(
                    f"{form_key}_technologies"
                ),
            )

        evidence_url = st.text_input(
            "Evidence URL / Nachweis-URL",
            value=original.evidence_url,
            placeholder=(
                "GitHub, certificate, portfolio or other evidence"
            ),
            key=f"{form_key}_evidence_url",
        )

        verified = st.checkbox(
            "I confirm this achievement is accurate. / "
            "Ich bestätige, dass dieser Erfolg korrekt ist.",
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

    candidate = AchievementRecord(
        id=original.id,
        title_en=title_en,
        title_de=title_de,
        category=category,
        source_type=source_type,
        source_name=source_name,
        achievement_date=(
            achievement_date
        ),
        description_en=description_en,
        description_de=description_de,
        result_en=result_en,
        result_de=result_de,
        metric_value=metric_value,
        competencies=split_items(
            competencies_text
        ),
        technologies=split_items(
            technologies_text
        ),
        evidence_url=evidence_url,
        verified=verified,
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Date and at least one achievement title are required. / "
            "Datum und mindestens ein Erfolgstitel sind erforderlich."
        )

        return False

    save_achievement_record(
        candidate
    )

    st.success(
        "Achievement saved. / Erfolg gespeichert."
    )

    return True


def render_achievements_section() -> None:
    st.divider()

    st.subheader(
        "Achievements / Erfolge"
    )

    st.caption(
        "Store measurable accomplishments separately so the Career Agent "
        "can later select the strongest evidence for CV bullets, elevator "
        "pitches and STAR interview answers."
    )

    records = (
        get_achievement_records()
    )

    metric1, metric2, metric3 = (
        st.columns(3)
    )

    with metric1:
        st.metric(
            "Achievements / Erfolge",
            len(records),
        )

    with metric2:
        st.metric(
            "Verified / Verifiziert",
            sum(
                1
                for item in records
                if item.verified
            ),
        )

    with metric3:
        st.metric(
            "Measured / Messbar",
            sum(
                1
                for item in records
                if item.metric_value.strip()
            ),
        )

    with st.expander(
        "➕ Add Achievement / Erfolg hinzufügen",
        expanded=not records,
    ):
        saved = _render_form(
            form_key=(
                "career_add_achievement"
            ),
            submit_label=(
                "Add Achievement / Erfolg hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_achievement_id",
                None,
            )

            st.rerun()

    if not records:
        st.info(
            "No achievements have been added yet. / "
            "Noch keine Erfolge hinzugefügt."
        )

        return

    st.markdown(
        "### Saved Achievements / Gespeicherte Erfolge"
    )

    edit_id = (
        st.session_state.get(
            "career_edit_achievement_id"
        )
    )

    for record in records:
        label = (
            record.display_title()
        )

        if record.metric_value:
            label += (
                f" — {record.metric_value}"
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
                        f"career_edit_achievement_"
                        f"{record.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_achievement_id"
                    ] = record.id

                    st.rerun()

            with col2:
                confirm_delete = (
                    st.checkbox(
                        "Confirm delete / Löschen bestätigen",
                        key=(
                            "career_confirm_delete_achievement_"
                            f"{record.id}"
                        ),
                    )
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_achievement_"
                        f"{record.id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_achievement_record(
                        record.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_achievement_id"
                        )
                        == record.id
                    ):
                        st.session_state.pop(
                            "career_edit_achievement_id",
                            None,
                        )

                    st.rerun()

            if edit_id == record.id:
                st.divider()

                st.markdown(
                    "#### Edit Achievement / Erfolg bearbeiten"
                )

                saved = _render_form(
                    form_key=(
                        f"career_update_achievement_"
                        f"{record.id}"
                    ),
                    record=record,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_achievement_id",
                        None,
                    )

                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_achievement_"
                        f"{record.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_achievement_id",
                        None,
                    )

                    st.rerun()
