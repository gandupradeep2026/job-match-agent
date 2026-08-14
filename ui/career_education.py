from __future__ import annotations

import streamlit as st

from career.bilingual import (
    join_items,
    split_items,
)
from career.education import (
    EducationRecord,
)
from career.education_database import (
    delete_education_record,
    get_education_records,
    save_education_record,
)


def _language_view() -> str:
    return st.session_state.get(
        "career_profile_output_language",
        "Both / Beide",
    )


def _render_summary(
    record: EducationRecord,
) -> None:
    language = _language_view()

    date_text = record.start_date

    if record.is_current:
        date_text += " — Present / Heute"
    elif record.end_date:
        date_text += (
            f" — {record.end_date}"
        )

    st.write(
        f"**{record.institution}**"
    )

    if (
        language in (
            "Both / Beide",
            "English",
        )
        and record.degree_en
    ):
        st.write(
            f"**EN:** {record.degree_en}"
        )

        if record.field_of_study_en:
            st.write(
                record.field_of_study_en
            )

    if (
        language in (
            "Both / Beide",
            "Deutsch",
        )
        and record.degree_de
    ):
        st.write(
            f"**DE:** {record.degree_de}"
        )

        if record.field_of_study_de:
            st.write(
                record.field_of_study_de
            )

    st.caption(
        " | ".join(
            item
            for item in [
                record.location,
                record.country,
                date_text,
                (
                    f"Grade / Note: {record.grade}"
                    if record.grade
                    else ""
                ),
            ]
            if item
        )
    )

    if language in (
        "Both / Beide",
        "English",
    ):
        if record.thesis_title_en:
            st.write(
                "**Thesis:** "
                + record.thesis_title_en
            )

        if record.description_en:
            st.write(
                record.description_en
            )

        if record.achievements_en:
            st.markdown(
                "**Highlights — English**"
            )

            for item in record.achievements_en:
                st.markdown(
                    f"- {item}"
                )

    if language in (
        "Both / Beide",
        "Deutsch",
    ):
        if record.thesis_title_de:
            st.write(
                "**Abschlussarbeit:** "
                + record.thesis_title_de
            )

        if record.description_de:
            st.write(
                record.description_de
            )

        if record.achievements_de:
            st.markdown(
                "**Highlights — Deutsch**"
            )

            for item in record.achievements_de:
                st.markdown(
                    f"- {item}"
                )

    if record.verified:
        st.success(
            "Verified education / Verifizierte Ausbildung"
        )
    else:
        st.warning(
            "Not verified / Noch nicht verifiziert"
        )


