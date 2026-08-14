from __future__ import annotations

import streamlit as st

from career.bilingual import join_items, split_items
from career.work_experience import WorkExperience
from career.work_experience_database import (
    delete_work_experience,
    get_work_experiences,
    save_work_experience,
)


def _language_view() -> str:
    return st.session_state.get(
        "career_profile_output_language",
        "Both / Beide",
    )


def _render_experience_summary(
    experience: WorkExperience,
) -> None:
    language = _language_view()

    date_text = experience.start_date
    if experience.is_current:
        date_text += " — Present / Heute"
    elif experience.end_date:
        date_text += f" — {experience.end_date}"

    st.write(f"**{experience.employer}**")

    if (
        language in ("Both / Beide", "English")
        and experience.job_title_en
    ):
        st.write(f"**EN:** {experience.job_title_en}")

    if (
        language in ("Both / Beide", "Deutsch")
        and experience.job_title_de
    ):
        st.write(f"**DE:** {experience.job_title_de}")

    st.caption(
        " | ".join(
            item
            for item in [
                experience.location,
                experience.country,
                date_text,
                experience.employment_type,
            ]
            if item
        )
    )

    if language in ("Both / Beide", "English"):
        if experience.description_en:
            st.write(experience.description_en)

        if experience.achievements_en:
            st.markdown("**Achievements — English**")
            for achievement in experience.achievements_en:
                st.markdown(f"- {achievement}")

    if language in ("Both / Beide", "Deutsch"):
        if experience.description_de:
            st.write(experience.description_de)

        if experience.achievements_de:
            st.markdown("**Erfolge — Deutsch**")
            for achievement in experience.achievements_de:
                st.markdown(f"- {achievement}")

    if experience.technologies:
        st.write(
            "**Technologies / Technologien:** "
            + ", ".join(experience.technologies)
        )

    if experience.verified:
        st.success(
            "Verified experience / Verifizierte Berufserfahrung"
        )
    else:
        st.warning(
            "Not verified / Noch nicht verifiziert"
        )


