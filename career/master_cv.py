from __future__ import annotations

from dataclasses import dataclass, field

from career.achievement import AchievementRecord
from career.education import EducationRecord
from career.models import CareerProfile
from career.project import ProjectRecord
from career.work_experience import WorkExperience


@dataclass
class MasterCVData:
    language: str

    candidate_name: str = ""
    professional_title: str = ""

    contact_details: list[str] = field(
        default_factory=list
    )

    professional_summary: str = ""

    technical_skills: list[str] = field(
        default_factory=list
    )

    experiences: list[str] = field(
        default_factory=list
    )

    projects: list[str] = field(
        default_factory=list
    )

    education: list[str] = field(
        default_factory=list
    )

    achievements: list[str] = field(
        default_factory=list
    )

    certifications: list[str] = field(
        default_factory=list
    )

    languages: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )


def _clean(values: list[str]) -> list[str]:
    result = []
    seen = set()

    for value in values or []:
        item = str(value).strip()

        if not item:
            continue

        key = item.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def _date_range(
    start_date: str,
    end_date: str,
    is_current: bool,
    language: str,
) -> str:
    start = (
        start_date
        or ""
    ).strip()

    if is_current:
        end = (
            "Present"
            if language == "English"
            else "Heute"
        )
    else:
        end = (
            end_date
            or ""
        ).strip()

    if start and end:
        return (
            f"{start} - {end}"
        )

    return start or end


def _format_experience(
    record: WorkExperience,
    language: str,
) -> str:
    if language == "English":
        title = (
            record.job_title_en
            or record.job_title_de
        ).strip()

        description = (
            record.description_en
            or ""
        ).strip()

        achievements = (
            record.achievements_en
            or []
        )

    else:
        title = (
            record.job_title_de
            or record.job_title_en
        ).strip()

        description = (
            record.description_de
            or ""
        ).strip()

        achievements = (
            record.achievements_de
            or []
        )

    lines = [
        " | ".join(
            item
            for item in [
                title,
                record.employer.strip(),
            ]
            if item
        )
    ]

    meta = " | ".join(
        item
        for item in [
            record.location.strip(),
            record.country.strip(),
            _date_range(
                record.start_date,
                record.end_date,
                record.is_current,
                language,
            ),
            record.employment_type.strip(),
        ]
        if item
    )

    if meta:
        lines.append(meta)

    if description:
        lines.append(
            description
        )

    for item in achievements:
        cleaned = item.strip()

        if cleaned:
            lines.append(
                f"- {cleaned}"
            )

    if record.technologies:
        label = (
            "Technologies"
            if language == "English"
            else "Technologien"
        )

        lines.append(
            f"{label}: "
            + ", ".join(
                _clean(
                    record.technologies
                )
            )
        )

    return "\n".join(
        line
        for line in lines
        if line.strip()
    )


def _format_project(
    record: ProjectRecord,
    language: str,
) -> str:
    if language == "English":
        name = (
            record.name_en
            or record.name_de
        ).strip()

        role = (
            record.role_en
            or record.role_de
        ).strip()

        description = (
            record.description_en
            or ""
        ).strip()

        responsibilities = (
            record.responsibilities_en
            or []
        )

        achievements = (
            record.achievements_en
            or []
        )

    else:
        name = (
            record.name_de
            or record.name_en
        ).strip()

        role = (
            record.role_de
            or record.role_en
        ).strip()

        description = (
            record.description_de
            or ""
        ).strip()

        responsibilities = (
            record.responsibilities_de
            or []
        )

        achievements = (
            record.achievements_de
            or []
        )

    lines = [
        name
    ]

    meta = " | ".join(
        item
        for item in [
            record.project_type.strip(),
            role,
            _date_range(
                record.start_date,
                record.end_date,
                record.is_current,
                language,
            ),
        ]
        if item
    )

    if meta:
        lines.append(
            meta
        )

    if description:
        lines.append(
            description
        )

    for item in responsibilities:
        cleaned = item.strip()

        if cleaned:
            lines.append(
                f"- {cleaned}"
            )

    for item in achievements:
        cleaned = item.strip()

        if cleaned:
            lines.append(
                f"- {cleaned}"
            )

    if record.technologies:
        label = (
            "Technologies"
            if language == "English"
            else "Technologien"
        )

        lines.append(
            f"{label}: "
            + ", ".join(
                _clean(
                    record.technologies
                )
            )
        )

    if record.repository_url.strip():
        lines.append(
            "Repository: "
            + record.repository_url.strip()
        )

    return "\n".join(
        line
        for line in lines
        if line.strip()
    )


