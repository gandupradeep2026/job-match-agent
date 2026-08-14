from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CareerDashboardSnapshot:
    profile_verified: bool = False
    profile_completeness: int = 0

    work_experience_total: int = 0
    work_experience_verified: int = 0

    education_total: int = 0
    education_verified: int = 0

    projects_total: int = 0
    projects_verified: int = 0

    achievements_total: int = 0
    achievements_verified: int = 0

    star_stories_total: int = 0
    star_stories_verified: int = 0

    target_companies_total: int = 0
    dream_companies_total: int = 0

    applications_total: int = 0
    active_applications: int = 0
    tailored_cv_ready: int = 0
    interview_pack_ready: int = 0
    interview_ready: int = 0

    overall_progress: int = 0

    next_actions: list[str] = field(
        default_factory=list
    )

    application_rows: list[dict] = field(
        default_factory=list
    )
