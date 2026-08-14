from __future__ import annotations

import streamlit as st

from career.bilingual import (
    join_items,
    split_items,
)
from career.project import (
    ProjectRecord,
)
from career.project_database import (
    delete_project_record,
    get_project_records,
    save_project_record,
)


PROJECT_TYPES = [
    "",
    "Academic Project",
    "Personal Project",
    "Professional Project",
    "Master Thesis",
    "Bachelor Thesis",
    "Open Source Project",
    "Research Project",
    "Portfolio Project",
    "Other",
]


def _language_view() -> str:
    return st.session_state.get(
        "career_profile_output_language",
        "Both / Beide",
    )


def _render_summary(
    record: ProjectRecord,
) -> None:
    language = _language_view()

    date_text = (
        record.start_date
    )

    if record.is_current:
        date_text += (
            " — Present / Heute"
        )
    elif record.end_date:
        date_text += (
            f" — {record.end_date}"
        )

    st.write(
        f"**{record.display_title()}**"
    )

    if record.project_type:
        st.caption(
            f"{record.project_type} | {date_text}"
        )
    else:
        st.caption(
            date_text
        )

    if (
        language in (
            "Both / Beide",
            "English",
        )
        and record.name_en
    ):
        st.write(
            f"**EN:** {record.name_en}"
        )

        if record.role_en:
            st.write(
                f"**Role:** {record.role_en}"
            )

        if record.description_en:
            st.write(
                record.description_en
            )

        if record.responsibilities_en:
            st.markdown(
                "**Responsibilities — English**"
            )

            for item in (
                record.responsibilities_en
            ):
                st.markdown(
                    f"- {item}"
                )

        if record.achievements_en:
            st.markdown(
                "**Results / Achievements — English**"
            )

            for item in (
                record.achievements_en
            ):
                st.markdown(
                    f"- {item}"
                )

    if (
        language in (
            "Both / Beide",
            "Deutsch",
        )
        and record.name_de
    ):
        st.write(
            f"**DE:** {record.name_de}"
        )

        if record.role_de:
            st.write(
                f"**Rolle:** {record.role_de}"
            )

        if record.description_de:
            st.write(
                record.description_de
            )

        if record.responsibilities_de:
            st.markdown(
                "**Aufgaben — Deutsch**"
            )

            for item in (
                record.responsibilities_de
            ):
                st.markdown(
                    f"- {item}"
                )

        if record.achievements_de:
            st.markdown(
                "**Ergebnisse / Erfolge — Deutsch**"
            )

            for item in (
                record.achievements_de
            ):
                st.markdown(
                    f"- {item}"
                )

    if record.technologies:
        st.write(
            "**Technologies / Technologien:** "
            + ", ".join(
                record.technologies
            )
        )

    if record.skills:
        st.write(
            "**Skills / Kompetenzen:** "
            + ", ".join(
                record.skills
            )
        )

    if record.repository_url:
        st.write(
            "**Repository:** "
            + record.repository_url
        )

    if record.demo_url:
        st.write(
            "**Demo:** "
            + record.demo_url
        )

    if record.verified:
        st.success(
            "Verified project / Verifiziertes Projekt"
        )
    else:
        st.warning(
            "Not verified / Noch nicht verifiziert"
        )


def _project_type_index(
    value: str,
) -> int:
    try:
        return PROJECT_TYPES.index(
            value
        )
    except ValueError:
        return 0


