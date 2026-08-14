from __future__ import annotations

import streamlit as st

from career.application_tracker_link import (
    CareerApplicationLink,
)
from career.application_tracker_service import (
    INTERVIEW_PACK_LANGUAGES,
    PREPARATION_STAGES,
    get_career_application_link,
    get_career_application_overview,
    save_career_application_link,
    suggest_target_company_id,
)
from career.target_company_database import (
    get_target_companies,
)
from services.job_tracker import (
    get_all_applications,
    get_application_by_id,
)


def _safe_index(
    values: list[str],
    value: str,
) -> int:
    try:
        return values.index(
            value
        )
    except ValueError:
        return 0


def render_application_tracker_integration_section() -> None:
    st.divider()

    st.subheader(
        "Application Tracker Integration / Bewerbungs-Tracker-Integration"
    )

    st.caption(
        "Connect each tracked application to its Career Agent preparation: "
        "target company, target role, tailored CV, interview pack and next action."
    )

    applications = (
        get_all_applications()
    )

    if not applications:
        st.info(
            "No tracked applications are available yet. Add an application "
            "in Application Tracker first. / Noch keine Bewerbungen vorhanden."
        )
        return

    overview = (
        get_career_application_overview()
    )

    linked_count = sum(
        1
        for item in overview
        if item["target_company"]
    )

    interview_ready_count = sum(
        1
        for item in overview
        if (
            item["interview_pack_ready"]
            and item["preparation_stage"]
            in {
                "Interview Prep",
                "Interview Ready",
            }
        )
    )

    cv_ready_count = sum(
        1
        for item in overview
        if item["tailored_cv_ready"]
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:
        st.metric(
            "Applications",
            len(
                overview
            ),
        )

    with col2:
        st.metric(
            "Company Linked",
            linked_count,
        )

    with col3:
        st.metric(
            "CV Ready",
            cv_ready_count,
        )

    with col4:
        st.metric(
            "Interview Ready",
            interview_ready_count,
        )

    st.markdown(
        "### Career Preparation Overview"
    )

    st.dataframe(
        overview,
        use_container_width=True,
        hide_index=True,
    )

    application_options = {
        (
            f"ID {item['id']} — "
            f"{item.get('company', '')} — "
            f"{item.get('job_title', '')}"
        ): item["id"]
        for item in applications
    }

    selected_label = st.selectbox(
        "Select Application / Bewerbung auswählen",
        list(
            application_options.keys()
        ),
        key=(
            "career_tracker_selected_application"
        ),
    )

    application_id = (
        application_options[
            selected_label
        ]
    )

    application = (
        get_application_by_id(
            application_id
        )
    )

    link = (
        get_career_application_link(
            application_id
        )
    )

    if (
        application is None
        or link is None
    ):
        st.error(
            "The selected application could not be loaded."
        )
        return

    target_companies = (
        get_target_companies()
    )

    suggested_company_id = (
        suggest_target_company_id(
            application,
            target_companies,
        )
    )

    company_options = [
        (
            None,
            "No target-company link / Kein Zielunternehmen verknüpft",
        ),
        *[
            (
                item.id,
                item.company_name,
            )
            for item in target_companies
        ],
    ]

    company_labels = [
        label
        for _, label
        in company_options
    ]

    company_id_to_label = {
        company_id: label
        for company_id, label
        in company_options
    }

    selected_company_id = (
        link.target_company_id
    )

    if (
        selected_company_id is None
        and suggested_company_id
        is not None
    ):
        selected_company_id = (
            suggested_company_id
        )

    default_company_label = (
        company_id_to_label.get(
            selected_company_id,
            company_labels[0],
        )
    )

    with st.form(
        "career_tracker_link_form"
    ):
        st.markdown(
            f"**Tracked application:** "
            f"{application.get('company', '')} — "
            f"{application.get('job_title', '')}"
        )

        if (
            suggested_company_id
            is not None
            and link.target_company_id
            is None
        ):
            st.info(
                "An exact company-name match was found in Target Companies "
                "and has been suggested automatically."
            )

        company_label = st.selectbox(
            "Target Company / Zielunternehmen",
            company_labels,
            index=company_labels.index(
                default_company_label
            ),
            key=(
                "career_tracker_target_company"
            ),
        )

        target_company_id = dict(
            (
                label,
                company_id,
            )
            for company_id, label
            in company_options
        )[
            company_label
        ]

        col1, col2 = st.columns(2)

        with col1:
            career_target_role = (
                st.text_input(
                    "Career Target Role / Karriere-Zielrolle",
                    value=(
                        link.career_target_role
                        or application.get(
                            "job_title",
                            "",
                        )
                    ),
                    key=(
                        "career_tracker_target_role"
                    ),
                )
            )

            preparation_stage = (
                st.selectbox(
                    "Preparation Stage / Vorbereitungsphase",
                    PREPARATION_STAGES,
                    index=_safe_index(
                        PREPARATION_STAGES,
                        link.preparation_stage,
                    ),
                    key=(
                        "career_tracker_preparation_stage"
                    ),
                )
            )

            interview_pack_language = (
                st.selectbox(
                    "Interview Pack Language / Sprache",
                    INTERVIEW_PACK_LANGUAGES,
                    index=_safe_index(
                        INTERVIEW_PACK_LANGUAGES,
                        link.interview_pack_language,
                    ),
                    key=(
                        "career_tracker_interview_language"
                    ),
                )
            )

        with col2:
            tailored_cv_ready = (
                st.checkbox(
                    "Tailored CV ready / Angepasster CV fertig",
                    value=(
                        link.tailored_cv_ready
                    ),
                    key=(
                        "career_tracker_cv_ready"
                    ),
                )
            )

            interview_pack_ready = (
                st.checkbox(
                    "Interview Pack ready / Interview-Paket fertig",
                    value=(
                        link.interview_pack_ready
                    ),
                    key=(
                        "career_tracker_pack_ready"
                    ),
                )
            )

        career_next_action = (
            st.text_area(
                "Next Career Action / Nächster Karriereschritt",
                value=(
                    link.career_next_action
                ),
                height=100,
                placeholder=(
                    "Example: Tailor German CV and apply before Friday."
                ),
                key=(
                    "career_tracker_next_action"
                ),
            )
        )

        career_notes = (
            st.text_area(
                "Career Preparation Notes / Notizen",
                value=(
                    link.career_notes
                ),
                height=110,
                key=(
                    "career_tracker_notes"
                ),
            )
        )

        submitted = (
            st.form_submit_button(
                "Save Career Link / Karriere-Verknüpfung speichern",
                type="primary",
                use_container_width=True,
            )
        )

    if submitted:
        try:
            saved = (
                save_career_application_link(
                    CareerApplicationLink(
                        application_id=(
                            application_id
                        ),
                        target_company_id=(
                            target_company_id
                        ),
                        career_target_role=(
                            career_target_role
                        ),
                        preparation_stage=(
                            preparation_stage
                        ),
                        tailored_cv_ready=(
                            tailored_cv_ready
                        ),
                        interview_pack_ready=(
                            interview_pack_ready
                        ),
                        interview_pack_language=(
                            interview_pack_language
                        ),
                        career_next_action=(
                            career_next_action
                        ),
                        career_notes=(
                            career_notes
                        ),
                    )
                )
            )

            st.success(
                "Application linked to Career Agent preparation. / "
                "Bewerbung mit der Karrierevorbereitung verknüpft."
            )

            st.caption(
                "Last synced: "
                + saved.last_career_sync_at
            )

            st.rerun()

        except Exception as error:
            st.error(
                f"{type(error).__name__}: {error}"
            )