def _render_experience_form(
    *,
    form_key: str,
    experience: WorkExperience | None = None,
    submit_label: str,
) -> bool:
    original = experience or WorkExperience()

    with st.form(form_key, clear_on_submit=False):
        st.markdown(
            "#### Employer and Role / Arbeitgeber und Position"
        )

        col1, col2 = st.columns(2)

        with col1:
            employer = st.text_input(
                "Employer / Arbeitgeber *",
                value=original.employer,
                key=f"{form_key}_employer",
            )

            job_title_en = st.text_input(
                "Job Title — English *",
                value=original.job_title_en,
                key=f"{form_key}_job_title_en",
            )

            location = st.text_input(
                "Location / Ort",
                value=original.location,
                key=f"{form_key}_location",
            )

            start_date = st.text_input(
                "Start Date / Startdatum *",
                value=original.start_date,
                placeholder="2024-04",
                key=f"{form_key}_start_date",
            )

        with col2:
            job_title_de = st.text_input(
                "Position — Deutsch",
                value=original.job_title_de,
                key=f"{form_key}_job_title_de",
            )

            country = st.text_input(
                "Country / Land",
                value=original.country,
                key=f"{form_key}_country",
            )

            employment_type = st.text_input(
                "Employment Type / Beschäftigungsart",
                value=original.employment_type,
                placeholder="Full-time / Vollzeit",
                key=f"{form_key}_employment_type",
            )

            is_current = st.checkbox(
                "Current position / Aktuelle Position",
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
            "#### Role Description / Tätigkeitsbeschreibung"
        )

        description_en = st.text_area(
            "Description — English",
            value=original.description_en,
            height=130,
            key=f"{form_key}_description_en",
        )

        description_de = st.text_area(
            "Beschreibung — Deutsch",
            value=original.description_de,
            height=130,
            key=f"{form_key}_description_de",
        )

        st.markdown("#### Achievements / Erfolge")
        col3, col4 = st.columns(2)

        with col3:
            achievements_en_text = st.text_area(
                "Achievements — English",
                value=join_items(
                    original.achievements_en
                ),
                height=150,
                placeholder="One achievement per line...",
                key=f"{form_key}_achievements_en",
            )

        with col4:
            achievements_de_text = st.text_area(
                "Erfolge — Deutsch",
                value=join_items(
                    original.achievements_de
                ),
                height=150,
                placeholder="Ein Erfolg pro Zeile...",
                key=f"{form_key}_achievements_de",
            )

        technologies_text = st.text_area(
            "Technologies / Technologien",
            value=join_items(
                original.technologies
            ),
            height=120,
            placeholder=(
                "Python\nSQL\nGoogle Cloud Platform"
            ),
            key=f"{form_key}_technologies",
        )

        verified = st.checkbox(
            "I confirm this employment record is accurate. / "
            "Ich bestätige, dass diese Berufserfahrung korrekt ist.",
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

    candidate = WorkExperience(
        id=original.id,
        employer=employer,
        job_title_en=job_title_en,
        job_title_de=job_title_de,
        location=location,
        country=country,
        start_date=start_date,
        end_date="" if is_current else end_date,
        is_current=is_current,
        employment_type=employment_type,
        description_en=description_en,
        description_de=description_de,
        achievements_en=split_items(
            achievements_en_text
        ),
        achievements_de=split_items(
            achievements_de_text
        ),
        technologies=split_items(
            technologies_text
        ),
        verified=verified,
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Employer, start date and at least one job title are required. / "
            "Arbeitgeber, Startdatum und mindestens eine Positionsbezeichnung "
            "sind erforderlich."
        )
        return False

    save_work_experience(candidate)

    st.success(
        "Work experience saved. / Berufserfahrung gespeichert."
    )

    return True


def render_work_experience_section() -> None:
    st.divider()
    st.subheader(
        "Work Experience / Berufserfahrung"
    )

    st.caption(
        "Add each employer as a structured, verifiable record. "
        "These records will later feed the Master CV, personal elevator "
        "pitch and STAR interview stories."
    )

    experiences = get_work_experiences()

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "Experience Records / Einträge",
            len(experiences),
        )

    with metric2:
        st.metric(
            "Verified / Verifiziert",
            sum(
                1
                for item in experiences
                if item.verified
            ),
        )

    with st.expander(
        "➕ Add Work Experience / Berufserfahrung hinzufügen",
        expanded=not experiences,
    ):
        saved = _render_experience_form(
            form_key="career_add_experience",
            submit_label=(
                "Add Work Experience / Berufserfahrung hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_experience_id",
                None,
            )
            st.rerun()

    if not experiences:
        st.info(
            "No work experience has been added yet. / "
            "Noch keine Berufserfahrung hinzugefügt."
        )
        return

    st.markdown(
        "### Saved Experience / Gespeicherte Berufserfahrung"
    )

    edit_id = st.session_state.get(
        "career_edit_experience_id"
    )

    for experience in experiences:
        label = (
            f"{experience.display_title()} — "
            f"{experience.employer}"
        )

        with st.expander(
            label,
            expanded=(edit_id == experience.id),
        ):
            _render_experience_summary(experience)

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "✏️ Edit / Bearbeiten",
                    key=(
                        f"career_edit_experience_"
                        f"{experience.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_experience_id"
                    ] = experience.id
                    st.rerun()

            with col2:
                confirm_delete = st.checkbox(
                    "Confirm delete / Löschen bestätigen",
                    key=(
                        f"career_confirm_delete_"
                        f"{experience.id}"
                    ),
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_experience_"
                        f"{experience.id}"
                    ),
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_work_experience(
                        experience.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_experience_id"
                        )
                        == experience.id
                    ):
                        st.session_state.pop(
                            "career_edit_experience_id",
                            None,
                        )

                    st.rerun()

            if edit_id == experience.id:
                st.divider()
                st.markdown(
                    "#### Edit Experience / Berufserfahrung bearbeiten"
                )

                saved = _render_experience_form(
                    form_key=(
                        f"career_update_experience_"
                        f"{experience.id}"
                    ),
                    experience=experience,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_experience_id",
                        None,
                    )
                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_experience_"
                        f"{experience.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_experience_id",
                        None,
                    )
                    st.rerun()
