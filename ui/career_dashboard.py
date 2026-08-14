from __future__ import annotations

import streamlit as st

from services.career_dashboard_service import (
    build_career_dashboard_snapshot,
)


def _verified_label(
    verified: int,
    total: int,
) -> str:
    return (
        f"{verified}/{total}"
    )


def render_career_dashboard_section() -> None:
    st.divider()

    st.subheader(
        "Career Dashboard / Karriere-Dashboard"
    )

    st.caption(
        "One-screen readiness overview for your verified career data, "
        "target companies, applications, CV preparation and interview preparation."
    )

    snapshot = (
        build_career_dashboard_snapshot()
    )

    st.markdown(
        "### Overall Career Preparation / Gesamtfortschritt"
    )

    st.progress(
        snapshot.overall_progress
        / 100
    )

    st.write(
        f"**{snapshot.overall_progress}% complete**"
    )

    st.caption(
        "This percentage measures Career Agent workflow completion, "
        "not your probability of receiving a job offer."
    )

    metric1, metric2, metric3, metric4 = (
        st.columns(4)
    )

    with metric1:
        st.metric(
            "Profile Complete",
            f"{snapshot.profile_completeness}%",
        )

    with metric2:
        st.metric(
            "Target Companies",
            snapshot.target_companies_total,
        )

    with metric3:
        st.metric(
            "Applications",
            snapshot.applications_total,
        )

    with metric4:
        st.metric(
            "Interview Ready",
            snapshot.interview_ready,
        )

    st.markdown(
        "### Verified Career Evidence / Verifizierte Karrieredaten"
    )

    evidence1, evidence2, evidence3 = (
        st.columns(3)
    )

    with evidence1:
        st.metric(
            "Work Experience",
            _verified_label(
                snapshot.work_experience_verified,
                snapshot.work_experience_total,
            ),
        )

        st.metric(
            "Education",
            _verified_label(
                snapshot.education_verified,
                snapshot.education_total,
            ),
        )

    with evidence2:
        st.metric(
            "Projects",
            _verified_label(
                snapshot.projects_verified,
                snapshot.projects_total,
            ),
        )

        st.metric(
            "Achievements",
            _verified_label(
                snapshot.achievements_verified,
                snapshot.achievements_total,
            ),
        )

    with evidence3:
        st.metric(
            "STAR Stories",
            _verified_label(
                snapshot.star_stories_verified,
                snapshot.star_stories_total,
            ),
        )

        st.metric(
            "Dream Companies",
            snapshot.dream_companies_total,
        )

    st.markdown(
        "### Application Readiness / Bewerbungsbereitschaft"
    )

    readiness1, readiness2, readiness3 = (
        st.columns(3)
    )

    with readiness1:
        st.metric(
            "Active Applications",
            snapshot.active_applications,
        )

    with readiness2:
        st.metric(
            "Tailored CV Ready",
            snapshot.tailored_cv_ready,
        )

    with readiness3:
        st.metric(
            "Interview Pack Ready",
            snapshot.interview_pack_ready,
        )

    st.markdown(
        "### Next Actions / Nächste Schritte"
    )

    if snapshot.next_actions:
        for index, action in enumerate(
            snapshot.next_actions,
            start=1,
        ):
            st.write(
                f"**{index}.** {action}"
            )

    else:
        st.success(
            "No immediate Career Agent preparation actions are pending."
        )

    if snapshot.application_rows:
        st.markdown(
            "### Application Preparation Pipeline"
        )

        st.dataframe(
            snapshot.application_rows,
            use_container_width=True,
            hide_index=True,
        )
