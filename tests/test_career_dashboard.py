from career.dashboard import (
    CareerDashboardSnapshot,
)
from career.models import (
    CareerProfile,
)
from career.work_experience import (
    WorkExperience,
)
from career.education import (
    EducationRecord,
)
from career.project import (
    ProjectRecord,
)
from career.achievement import (
    AchievementRecord,
)
from career.star_story import (
    StarStory,
)
from career.target_company import (
    TargetCompany,
)
import services.career_dashboard_service as service


def _patch_all(
    monkeypatch,
    *,
    profile_verified=True,
):
    monkeypatch.setattr(
        service,
        "load_profile",
        lambda: CareerProfile(
            full_name="Test Candidate",
            email="test@example.com",
            city="Berlin",
            country="Germany",
            professional_summary_en=(
                "English summary"
            ),
            professional_summary_de=(
                "Deutsche Zusammenfassung"
            ),
            target_roles=[
                "Data Engineer",
            ],
            technical_skills=[
                "Python",
            ],
            languages=[
                "English",
                "German",
            ],
            github_url=(
                "https://github.com/example"
            ),
            verified=(
                profile_verified
            ),
        ),
    )

    monkeypatch.setattr(
        service,
        "get_work_experiences",
        lambda: [
            WorkExperience(
                employer="Example GmbH",
                job_title_en="Data Engineer",
                start_date="2025-01",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_education_records",
        lambda: [
            EducationRecord(
                institution="Example University",
                degree_en="MSc",
                start_date="2023-01",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_project_records",
        lambda: [
            ProjectRecord(
                name_en="Cloud Project",
                start_date="2026-01",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_achievement_records",
        lambda: [
            AchievementRecord(
                title_en="Improved pipeline",
                achievement_date="2026-01",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_star_stories",
        lambda: [
            StarStory(
                title_en="Solved issue",
                situation_en="S",
                task_en="T",
                action_en="A",
                result_en="R",
                verified=True,
            )
        ],
    )

    monkeypatch.setattr(
        service,
        "get_target_companies",
        lambda: [
            TargetCompany(
                id=1,
                company_name="Dream GmbH",
                priority="A — Dream Company",
            ),
        ],
    )

    monkeypatch.setattr(
        service,
        "get_career_application_overview",
        lambda: [
            {
                "application_id": 1,
                "company": "Dream GmbH",
                "job_title": "Data Engineer",
                "application_status": "Interview",
                "target_company": "Dream GmbH",
                "career_target_role": "Data Engineer",
                "preparation_stage": "Interview Ready",
                "tailored_cv_ready": True,
                "interview_pack_ready": True,
                "career_next_action": "Practice STAR stories",
            }
        ],
    )


def test_profile_completeness_can_reach_100(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert (
        snapshot.profile_completeness
        == 100
    )


def test_verified_counts(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert (
        snapshot.work_experience_verified
        == 1
    )

    assert (
        snapshot.projects_verified
        == 1
    )

    assert (
        snapshot.star_stories_verified
        == 1
    )


def test_application_readiness_metrics(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert (
        snapshot.applications_total
        == 1
    )

    assert (
        snapshot.tailored_cv_ready
        == 1
    )

    assert (
        snapshot.interview_pack_ready
        == 1
    )

    assert (
        snapshot.interview_ready
        == 1
    )


def test_dream_company_count(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert (
        snapshot.dream_companies_total
        == 1
    )


def test_unverified_profile_creates_action(
    monkeypatch,
):
    _patch_all(
        monkeypatch,
        profile_verified=False,
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert any(
        "Verify the Master Career Profile"
        in action
        for action in (
            snapshot.next_actions
        )
    )


def test_missing_star_stories_creates_action(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    monkeypatch.setattr(
        service,
        "get_star_stories",
        lambda: [],
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert any(
        "STAR stories"
        in action
        for action in (
            snapshot.next_actions
        )
    )


def test_missing_cv_creates_application_action(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    monkeypatch.setattr(
        service,
        "get_career_application_overview",
        lambda: [
            {
                "application_id": 1,
                "company": "Example GmbH",
                "job_title": "Data Engineer",
                "application_status": "Applied",
                "target_company": "",
                "career_target_role": "Data Engineer",
                "preparation_stage": "Applied",
                "tailored_cv_ready": False,
                "interview_pack_ready": False,
                "career_next_action": "",
            }
        ],
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert any(
        "Prepare the tailored CV"
        in action
        for action in (
            snapshot.next_actions
        )
    )


def test_interview_without_pack_creates_action(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    monkeypatch.setattr(
        service,
        "get_career_application_overview",
        lambda: [
            {
                "application_id": 1,
                "company": "Example GmbH",
                "job_title": "Data Engineer",
                "application_status": "Interview",
                "target_company": "",
                "career_target_role": "Data Engineer",
                "preparation_stage": "Interview Prep",
                "tailored_cv_ready": True,
                "interview_pack_ready": False,
                "career_next_action": "",
            }
        ],
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert any(
        "Prepare the interview pack"
        in action
        for action in (
            snapshot.next_actions
        )
    )


def test_overall_progress_is_bounded(
    monkeypatch,
):
    _patch_all(
        monkeypatch
    )

    snapshot = (
        service
        .build_career_dashboard_snapshot()
    )

    assert (
        0
        <= snapshot.overall_progress
        <= 100
    )
