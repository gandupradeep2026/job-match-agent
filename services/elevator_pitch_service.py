from __future__ import annotations

from career.achievement_database import (
    get_achievement_records,
)
from career.database import (
    load_profile,
)
from career.education_database import (
    get_education_records,
)
from career.elevator_pitch import (
    ElevatorPitchRequest,
    ElevatorPitchResult,
)
from career.project_database import (
    get_project_records,
)
from career.work_experience_database import (
    get_work_experiences,
)


def _first_verified(items):
    for item in items:
        if item.verified:
            return item

    return None


def _verified(items):
    return [
        item
        for item in items
        if item.verified
    ]


def _top_skills(
    skills: list[str],
    limit: int,
) -> list[str]:
    result = []
    seen = set()

    for value in skills or []:
        item = str(value).strip()

        if not item:
            continue

        key = item.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

        if len(result) >= limit:
            break

    return result


def _english_pitch(
    *,
    name: str,
    target_role: str,
    audience: str,
    duration: int,
    summary: str,
    skills: list[str],
    experience,
    education,
    project,
    achievement,
) -> tuple[str, int]:
    parts = []
    evidence_count = 0

    if name:
        intro = (
            f"Hi, I'm {name}."
        )
    else:
        intro = "Hello."

    if target_role:
        intro += (
            f" I'm currently targeting full-time "
            f"{target_role} opportunities."
        )

    parts.append(intro)

    if duration >= 60 and summary:
        parts.append(
            summary
        )
        evidence_count += 1

    if experience is not None:
        title = (
            experience.job_title_en
            or experience.job_title_de
        ).strip()

        employer = (
            experience.employer
            or ""
        ).strip()

        if title and employer:
            parts.append(
                f"My professional background includes experience "
                f"as {title} with {employer}."
            )
        elif employer:
            parts.append(
                f"My professional background includes experience "
                f"with {employer}."
            )

        evidence_count += 1

    if education is not None:
        degree = (
            education.degree_en
            or education.degree_de
        ).strip()

        field = (
            education.field_of_study_en
            or education.field_of_study_de
        ).strip()

        institution = (
            education.institution
            or ""
        ).strip()

        education_bits = [
            value
            for value in [
                degree,
                field,
            ]
            if value
        ]

        if education_bits and institution:
            parts.append(
                "My academic background includes "
                + " in ".join(education_bits)
                + f" at {institution}."
            )
        elif institution:
            parts.append(
                f"I also have an academic background at {institution}."
            )

        evidence_count += 1

    if skills:
        if len(skills) == 1:
            skill_text = skills[0]
        else:
            skill_text = (
                ", ".join(
                    skills[:-1]
                )
                + f" and {skills[-1]}"
            )

        if audience == "Technical Manager":
            parts.append(
                f"My strongest technical areas include {skill_text}."
            )
        else:
            parts.append(
                f"My key strengths include {skill_text}."
            )

        evidence_count += len(skills)

    if duration >= 60 and project is not None:
        project_name = (
            project.name_en
            or project.name_de
        ).strip()

        technologies = _top_skills(
            project.technologies,
            4,
        )

        if project_name:
            if technologies:
                parts.append(
                    f"I've also applied these skills in the verified "
                    f"project '{project_name}', working with "
                    + ", ".join(technologies)
                    + "."
                )
            else:
                parts.append(
                    f"I've also applied my skills in the verified "
                    f"project '{project_name}'."
                )

        evidence_count += 1

    if duration >= 90 and achievement is not None:
        title = (
            achievement.title_en
            or achievement.title_de
        ).strip()

        metric = (
            achievement.metric_value
            or ""
        ).strip()

        if title:
            if metric:
                parts.append(
                    f"One result I'm particularly proud of is "
                    f"{title}, with a measured result of {metric}."
                )
            else:
                parts.append(
                    f"One result I'm particularly proud of is {title}."
                )

        evidence_count += 1

    if target_role:
        if audience == "Recruiter":
            ending = (
                f"I'm looking for a role where I can contribute these "
                f"skills while continuing to grow as a {target_role}."
            )
        elif audience == "Hiring Manager":
            ending = (
                f"I'm interested in bringing this combination of "
                f"experience, technical learning and project work to "
                f"a {target_role} team where I can contribute from day one."
            )
        elif audience == "Technical Manager":
            ending = (
                f"I'm now looking to apply this foundation in a "
                f"{target_role} position focused on reliable, practical "
                f"and scalable technical solutions."
            )
        else:
            ending = (
                f"I'm currently exploring {target_role} opportunities "
                f"and would be glad to connect with teams working in this area."
            )
    else:
        ending = (
            "I'm now looking for a full-time opportunity where I can "
            "apply my experience and continue developing professionally."
        )

    parts.append(
        ending
    )

    text = " ".join(
        part.strip()
        for part in parts
        if part.strip()
    )

    return text, evidence_count