def _render_form(
    *,
    form_key: str,
    record: ProjectRecord | None = None,
    submit_label: str,
) -> bool:
    original = (
        record
        or ProjectRecord()
    )

    with st.form(
        form_key,
        clear_on_submit=False,
    ):
        st.markdown(
            "#### Project Identity / Projektinformationen"
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            name_en = st.text_input(
                "Project Name — English *",
                value=original.name_en,
                key=f"{form_key}_name_en",
            )

            role_en = st.text_input(
                "Your Role — English",
                value=original.role_en,
                placeholder=(
                    "Data Engineer / Developer / Researcher"
                ),
                key=f"{form_key}_role_en",
            )

            start_date = st.text_input(
                "Start Date / Startdatum *",
                value=original.start_date,
                placeholder="2026-01",
                key=f"{form_key}_start_date",
            )

            project_type = st.selectbox(
                "Project Type / Projekttyp",
                PROJECT_TYPES,
                index=_project_type_index(
                    original.project_type
                ),
                key=f"{form_key}_project_type",
            )

        with col2:
            name_de = st.text_input(
                "Projektname — Deutsch",
                value=original.name_de,
                key=f"{form_key}_name_de",
            )

            role_de = st.text_input(
                "Ihre Rolle — Deutsch",
                value=original.role_de,
                key=f"{form_key}_role_de",
            )

            is_current = st.checkbox(
                "Current project / Laufendes Projekt",
                value=original.is_current,
                key=f"{form_key}_is_current",
            )

            end_date = st.text_input(
                "End Date / Enddatum",
                value=original.end_date,
                placeholder="2026-08",
                disabled=is_current,
                key=f"{form_key}_end_date",
            )

        st.markdown(
            "#### Project Description / Projektbeschreibung"
        )

        description_en = st.text_area(
            "Description — English",
            value=original.description_en,
            height=140,
            key=f"{form_key}_description_en",
        )

        description_de = st.text_area(
            "Beschreibung — Deutsch",
            value=original.description_de,
            height=140,
            key=f"{form_key}_description_de",
        )

        st.markdown(
            "#### Responsibilities / Aufgaben"
        )

        col3, col4 = st.columns(2)

        with col3:
            responsibilities_en_text = (
                st.text_area(
                    "Responsibilities — English",
                    value=join_items(
                        original.responsibilities_en
                    ),
                    height=150,
                    placeholder=(
                        "One responsibility per line..."
                    ),
                    key=(
                        f"{form_key}_responsibilities_en"
                    ),
                )
            )

        with col4:
            responsibilities_de_text = (
                st.text_area(
                    "Aufgaben — Deutsch",
                    value=join_items(
                        original.responsibilities_de
                    ),
                    height=150,
                    placeholder=(
                        "Eine Aufgabe pro Zeile..."
                    ),
                    key=(
                        f"{form_key}_responsibilities_de"
                    ),
                )
            )

        st.markdown(
            "#### Results / Achievements / Ergebnisse"
        )

        col5, col6 = st.columns(2)

        with col5:
            achievements_en_text = (
                st.text_area(
                    "Results / Achievements — English",
                    value=join_items(
                        original.achievements_en
                    ),
                    height=150,
                    placeholder=(
                        "One measurable result per line..."
                    ),
                    key=(
                        f"{form_key}_achievements_en"
                    ),
                )
            )

        with col6:
            achievements_de_text = (
                st.text_area(
                    "Ergebnisse / Erfolge — Deutsch",
                    value=join_items(
                        original.achievements_de
                    ),
                    height=150,
                    placeholder=(
                        "Ein messbares Ergebnis pro Zeile..."
                    ),
                    key=(
                        f"{form_key}_achievements_de"
                    ),
                )
            )

        col7, col8 = st.columns(2)

        with col7:
            technologies_text = st.text_area(
                "Technologies / Technologien",
                value=join_items(
                    original.technologies
                ),
                height=130,
                placeholder=(
                    "Python\nSQL\nGCP\nSpark"
                ),
                key=(
                    f"{form_key}_technologies"
                ),
            )

        with col8:
            skills_text = st.text_area(
                "Skills / Kompetenzen",
                value=join_items(
                    original.skills
                ),
                height=130,
                placeholder=(
                    "Data Engineering\nETL\nCloud Computing"
                ),
                key=f"{form_key}_skills",
            )

        st.markdown(
            "#### Links"
        )

        repository_url = st.text_input(
            "Repository URL",
            value=(
                original.repository_url
            ),
            key=(
                f"{form_key}_repository_url"
            ),
        )

        demo_url = st.text_input(
            "Demo / Project URL",
            value=original.demo_url,
            key=f"{form_key}_demo_url",
        )

        verified = st.checkbox(
            "I confirm this project record is accurate. / "
            "Ich bestätige, dass diese Projektangaben korrekt sind.",
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

    candidate = ProjectRecord(
        id=original.id,
        name_en=name_en,
        name_de=name_de,
        project_type=project_type,
        role_en=role_en,
        role_de=role_de,
        start_date=start_date,
        end_date=(
            ""
            if is_current
            else end_date
        ),
        is_current=is_current,
        description_en=description_en,
        description_de=description_de,
        responsibilities_en=split_items(
            responsibilities_en_text
        ),
        responsibilities_de=split_items(
            responsibilities_de_text
        ),
        achievements_en=split_items(
            achievements_en_text
        ),
        achievements_de=split_items(
            achievements_de_text
        ),
        technologies=split_items(
            technologies_text
        ),
        skills=split_items(
            skills_text
        ),
        repository_url=repository_url,
        demo_url=demo_url,
        verified=verified,
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Start date and at least one project name are required. / "
            "Startdatum und mindestens ein Projektname sind erforderlich."
        )

        return False

    save_project_record(
        candidate
    )

    st.success(
        "Project saved. / Projekt gespeichert."
    )

    return True


def render_projects_section() -> None:
    st.divider()

    st.subheader(
        "Projects / Projekte"
    )

    st.caption(
        "Store technical, academic, thesis, AI and data-engineering "
        "projects as structured evidence for your Master CV and interviews."
    )

    records = (
        get_project_records()
    )

    metric1, metric2 = (
        st.columns(2)
    )

    with metric1:
        st.metric(
            "Project Records / Projekte",
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
        "➕ Add Project / Projekt hinzufügen",
        expanded=not records,
    ):
        saved = _render_form(
            form_key="career_add_project",
            submit_label=(
                "Add Project / Projekt hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_project_id",
                None,
            )

            st.rerun()

    if not records:
        st.info(
            "No projects have been added yet. / "
            "Noch keine Projekte hinzugefügt."
        )

        return

    st.markdown(
        "### Saved Projects / Gespeicherte Projekte"
    )

    edit_id = (
        st.session_state.get(
            "career_edit_project_id"
        )
    )

    for record in records:
        label = (
            f"{record.display_title()}"
        )

        if record.project_type:
            label += (
                f" — {record.project_type}"
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
                        f"career_edit_project_"
                        f"{record.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_project_id"
                    ] = record.id

                    st.rerun()

            with col2:
                confirm_delete = (
                    st.checkbox(
                        "Confirm delete / Löschen bestätigen",
                        key=(
                            f"career_confirm_delete_project_"
                            f"{record.id}"
                        ),
                    )
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_project_"
                        f"{record.id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_project_record(
                        record.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_project_id"
                        )
                        == record.id
                    ):
                        st.session_state.pop(
                            "career_edit_project_id",
                            None,
                        )

                    st.rerun()

            if edit_id == record.id:
                st.divider()

                st.markdown(
                    "#### Edit Project / Projekt bearbeiten"
                )

                saved = _render_form(
                    form_key=(
                        f"career_update_project_"
                        f"{record.id}"
                    ),
                    record=record,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_project_id",
                        None,
                    )

                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_project_"
                        f"{record.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_project_id",
                        None,
                    )

                    st.rerun()
