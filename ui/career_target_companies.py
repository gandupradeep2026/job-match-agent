from __future__ import annotations

import streamlit as st

from career.bilingual import (
    join_items,
    split_items,
)
from career.target_company import (
    TargetCompany,
)
from career.target_company_database import (
    delete_target_company,
    get_target_companies,
    save_target_company,
)


PRIORITIES = [
    "A — Dream Company",
    "B — Strong Target",
    "C — Secondary Target",
]


STATUSES = [
    "Researching",
    "Ready to Apply",
    "Applied",
    "Recruiter Contact",
    "Interviewing",
    "On Hold",
    "Rejected",
    "Offer",
]


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


def _language_view() -> str:
    return st.session_state.get(
        "career_profile_output_language",
        "Both / Beide",
    )


def _render_summary(
    record: TargetCompany,
) -> None:
    language = _language_view()

    st.write(
        f"**{record.company_name}**"
    )

    st.caption(
        " | ".join(
            item
            for item in [
                record.priority,
                record.status,
                record.industry,
                record.headquarters,
            ]
            if item
        )
    )

    if record.germany_locations:
        st.write(
            "**Germany Locations / Standorte in Deutschland:** "
            + ", ".join(
                record.germany_locations
            )
        )

    if record.target_roles:
        st.write(
            "**Target Roles / Zielrollen:** "
            + ", ".join(
                record.target_roles
            )
        )

    if record.technologies:
        st.write(
            "**Technologies / Technologien:** "
            + ", ".join(
                record.technologies
            )
        )

    if language in (
        "Both / Beide",
        "English",
    ):
        if record.why_company_en:
            st.markdown(
                "**Why this company — English**"
            )
            st.write(
                record.why_company_en
            )

        if record.why_fit_en:
            st.markdown(
                "**Why I fit — English**"
            )
            st.write(
                record.why_fit_en
            )

        if record.next_action_en:
            st.markdown(
                "**Next action — English**"
            )
            st.write(
                record.next_action_en
            )

    if language in (
        "Both / Beide",
        "Deutsch",
    ):
        if record.why_company_de:
            st.markdown(
                "**Warum dieses Unternehmen — Deutsch**"
            )
            st.write(
                record.why_company_de
            )

        if record.why_fit_de:
            st.markdown(
                "**Warum ich passe — Deutsch**"
            )
            st.write(
                record.why_fit_de
            )

        if record.next_action_de:
            st.markdown(
                "**Nächster Schritt — Deutsch**"
            )
            st.write(
                record.next_action_de
            )

    if record.contact_name:
        contact_bits = [
            record.contact_name,
            record.contact_role,
            record.contact_email,
        ]

        st.write(
            "**Contact / Kontakt:** "
            + " | ".join(
                item
                for item in contact_bits
                if item
            )
        )

    if record.careers_url:
        st.write(
            "**Careers:** "
            + record.careers_url
        )

    if record.last_researched_date:
        st.caption(
            "Last researched / Zuletzt recherchiert: "
            + record.last_researched_date
        )