def _german_pitch(
    *,
    name: str,
    target_role: str,
    audience: str,
    duration: int,
    summary: str,
    skills: list[str],
    experience,
    education,
    project,
    achievement,
) -> tuple[str, int]:
    parts = []
    evidence_count = 0

    if name:
        intro = (
            f"Hallo, ich bin {name}."
        )
    else:
        intro = "Guten Tag."

    if target_role:
        intro += (
            f" Aktuell suche ich eine Vollzeitposition "
            f"im Bereich {target_role}."
        )

    parts.append(intro)

    if duration >= 60 and summary:
        parts.append(
            summary
        )
        evidence_count += 1

    if experience is not None:
        title = (
            experience.job_title_de
            or experience.job_title_en
        ).strip()

        employer = (
            experience.employer
            or ""
        ).strip()

        if title and employer:
            parts.append(
                f"Zu meinem beruflichen Hintergrund gehört die "
                f"Tätigkeit als {title} bei {employer}."
            )
        elif employer:
            parts.append(
                f"Ich bringe Berufserfahrung bei {employer} mit."
            )

        evidence_count += 1

    if education is not None:
        degree = (
            education.degree_de
            or education.degree_en
        ).strip()

        field = (
            education.field_of_study_de
            or education.field_of_study_en
        ).strip()

        institution = (
            education.institution
            or ""
        ).strip()

        if degree and field and institution:
            parts.append(
                f"Akademisch verfüge ich über einen Hintergrund "
                f"mit {degree} im Bereich {field} an der {institution}."
            )
        elif degree and institution:
            parts.append(
                f"Akademisch gehört ein {degree} an der "
                f"{institution} zu meinem Profil."
            )
        elif institution:
            parts.append(
                f"Zu meinem akademischen Hintergrund gehört die "
                f"{institution}."
            )

        evidence_count += 1

    if skills:
        if len(skills) == 1:
            skill_text = skills[0]
        else:
            skill_text = (
                ", ".join(
                    skills[:-1]
                )
                + f" und {skills[-1]}"
            )

        if audience == "Technical Manager":
            parts.append(
                f"Meine wichtigsten technischen Schwerpunkte sind "
                f"{skill_text}."
            )
        else:
            parts.append(
                f"Zu meinen relevanten Stärken zählen {skill_text}."
            )

        evidence_count += len(skills)

    if duration >= 60 and project is not None:
        project_name = (
            project.name_de
            or project.name_en
        ).strip()

        technologies = _top_skills(
            project.technologies,
            4,
        )

        if project_name:
            if technologies:
                parts.append(
                    f"Diese Kenntnisse habe ich auch im verifizierten "
                    f"Projekt „{project_name}“ praktisch eingesetzt, "
                    f"unter anderem mit "
                    + ", ".join(technologies)
                    + "."
                )
            else:
                parts.append(
                    f"Diese Kenntnisse habe ich auch im verifizierten "
                    f"Projekt „{project_name}“ praktisch eingesetzt."
                )

        evidence_count += 1

    if duration >= 90 and achievement is not None:
        title = (
            achievement.title_de
            or achievement.title_en
        ).strip()

        metric = (
            achievement.metric_value
            or ""
        ).strip()

        if title:
            if metric:
                parts.append(
                    f"Ein konkretes Ergebnis, auf das ich besonders "
                    f"stolz bin, ist {title} mit einem messbaren "
                    f"Ergebnis von {metric}."
                )
            else:
                parts.append(
                    f"Ein konkretes Ergebnis, auf das ich besonders "
                    f"stolz bin, ist {title}."
                )

        evidence_count += 1

    if target_role:
        if audience == "Recruiter":
            ending = (
                f"Ich suche eine Position, in der ich diese Kenntnisse "
                f"einbringen und mich gleichzeitig als {target_role} "
                f"weiterentwickeln kann."
            )
        elif audience == "Hiring Manager":
            ending = (
                f"Ich möchte diese Kombination aus Berufserfahrung, "
                f"technischer Entwicklung und Projektpraxis in ein "
                f"{target_role}-Team einbringen und dort aktiv Mehrwert schaffen."
            )
        elif audience == "Technical Manager":
            ending = (
                f"Nun möchte ich diese Grundlage in einer "
                f"{target_role}-Position einsetzen und an zuverlässigen, "
                f"praxisnahen und skalierbaren technischen Lösungen arbeiten."
            )
        else:
            ending = (
                f"Aktuell interessiere ich mich für Möglichkeiten im "
                f"Bereich {target_role} und freue mich auf den Austausch "
                f"mit passenden Teams."
            )
    else:
        ending = (
            "Ich suche nun eine Vollzeitposition, in der ich meine "
            "Erfahrung einbringen und mich fachlich weiterentwickeln kann."
        )

    parts.append(
        ending
    )

    text = " ".join(
        part.strip()
        for part in parts
        if part.strip()
    )

    return text, evidence_count


