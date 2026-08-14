from __future__ import annotations

import streamlit as st

from ui.career_polishing import (
    render_career_polishing_section,
)

from ui.career_dashboard import (
    render_career_dashboard_section,
)

from ui.career_application_tracker import (
    render_application_tracker_integration_section,
)

from ui.career_interview_pack import (
    render_complete_interview_pack_section,
)

from ui.career_interview_preparation import (
    render_interview_preparation_section,
)

from ui.career_star_stories import (
    render_star_story_section,
)

from ui.career_elevator_pitch import (
    render_elevator_pitch_section,
)

from ui.career_target_companies import (
    render_target_companies_section,
)

from ui.career_master_cv import (
    render_master_cv_section,
)

from ui.career_achievements import (
    render_achievements_section,
)

from ui.career_projects import (
    render_projects_section,
)

from ui.career_education import (
    render_education_section,
)

from ui.career_work_experience import (
    render_work_experience_section,
)

from career.bilingual import (
    OUTPUT_LANGUAGE_OPTIONS,
    join_items,
    normalize_output_language,
    split_items,
)
from career.database import load_profile, profile_exists, save_profile
from career.models import CareerProfile


def _render_profile_status(profile: CareerProfile) -> None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Profile / Profil",
            "Saved / Gespeichert" if profile_exists() else "New / Neu",
        )

    with col2:
        st.metric(
            "Truth Lock",
            "Verified / Verifiziert"
            if profile.verified
            else "Not verified / Nicht verifiziert",
        )

    with col3:
        st.metric(
            "Target Roles / Zielrollen",
            len(profile.target_roles),
        )


def render_career_profile_page() -> None:
    st.header("💼 Career Preparation / Karrierevorbereitung")
    st.subheader("Master Career Profile / Master-Karriereprofil")

    st.caption(
        "Your verified career information becomes the trusted source for "
        "future CVs, personal elevator pitches and interview preparation. "
        "Ihre verifizierten Karrieredaten dienen später als verlässliche "
        "Grundlage für Lebensläufe, persönliche Elevator Pitches und "
        "Interviewvorbereitung."
    )

    profile = load_profile()
    _render_profile_status(profile)
    st.divider()

    current_view = normalize_output_language(
        st.session_state.get(
            "career_profile_output_language",
            "Both / Beide",
        )
    )

    output_language = st.radio(
        "Working view / Arbeitsansicht",
        OUTPUT_LANGUAGE_OPTIONS,
        index=OUTPUT_LANGUAGE_OPTIONS.index(current_view),
        horizontal=True,
        key="career_profile_output_language",
    )

    with st.form(
        "master_career_profile_form",
        clear_on_submit=False,
    ):
        st.markdown("### 1. Personal Information / Persönliche Daten")
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name / Vollständiger Name",
                value=profile.full_name,
            )
            email = st.text_input(
                "Email / E-Mail",
                value=profile.email,
            )
            phone = st.text_input(
                "Phone / Telefon",
                value=profile.phone,
            )
            city = st.text_input(
                "City / Stadt",
                value=profile.city,
            )

        with col2:
            country = st.text_input(
                "Country / Land",
                value=profile.country,
            )
            linkedin_url = st.text_input(
                "LinkedIn URL",
                value=profile.linkedin_url,
            )
            github_url = st.text_input(
                "GitHub URL",
                value=profile.github_url,
            )

        st.markdown("### 2. Professional Profile / Berufliches Profil")

        if output_language in ("Both / Beide", "English"):
            professional_summary_en = st.text_area(
                "Professional Summary — English",
                value=profile.professional_summary_en,
                height=180,
            )
        else:
            professional_summary_en = profile.professional_summary_en

        if output_language in ("Both / Beide", "Deutsch"):
            professional_summary_de = st.text_area(
                "Berufliches Profil — Deutsch",
                value=profile.professional_summary_de,
                height=180,
            )
        else:
            professional_summary_de = profile.professional_summary_de

        st.markdown("### 3. Career Targets / Karriereziele")
        col3, col4, col5 = st.columns(3)

        with col3:
            target_roles_text = st.text_area(
                "Target Roles / Zielrollen",
                value=join_items(profile.target_roles),
                height=130,
                placeholder="Data Engineer\nCloud Data Engineer",
            )

        with col4:
            preferred_locations_text = st.text_area(
                "Preferred Locations / Bevorzugte Standorte",
                value=join_items(profile.preferred_locations),
                height=130,
                placeholder="Germany\nBerlin\nMunich",
            )

        with col5:
            employment_types_text = st.text_area(
                "Employment Types / Beschäftigungsarten",
                value=join_items(profile.employment_types),
                height=130,
                placeholder="Full-time\nPermanent",
            )

        st.markdown("### 4. Skills / Kompetenzen")
        col6, col7, col8 = st.columns(3)

        with col6:
            technical_skills_text = st.text_area(
                "Technical Skills / Technische Kenntnisse",
                value=join_items(profile.technical_skills),
                height=180,
            )

        with col7:
            languages_text = st.text_area(
                "Languages / Sprachen",
                value=join_items(profile.languages),
                height=180,
            )

        with col8:
            certifications_text = st.text_area(
                "Certifications / Zertifikate",
                value=join_items(profile.certifications),
                height=180,
            )

        st.markdown("### 5. Truth Lock / Wahrheitsprüfung")

        st.info(
            "When verified, downstream Career Agent features should use "
            "only facts stored in this profile and later verified records."
        )

        verified = st.checkbox(
            "I confirm that the information above is accurate. / "
            "Ich bestätige, dass die oben genannten Angaben korrekt sind.",
            value=profile.verified,
        )

        submitted = st.form_submit_button(
            "Save Master Career Profile / Master-Karriereprofil speichern",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        updated_profile = CareerProfile(
            full_name=full_name,
            email=email,
            phone=phone,
            city=city,
            country=country,
            linkedin_url=linkedin_url,
            github_url=github_url,
            professional_summary_en=professional_summary_en,
            professional_summary_de=professional_summary_de,
            target_roles=split_items(target_roles_text),
            preferred_locations=split_items(preferred_locations_text),
            employment_types=split_items(employment_types_text),
            technical_skills=split_items(technical_skills_text),
            languages=split_items(languages_text),
            certifications=split_items(certifications_text),
            verified=verified,
            created_at=profile.created_at,
        )

        saved = save_profile(updated_profile)

        if not saved.has_basic_identity():
            st.warning(
                "Profile saved, but Full Name and Email are still missing. / "
                "Profil gespeichert, aber Name und E-Mail fehlen noch."
            )
        elif saved.verified:
            st.success(
                "Master Career Profile saved and Truth Lock enabled. / "
                "Master-Karriereprofil gespeichert und Truth Lock aktiviert."
            )
        else:
            st.success(
                "Master Career Profile saved. / "
                "Master-Karriereprofil gespeichert."
            )

        st.rerun()

    render_work_experience_section()

    render_education_section()

    render_projects_section()

    render_achievements_section()

    render_master_cv_section()

    render_target_companies_section()

    render_elevator_pitch_section()

    render_star_story_section()

    render_interview_preparation_section()

    render_complete_interview_pack_section()

    render_application_tracker_integration_section()

    render_career_dashboard_section()

    render_career_polishing_section()
