from __future__ import annotations

from career.achievement_database import (
    get_achievement_records,
)
from career.application_tracker_service import (
    get_career_application_overview,
)
from career.dashboard import (
    CareerDashboardSnapshot,
)
from career.database import (
    load_profile,
)
from career.education_database import (
    get_education_records,
)
from career.project_database import (
    get_project_records,
)
from career.star_story_database import (
    get_star_stories,
)
from career.target_company_database import (
    get_target_companies,
)
from career.work_experience_database import (
    get_work_experiences,
)


CLOSED_APPLICATION_STATUSES = {
    "Offer",
    "Rejected",
    "Withdrawn",
}


def _count_verified(
    records,
) -> int:
    return sum(
        1
        for item in records
        if item.verified
    )


def _profile_completeness(
    profile,
) -> int:
    checks = [
        bool(
            profile.full_name.strip()
        ),
        bool(
            profile.email.strip()
        ),
        bool(
            profile.city.strip()
            or profile.country.strip()
        ),
        bool(
            profile.professional_summary_en.strip()
        ),
        bool(
            profile.professional_summary_de.strip()
        ),
        bool(
            profile.target_roles
        ),
        bool(
            profile.technical_skills
        ),
        bool(
            profile.languages
        ),
        bool(
            profile.linkedin_url.strip()
            or profile.github_url.strip()
        ),
        bool(
            profile.verified
        ),
    ]

    return round(
        100
        * sum(
            checks
        )
        / len(
            checks
        )
    )


def _ratio_score(
    verified: int,
    total: int,
) -> float:
    if total <= 0:
        return 0.0

    return min(
        1.0,
        verified
        / total,
    )


def _overall_progress(
    *,
    profile_completeness: int,
    profile_verified: bool,
    work_verified: int,
    education_verified: int,
    projects_verified: int,
    achievements_verified: int,
    star_verified: int,
    target_companies_total: int,
    applications_total: int,
    tailored_cv_ready: int,
    interview_pack_ready: int,
) -> int:
    """
    Weighted readiness score for the Career Agent workflow.

    This is not a hiring probability. It measures completion of the
    preparation workflow only.
    """

    score = 0.0

    score += (
        profile_completeness
        / 100
    ) * 18

    score += (
        7
        if profile_verified
        else 0
    )

    score += min(
        work_verified,
        3,
    ) / 3 * 10

    score += min(
        education_verified,
        2,
    ) / 2 * 7

    score += min(
        projects_verified,
        3,
    ) / 3 * 10

    score += min(
        achievements_verified,
        3,
    ) / 3 * 7

    score += min(
        star_verified,
        5,
    ) / 5 * 12

    score += min(
        target_companies_total,
        10,
    ) / 10 * 8

    if applications_total > 0:
        score += min(
            tailored_cv_ready
            / applications_total,
            1.0,
        ) * 10

        score += min(
            interview_pack_ready
            / applications_total,
            1.0,
        ) * 11

    return min(
        100,
        round(
            score
        ),
    )