def generate_personal_elevator_pitch(
    request: ElevatorPitchRequest,
) -> ElevatorPitchResult:
    """
    Create a personal elevator pitch using verified career data only.

    This first version is deterministic and intentionally does not ask
    an LLM to invent or infer missing facts.
    """

    if request.language not in (
        "English",
        "Deutsch",
    ):
        raise ValueError(
            "language must be English or Deutsch"
        )

    if request.duration_seconds not in (
        30,
        60,
        90,
    ):
        raise ValueError(
            "duration_seconds must be 30, 60 or 90"
        )

    profile = load_profile()

    warnings = []

    if not profile.verified:
        warnings.append(
            "Master Career Profile is not verified. "
            "Verify it before using this pitch in a real interview."
            if request.language == "English"
            else (
                "Das Master-Karriereprofil ist noch nicht verifiziert. "
                "Bitte vor einem echten Interview verifizieren."
            )
        )

    experiences = _verified(
        get_work_experiences()
    )

    education_records = _verified(
        get_education_records()
    )

    projects = _verified(
        get_project_records()
    )

    achievements = _verified(
        get_achievement_records()
    )

    experience = _first_verified(
        experiences
    )

    education = _first_verified(
        education_records
    )

    project = _first_verified(
        projects
    )

    achievement = _first_verified(
        achievements
    )

    if request.language == "English":
        summary = (
            profile.professional_summary_en
            or ""
        ).strip()
    else:
        summary = (
            profile.professional_summary_de
            or ""
        ).strip()

    skill_limit = {
        30: 3,
        60: 5,
        90: 6,
    }[
        request.duration_seconds
    ]

    skills = _top_skills(
        profile.technical_skills,
        skill_limit,
    )

    common = dict(
        name=profile.full_name.strip(),
        target_role=request.target_role.strip(),
        audience=request.audience,
        duration=request.duration_seconds,
        summary=summary,
        skills=skills,
        experience=experience,
        education=education,
        project=project,
        achievement=achievement,
    )

    if request.language == "English":
        text, evidence_count = (
            _english_pitch(
                **common
            )
        )
    else:
        text, evidence_count = (
            _german_pitch(
                **common
            )
        )

    if not text.strip():
        warnings.append(
            "Not enough verified career data is available to build a pitch."
            if request.language == "English"
            else (
                "Es stehen nicht genügend verifizierte Karrieredaten "
                "für einen Pitch zur Verfügung."
            )
        )

    return ElevatorPitchResult(
        language=request.language,
        duration_seconds=(
            request.duration_seconds
        ),
        audience=request.audience,
        target_role=request.target_role,
        text=text,
        warnings=warnings,
        evidence_count=evidence_count,
    )