def _format_education(
    record: EducationRecord,
    language: str,
) -> str:
    if language == "English":
        degree = (
            record.degree_en
            or record.degree_de
        ).strip()

        field_name = (
            record.field_of_study_en
            or record.field_of_study_de
        ).strip()

        thesis = (
            record.thesis_title_en
            or ""
        ).strip()

        description = (
            record.description_en
            or ""
        ).strip()

        highlights = (
            record.achievements_en
            or []
        )

        thesis_label = "Thesis"

    else:
        degree = (
            record.degree_de
            or record.degree_en
        ).strip()

        field_name = (
            record.field_of_study_de
            or record.field_of_study_en
        ).strip()

        thesis = (
            record.thesis_title_de
            or ""
        ).strip()

        description = (
            record.description_de
            or ""
        ).strip()

        highlights = (
            record.achievements_de
            or []
        )

        thesis_label = (
            "Abschlussarbeit"
        )

    lines = [
        " | ".join(
            item
            for item in [
                degree,
                field_name,
            ]
            if item
        )
    ]

    meta = " | ".join(
        item
        for item in [
            record.institution.strip(),
            record.location.strip(),
            record.country.strip(),
            _date_range(
                record.start_date,
                record.end_date,
                record.is_current,
                language,
            ),
        ]
        if item
    )

    if meta:
        lines.append(
            meta
        )

    if record.grade.strip():
        grade_label = (
            "Grade"
            if language == "English"
            else "Note"
        )

        lines.append(
            f"{grade_label}: "
            + record.grade.strip()
        )

    if thesis:
        lines.append(
            f"{thesis_label}: {thesis}"
        )

    if description:
        lines.append(
            description
        )

    for item in highlights:
        cleaned = item.strip()

        if cleaned:
            lines.append(
                f"- {cleaned}"
            )

    return "\n".join(
        line
        for line in lines
        if line.strip()
    )


def _format_achievement(
    record: AchievementRecord,
    language: str,
) -> str:
    if language == "English":
        title = (
            record.title_en
            or record.title_de
        ).strip()

        description = (
            record.description_en
            or ""
        ).strip()

        result = (
            record.result_en
            or ""
        ).strip()

        result_label = "Result"

    else:
        title = (
            record.title_de
            or record.title_en
        ).strip()

        description = (
            record.description_de
            or ""
        ).strip()

        result = (
            record.result_de
            or ""
        ).strip()

        result_label = "Ergebnis"

    lines = [
        title
    ]

    meta = " | ".join(
        item
        for item in [
            record.category.strip(),
            record.source_name.strip(),
            record.achievement_date.strip(),
        ]
        if item
    )

    if meta:
        lines.append(
            meta
        )

    if description:
        lines.append(
            description
        )

    if result:
        lines.append(
            f"{result_label}: {result}"
        )

    if record.metric_value.strip():
        lines.append(
            record.metric_value.strip()
        )

    return "\n".join(
        line
        for line in lines
        if line.strip()
    )


def build_master_cv_data(
    *,
    profile: CareerProfile,
    experiences: list[WorkExperience],
    education_records: list[EducationRecord],
    projects: list[ProjectRecord],
    achievements: list[AchievementRecord],
    language: str,
) -> MasterCVData:
    """
    Build one English or German Master CV.

    Truth Lock rule:
    - the profile itself must be verified;
    - only individually verified structured records are included.
    """

    if language not in (
        "English",
        "Deutsch",
    ):
        raise ValueError(
            "language must be English or Deutsch"
        )

    warnings = []

    if not profile.verified:
        warnings.append(
            "Master Career Profile is not verified."
            if language == "English"
            else (
                "Das Master-Karriereprofil ist "
                "noch nicht verifiziert."
            )
        )

    verified_experiences = [
        item
        for item in experiences
        if item.verified
    ]

    verified_education = [
        item
        for item in education_records
        if item.verified
    ]

    verified_projects = [
        item
        for item in projects
        if item.verified
    ]

    verified_achievements = [
        item
        for item in achievements
        if item.verified
    ]

    if language == "English":
        summary = (
            profile.professional_summary_en
            or ""
        ).strip()
    else:
        summary = (
            profile.professional_summary_de
            or ""
        ).strip()

    professional_title = (
        profile.target_roles[0].strip()
        if profile.target_roles
        else ""
    )

    contact_details = _clean(
        [
            profile.email,
            profile.phone,
            profile.city,
            profile.country,
            profile.linkedin_url,
            profile.github_url,
        ]
    )

    if not verified_experiences:
        warnings.append(
            "No verified work experience records."
            if language == "English"
            else (
                "Keine verifizierten "
                "Berufserfahrungen vorhanden."
            )
        )

    if not verified_education:
        warnings.append(
            "No verified education records."
            if language == "English"
            else (
                "Keine verifizierten "
                "Ausbildungs- oder Studienangaben vorhanden."
            )
        )

    return MasterCVData(
        language=language,
        candidate_name=(
            profile.full_name.strip()
        ),
        professional_title=(
            professional_title
        ),
        contact_details=(
            contact_details
        ),
        professional_summary=(
            summary
        ),
        technical_skills=_clean(
            profile.technical_skills
        ),
        experiences=[
            _format_experience(
                item,
                language,
            )
            for item in verified_experiences
        ],
        projects=[
            _format_project(
                item,
                language,
            )
            for item in verified_projects
        ],
        education=[
            _format_education(
                item,
                language,
            )
            for item in verified_education
        ],
        achievements=[
            _format_achievement(
                item,
                language,
            )
            for item in verified_achievements
        ],
        certifications=_clean(
            profile.certifications
        ),
        languages=_clean(
            profile.languages
        ),
        warnings=warnings,
    )