def _build_next_actions(
    *,
    profile,
    work_verified: int,
    education_verified: int,
    projects_verified: int,
    achievements_verified: int,
    star_verified: int,
    target_companies_total: int,
    application_rows: list[dict],
) -> list[str]:
    actions = []

    if not profile.verified:
        actions.append(
            "Verify the Master Career Profile before using generated materials."
        )

    if work_verified <= 0:
        actions.append(
            "Add and verify at least one Work Experience record."
        )

    if education_verified <= 0:
        actions.append(
            "Add and verify your Education / Study record."
        )

    if projects_verified <= 0:
        actions.append(
            "Add and verify at least one technical or academic project."
        )

    if achievements_verified <= 0:
        actions.append(
            "Add at least one verified achievement with a concrete result."
        )

    if star_verified < 3:
        actions.append(
            "Build at least three verified STAR stories covering different competencies."
        )

    if target_companies_total < 5:
        actions.append(
            "Build a focused target-company list with at least five companies."
        )

    for application in application_rows:
        label = (
            f"{application.get('company', '')} — "
            f"{application.get('job_title', '')}"
        ).strip(
            " —"
        )

        if not application.get(
            "tailored_cv_ready"
        ):
            actions.append(
                f"Prepare the tailored CV for {label}."
            )

        status = (
            application.get(
                "application_status"
            )
            or ""
        )

        if (
            status
            in {
                "Interview",
                "Second Interview",
                "Assessment",
            }
            and not application.get(
                "interview_pack_ready"
            )
        ):
            actions.append(
                f"Prepare the interview pack for {label}."
            )

        next_action = (
            application.get(
                "career_next_action"
            )
            or ""
        ).strip()

        if next_action:
            actions.append(
                f"{label}: {next_action}"
            )

    deduped = []
    seen = set()

    for action in actions:
        key = (
            action.casefold()
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        deduped.append(
            action
        )

    return deduped[:12]


def build_career_dashboard_snapshot() -> CareerDashboardSnapshot:
    profile = load_profile()

    work = (
        get_work_experiences()
    )

    education = (
        get_education_records()
    )

    projects = (
        get_project_records()
    )

    achievements = (
        get_achievement_records()
    )

    star_stories = (
        get_star_stories()
    )

    target_companies = (
        get_target_companies()
    )

    application_rows = (
        get_career_application_overview()
    )

    work_verified = (
        _count_verified(
            work
        )
    )

    education_verified = (
        _count_verified(
            education
        )
    )

    projects_verified = (
        _count_verified(
            projects
        )
    )

    achievements_verified = (
        _count_verified(
            achievements
        )
    )

    star_verified = (
        _count_verified(
            star_stories
        )
    )

    dream_companies = sum(
        1
        for item in target_companies
        if item.priority
        == "A — Dream Company"
    )

    active_applications = sum(
        1
        for item in application_rows
        if (
            item.get(
                "application_status"
            )
            not in CLOSED_APPLICATION_STATUSES
        )
    )

    tailored_cv_ready = sum(
        1
        for item in application_rows
        if item.get(
            "tailored_cv_ready"
        )
    )

    interview_pack_ready = sum(
        1
        for item in application_rows
        if item.get(
            "interview_pack_ready"
        )
    )

    interview_ready = sum(
        1
        for item in application_rows
        if (
            item.get(
                "interview_pack_ready"
            )
            and item.get(
                "preparation_stage"
            )
            in {
                "Interview Prep",
                "Interview Ready",
            }
        )
    )

    completeness = (
        _profile_completeness(
            profile
        )
    )

    overall = (
        _overall_progress(
            profile_completeness=(
                completeness
            ),
            profile_verified=(
                profile.verified
            ),
            work_verified=(
                work_verified
            ),
            education_verified=(
                education_verified
            ),
            projects_verified=(
                projects_verified
            ),
            achievements_verified=(
                achievements_verified
            ),
            star_verified=(
                star_verified
            ),
            target_companies_total=(
                len(
                    target_companies
                )
            ),
            applications_total=(
                len(
                    application_rows
                )
            ),
            tailored_cv_ready=(
                tailored_cv_ready
            ),
            interview_pack_ready=(
                interview_pack_ready
            ),
        )
    )

    next_actions = (
        _build_next_actions(
            profile=profile,
            work_verified=(
                work_verified
            ),
            education_verified=(
                education_verified
            ),
            projects_verified=(
                projects_verified
            ),
            achievements_verified=(
                achievements_verified
            ),
            star_verified=(
                star_verified
            ),
            target_companies_total=(
                len(
                    target_companies
                )
            ),
            application_rows=(
                application_rows
            ),
        )
    )

    return CareerDashboardSnapshot(
        profile_verified=(
            profile.verified
        ),
        profile_completeness=(
            completeness
        ),
        work_experience_total=(
            len(
                work
            )
        ),
        work_experience_verified=(
            work_verified
        ),
        education_total=(
            len(
                education
            )
        ),
        education_verified=(
            education_verified
        ),
        projects_total=(
            len(
                projects
            )
        ),
        projects_verified=(
            projects_verified
        ),
        achievements_total=(
            len(
                achievements
            )
        ),
        achievements_verified=(
            achievements_verified
        ),
        star_stories_total=(
            len(
                star_stories
            )
        ),
        star_stories_verified=(
            star_verified
        ),
        target_companies_total=(
            len(
                target_companies
            )
        ),
        dream_companies_total=(
            dream_companies
        ),
        applications_total=(
            len(
                application_rows
            )
        ),
        active_applications=(
            active_applications
        ),
        tailored_cv_ready=(
            tailored_cv_ready
        ),
        interview_pack_ready=(
            interview_pack_ready
        ),
        interview_ready=(
            interview_ready
        ),
        overall_progress=(
            overall
        ),
        next_actions=(
            next_actions
        ),
        application_rows=(
            application_rows
        ),
    )