def _render_form(
    *,
    form_key: str,
    record: EducationRecord | None = None,
    submit_label: str,
) -> bool:
    original = record or EducationRecord()

    with st.form(
        form_key,
        clear_on_submit=False,
    ):
        st.markdown(
            "#### Institution and Degree / Hochschule und Abschluss"
        )

        col1, col2 = st.columns(2)

        with col1:
            institution = st.text_input(
                "Institution / Hochschule *",
                value=original.institution,
                key=f"{form_key}_institution",
            )

            degree_en = st.text_input(
                "Degree — English *",
                value=original.degree_en,
                placeholder="Master of Science",
                key=f"{form_key}_degree_en",
            )

            field_of_study_en = (
                st.text_input(
                    "Field of Study — English",
                    value=original.field_of_study_en,
                    placeholder=(
                        "Automotive Software Engineering"
                    ),
                    key=(
                        f"{form_key}_field_en"
                    ),
                )
            )

            location = st.text_input(
                "Location / Ort",
                value=original.location,
                key=f"{form_key}_location",
            )

            start_date = st.text_input(
                "Start Date / Startdatum *",
                value=original.start_date,
                placeholder="2023-10",
                key=f"{form_key}_start_date",
            )

        with col2:
            degree_de = st.text_input(
                "Abschluss — Deutsch",
                value=original.degree_de,
                placeholder=(
                    "Master of Science"
                ),
                key=f"{form_key}_degree_de",
            )

            field_of_study_de = (
                st.text_input(
                    "Studiengang — Deutsch",
                    value=original.field_of_study_de,
                    placeholder=(
                        "Automotive Software Engineering"
                    ),
                    key=(
                        f"{form_key}_field_de"
                    ),
                )
            )

            country = st.text_input(
                "Country / Land",
                value=original.country,
                key=f"{form_key}_country",
            )

            grade = st.text_input(
                "Grade / Note",
                value=original.grade,
                key=f"{form_key}_grade",
            )

            is_current = st.checkbox(
                "Currently studying / Aktuelles Studium",
                value=original.is_current,
                key=f"{form_key}_is_current",
            )

            end_date = st.text_input(
                "End Date / Enddatum",
                value=original.end_date,
                placeholder="2026-12",
                disabled=is_current,
                key=f"{form_key}_end_date",
            )

        st.markdown(
            "#### Thesis / Abschlussarbeit"
        )

        thesis_title_en = st.text_area(
            "Thesis Title — English",
            value=original.thesis_title_en,
            height=90,
            key=f"{form_key}_thesis_en",
        )

        thesis_title_de = st.text_area(
            "Titel der Abschlussarbeit — Deutsch",
            value=original.thesis_title_de,
            height=90,
            key=f"{form_key}_thesis_de",
        )

        st.markdown(
            "#### Description / Beschreibung"
        )

        description_en = st.text_area(
            "Description — English",
            value=original.description_en,
            height=120,
            key=f"{form_key}_description_en",
        )

        description_de = st.text_area(
            "Beschreibung — Deutsch",
            value=original.description_de,
            height=120,
            key=f"{form_key}_description_de",
        )

        st.markdown(
            "#### Highlights / Schwerpunkte"
        )

        col3, col4 = st.columns(2)

        with col3:
            achievements_en_text = (
                st.text_area(
                    "Highlights — English",
                    value=join_items(
                        original.achievements_en
                    ),
                    height=140,
                    placeholder=(
                        "One item per line..."
                    ),
                    key=(
                        f"{form_key}_achievements_en"
                    ),
                )
            )

        with col4:
            achievements_de_text = (
                st.text_area(
                    "Highlights — Deutsch",
                    value=join_items(
                        original.achievements_de
                    ),
                    height=140,
                    placeholder=(
                        "Ein Punkt pro Zeile..."
                    ),
                    key=(
                        f"{form_key}_achievements_de"
                    ),
                )
            )

        verified = st.checkbox(
            "I confirm this education record is accurate. / "
            "Ich bestätige, dass diese Ausbildungsangaben korrekt sind.",
            value=original.verified,
            key=f"{form_key}_verified",
        )

        submitted = st.form_submit_button(
            submit_label,
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return False

    candidate = EducationRecord(
        id=original.id,
        institution=institution,
        degree_en=degree_en,
        degree_de=degree_de,
        field_of_study_en=(
            field_of_study_en
        ),
        field_of_study_de=(
            field_of_study_de
        ),
        location=location,
        country=country,
        start_date=start_date,
        end_date=(
            ""
            if is_current
            else end_date
        ),
        is_current=is_current,
        grade=grade,
        thesis_title_en=thesis_title_en,
        thesis_title_de=thesis_title_de,
        description_en=description_en,
        description_de=description_de,
        achievements_en=split_items(
            achievements_en_text
        ),
        achievements_de=split_items(
            achievements_de_text
        ),
        verified=verified,
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Institution, start date and at least one degree title "
            "are required. / Hochschule, Startdatum und mindestens "
            "eine Abschlussbezeichnung sind erforderlich."
        )

        return False

    save_education_record(
        candidate
    )

    st.success(
        "Education record saved. / Ausbildungsangaben gespeichert."
    )

    return True


def render_education_section() -> None:
    st.divider()

    st.subheader(
        "Education / Ausbildung & Studium"
    )

    st.caption(
        "Store each degree or major education record separately. "
        "These verified records will later feed the English and German "
        "Master CV and interview preparation."
    )

    records = get_education_records()

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "Education Records / Einträge",
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

    with st.expander(
        "➕ Add Education / Ausbildung hinzufügen",
        expanded=not records,
    ):
        saved = _render_form(
            form_key="career_add_education",
            submit_label=(
                "Add Education / Ausbildung hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_education_id",
                None,
            )
            st.rerun()

    if not records:
        st.info(
            "No education records have been added yet. / "
            "Noch keine Ausbildungsangaben hinzugefügt."
        )

        return

    st.markdown(
        "### Saved Education / Gespeicherte Ausbildung"
    )

    edit_id = st.session_state.get(
        "career_edit_education_id"
    )

    for record in records:
        label = (
            f"{record.display_title()} — "
            f"{record.institution}"
        )

        with st.expander(
            label,
            expanded=(
                edit_id == record.id
            ),
        ):
            _render_summary(
                record
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "✏️ Edit / Bearbeiten",
                    key=(
                        f"career_edit_education_"
                        f"{record.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_education_id"
                    ] = record.id

                    st.rerun()

            with col2:
                confirm_delete = st.checkbox(
                    "Confirm delete / Löschen bestätigen",
                    key=(
                        f"career_confirm_delete_education_"
                        f"{record.id}"
                    ),
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_education_"
                        f"{record.id}"
                    ),
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_education_record(
                        record.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_education_id"
                        )
                        == record.id
                    ):
                        st.session_state.pop(
                            "career_edit_education_id",
                            None,
                        )

                    st.rerun()

            if edit_id == record.id:
                st.divider()

                st.markdown(
                    "#### Edit Education / Ausbildung bearbeiten"
                )

                saved = _render_form(
                    form_key=(
                        f"career_update_education_"
                        f"{record.id}"
                    ),
                    record=record,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_education_id",
                        None,
                    )

                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_education_"
                        f"{record.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_education_id",
                        None,
                    )

                    st.rerun()