def _render_form(
    *,
    form_key: str,
    record: TargetCompany | None = None,
    submit_label: str,
) -> bool:
    original = (
        record
        or TargetCompany()
    )

    with st.form(
        form_key,
        clear_on_submit=False,
    ):
        st.markdown(
            "#### Company / Unternehmen"
        )

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input(
                "Company Name / Unternehmensname *",
                value=original.company_name,
                key=f"{form_key}_company_name",
            )

            priority = st.selectbox(
                "Priority / Priorität",
                PRIORITIES,
                index=_safe_index(
                    PRIORITIES,
                    original.priority,
                ),
                key=f"{form_key}_priority",
            )

            industry = st.text_input(
                "Industry / Branche",
                value=original.industry,
                key=f"{form_key}_industry",
            )

            headquarters = st.text_input(
                "Headquarters / Hauptsitz",
                value=original.headquarters,
                key=f"{form_key}_headquarters",
            )

        with col2:
            status = st.selectbox(
                "Pipeline Status",
                STATUSES,
                index=_safe_index(
                    STATUSES,
                    original.status,
                ),
                key=f"{form_key}_status",
            )

            germany_locations_text = (
                st.text_area(
                    "Germany Locations / Standorte in Deutschland",
                    value=join_items(
                        original.germany_locations
                    ),
                    height=100,
                    placeholder=(
                        "Berlin\nMunich\nRemote Germany"
                    ),
                    key=(
                        f"{form_key}_germany_locations"
                    ),
                )
            )

            last_researched_date = (
                st.text_input(
                    "Last Researched / Zuletzt recherchiert",
                    value=(
                        original.last_researched_date
                    ),
                    placeholder="2026-08-14",
                    key=(
                        f"{form_key}_last_researched_date"
                    ),
                )
            )

        st.markdown(
            "#### Target Roles and Technology / Zielrollen und Technologie"
        )

        col3, col4 = st.columns(2)

        with col3:
            target_roles_text = st.text_area(
                "Target Roles / Zielrollen",
                value=join_items(
                    original.target_roles
                ),
                height=130,
                placeholder=(
                    "Data Engineer\nCloud Data Engineer"
                ),
                key=f"{form_key}_target_roles",
            )

        with col4:
            technologies_text = st.text_area(
                "Relevant Technologies / Relevante Technologien",
                value=join_items(
                    original.technologies
                ),
                height=130,
                placeholder=(
                    "GCP\nBigQuery\nSpark\nPython"
                ),
                key=f"{form_key}_technologies",
            )

        st.markdown(
            "#### Company Links / Unternehmenslinks"
        )

        careers_url = st.text_input(
            "Careers URL",
            value=original.careers_url,
            key=f"{form_key}_careers_url",
        )

        company_url = st.text_input(
            "Company Website",
            value=original.company_url,
            key=f"{form_key}_company_url",
        )

        linkedin_url = st.text_input(
            "Company LinkedIn",
            value=original.linkedin_url,
            key=f"{form_key}_linkedin_url",
        )

        st.markdown(
            "#### Contact / Kontakt"
        )

        col5, col6 = st.columns(2)

        with col5:
            contact_name = st.text_input(
                "Contact Name / Kontaktname",
                value=original.contact_name,
                key=f"{form_key}_contact_name",
            )

            contact_role = st.text_input(
                "Contact Role / Funktion",
                value=original.contact_role,
                key=f"{form_key}_contact_role",
            )

        with col6:
            contact_email = st.text_input(
                "Contact Email / Kontakt-E-Mail",
                value=original.contact_email,
                key=f"{form_key}_contact_email",
            )

            contact_linkedin = st.text_input(
                "Contact LinkedIn",
                value=original.contact_linkedin,
                key=f"{form_key}_contact_linkedin",
            )

        st.markdown(
            "#### Why This Company? / Warum dieses Unternehmen?"
        )

        why_company_en = st.text_area(
            "Why This Company — English",
            value=original.why_company_en,
            height=120,
            key=f"{form_key}_why_company_en",
        )

        why_company_de = st.text_area(
            "Warum dieses Unternehmen — Deutsch",
            value=original.why_company_de,
            height=120,
            key=f"{form_key}_why_company_de",
        )

        st.markdown(
            "#### Why Do I Fit? / Warum passe ich?"
        )

        why_fit_en = st.text_area(
            "Why I Fit — English",
            value=original.why_fit_en,
            height=120,
            key=f"{form_key}_why_fit_en",
        )

        why_fit_de = st.text_area(
            "Warum ich passe — Deutsch",
            value=original.why_fit_de,
            height=120,
            key=f"{form_key}_why_fit_de",
        )

        st.markdown(
            "#### Next Action / Nächster Schritt"
        )

        next_action_en = st.text_area(
            "Next Action — English",
            value=original.next_action_en,
            height=90,
            key=f"{form_key}_next_action_en",
        )

        next_action_de = st.text_area(
            "Nächster Schritt — Deutsch",
            value=original.next_action_de,
            height=90,
            key=f"{form_key}_next_action_de",
        )

        st.markdown(
            "#### Notes / Notizen"
        )

        notes_en = st.text_area(
            "Notes — English",
            value=original.notes_en,
            height=100,
            key=f"{form_key}_notes_en",
        )

        notes_de = st.text_area(
            "Notizen — Deutsch",
            value=original.notes_de,
            height=100,
            key=f"{form_key}_notes_de",
        )

        submitted = st.form_submit_button(
            submit_label,
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return False

    candidate = TargetCompany(
        id=original.id,
        company_name=company_name,
        priority=priority,
        status=status,
        industry=industry,
        headquarters=headquarters,
        germany_locations=split_items(
            germany_locations_text
        ),
        target_roles=split_items(
            target_roles_text
        ),
        technologies=split_items(
            technologies_text
        ),
        careers_url=careers_url,
        company_url=company_url,
        linkedin_url=linkedin_url,
        contact_name=contact_name,
        contact_role=contact_role,
        contact_email=contact_email,
        contact_linkedin=contact_linkedin,
        why_company_en=why_company_en,
        why_company_de=why_company_de,
        why_fit_en=why_fit_en,
        why_fit_de=why_fit_de,
        next_action_en=next_action_en,
        next_action_de=next_action_de,
        notes_en=notes_en,
        notes_de=notes_de,
        last_researched_date=(
            last_researched_date
        ),
        created_at=original.created_at,
    )

    if not candidate.has_required_fields():
        st.error(
            "Company name is required. / Unternehmensname ist erforderlich."
        )

        return False

    save_target_company(
        candidate
    )

    st.success(
        "Target company saved. / Zielunternehmen gespeichert."
    )

    return True


def render_target_companies_section() -> None:
    st.divider()

    st.subheader(
        "Target Companies / Zielunternehmen"
    )

    st.caption(
        "Build and manage your personal Germany-focused company pipeline. "
        "Later this will connect to job discovery, CV tailoring and interview preparation."
    )

    records = get_target_companies()

    a_count = sum(
        1
        for item in records
        if item.priority
        == "A — Dream Company"
    )

    ready_count = sum(
        1
        for item in records
        if item.status
        in {
            "Ready to Apply",
            "Applied",
            "Recruiter Contact",
            "Interviewing",
            "Offer",
        }
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:
        st.metric(
            "Target Companies / Zielunternehmen",
            len(records),
        )

    with col2:
        st.metric(
            "A-Priority",
            a_count,
        )

    with col3:
        st.metric(
            "Active Pipeline",
            ready_count,
        )

    with st.expander(
        "➕ Add Target Company / Zielunternehmen hinzufügen",
        expanded=not records,
    ):
        saved = _render_form(
            form_key=(
                "career_add_target_company"
            ),
            submit_label=(
                "Add Target Company / Zielunternehmen hinzufügen"
            ),
        )

        if saved:
            st.session_state.pop(
                "career_edit_target_company_id",
                None,
            )

            st.rerun()

    if not records:
        st.info(
            "No target companies have been added yet. / "
            "Noch keine Zielunternehmen hinzugefügt."
        )

        return

    st.markdown(
        "### Company Pipeline / Unternehmenspipeline"
    )

    filter_col1, filter_col2 = (
        st.columns(2)
    )

    with filter_col1:
        priority_filter = st.selectbox(
            "Filter by Priority / Priorität",
            [
                "All / Alle",
                *PRIORITIES,
            ],
            key=(
                "career_target_company_priority_filter"
            ),
        )

    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            [
                "All / Alle",
                *STATUSES,
            ],
            key=(
                "career_target_company_status_filter"
            ),
        )

    filtered = records

    if priority_filter != "All / Alle":
        filtered = [
            item
            for item in filtered
            if item.priority
            == priority_filter
        ]

    if status_filter != "All / Alle":
        filtered = [
            item
            for item in filtered
            if item.status
            == status_filter
        ]

    edit_id = (
        st.session_state.get(
            "career_edit_target_company_id"
        )
    )

    for record in filtered:
        label = (
            f"{record.priority} | "
            f"{record.company_name} | "
            f"{record.status}"
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
                        f"career_edit_target_company_"
                        f"{record.id}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "career_edit_target_company_id"
                    ] = record.id

                    st.rerun()

            with col2:
                confirm_delete = (
                    st.checkbox(
                        "Confirm delete / Löschen bestätigen",
                        key=(
                            "career_confirm_delete_target_company_"
                            f"{record.id}"
                        ),
                    )
                )

                if st.button(
                    "🗑️ Delete / Löschen",
                    key=(
                        f"career_delete_target_company_"
                        f"{record.id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_target_company(
                        record.id
                    )

                    if (
                        st.session_state.get(
                            "career_edit_target_company_id"
                        )
                        == record.id
                    ):
                        st.session_state.pop(
                            "career_edit_target_company_id",
                            None,
                        )

                    st.rerun()

            if edit_id == record.id:
                st.divider()

                st.markdown(
                    "#### Edit Target Company / Zielunternehmen bearbeiten"
                )

                saved = _render_form(
                    form_key=(
                        f"career_update_target_company_"
                        f"{record.id}"
                    ),
                    record=record,
                    submit_label=(
                        "Save Changes / Änderungen speichern"
                    ),
                )

                if saved:
                    st.session_state.pop(
                        "career_edit_target_company_id",
                        None,
                    )

                    st.rerun()

                if st.button(
                    "Cancel Edit / Bearbeiten abbrechen",
                    key=(
                        f"career_cancel_target_company_"
                        f"{record.id}"
                    ),
                ):
                    st.session_state.pop(
                        "career_edit_target_company_id",
                        None,
                    )

                    st.rerun()
