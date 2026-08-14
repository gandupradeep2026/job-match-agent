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
)
from career.interview_preparation import (
    BehavioralAnswer,
    InterviewPreparationPack,
    InterviewPreparationRequest,
    PreparedAnswer,
)
from career.project_database import (
    get_project_records,
)
from career.star_story_database import (
    get_star_stories,
)
from career.target_company_database import (
    get_target_company,
)
from career.work_experience_database import (
    get_work_experiences,
)
from services.elevator_pitch_service import (
    generate_personal_elevator_pitch,
)


def _clean(
    values: list[str],
    limit: int | None = None,
) -> list[str]:
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

        if (
            limit is not None
            and len(result) >= limit
        ):
            break

    return result


def _verified(
    values,
):
    return [
        item
        for item in values
        if item.verified
    ]


def _join_natural(
    values: list[str],
    language: str,
) -> str:
    values = _clean(
        values
    )

    if not values:
        return ""

    if len(values) == 1:
        return values[0]

    conjunction = (
        "and"
        if language == "English"
        else "und"
    )

    return (
        ", ".join(
            values[:-1]
        )
        + f" {conjunction} "
        + values[-1]
    )


def _make_tell_me_about_yourself(
    request: InterviewPreparationRequest,
) -> PreparedAnswer:
    result = (
        generate_personal_elevator_pitch(
            ElevatorPitchRequest(
                language=request.language,
                duration_seconds=60,
                audience="Hiring Manager",
                target_role=request.target_role,
            )
        )
    )

    question = (
        "Tell me about yourself."
        if request.language == "English"
        else "Erzählen Sie mir etwas über sich."
    )

    return PreparedAnswer(
        question=question,
        answer=result.text,
        source_summary=(
            "Verified profile, work experience, education and projects"
            if request.language == "English"
            else (
                "Verifiziertes Profil, Berufserfahrung, "
                "Ausbildung und Projekte"
            )
        ),
        warnings=list(
            result.warnings
        ),
    )


def _make_why_role(
    request: InterviewPreparationRequest,
    profile,
    projects,
) -> PreparedAnswer:
    skills = _clean(
        profile.technical_skills,
        5,
    )

    verified_projects = _verified(
        projects
    )

    project = (
        verified_projects[0]
        if verified_projects
        else None
    )

    role = request.target_role.strip()

    if request.language == "English":
        question = (
            "Why are you interested in this role?"
        )

        parts = []

        if role:
            parts.append(
                f"I'm interested in the {role} role because it matches "
                f"the direction in which I want to develop my career."
            )

        if skills:
            parts.append(
                "My current technical foundation includes "
                + _join_natural(
                    skills,
                    "English",
                )
                + ", which are directly relevant to this type of work."
            )

        if project is not None:
            name = (
                project.name_en
                or project.name_de
            ).strip()

            if name:
                parts.append(
                    f"I have also applied these skills in the verified "
                    f"project '{name}', which strengthened my practical "
                    f"interest in this field."
                )

        parts.append(
            "I am looking for a position where I can contribute this "
            "foundation while continuing to deepen my technical expertise."
        )

    else:
        question = (
            "Warum interessieren Sie sich für diese Position?"
        )

        parts = []

        if role:
            parts.append(
                f"Die Position im Bereich {role} interessiert mich, "
                f"weil sie genau zu der Richtung passt, in der ich "
                f"mich beruflich weiterentwickeln möchte."
            )

        if skills:
            parts.append(
                "Zu meiner aktuellen technischen Grundlage gehören "
                + _join_natural(
                    skills,
                    "Deutsch",
                )
                + ", die für diese Art von Tätigkeit direkt relevant sind."
            )

        if project is not None:
            name = (
                project.name_de
                or project.name_en
            ).strip()

            if name:
                parts.append(
                    f"Diese Kenntnisse habe ich außerdem im verifizierten "
                    f"Projekt „{name}“ praktisch eingesetzt, wodurch sich "
                    f"mein Interesse an diesem Bereich weiter vertieft hat."
                )

        parts.append(
            "Ich suche eine Position, in der ich diese Grundlage "
            "einbringen und gleichzeitig meine technische Expertise "
            "systematisch weiterentwickeln kann."
        )

    return PreparedAnswer(
        question=question,
        answer=" ".join(
            part
            for part in parts
            if part.strip()
        ),
        source_summary=(
            "Verified target role, skills and project data"
            if request.language == "English"
            else (
                "Verifizierte Zielrolle, Kenntnisse und Projektdaten"
            )
        ),
    )


def _make_why_company(
    request: InterviewPreparationRequest,
) -> tuple[
    PreparedAnswer,
    str,
]:
    company = None

    if request.company_id is not None:
        company = get_target_company(
            request.company_id
        )

    if request.language == "English":
        question = (
            "Why do you want to work for this company?"
        )

        if company is None:
            return (
                PreparedAnswer(
                    question=question,
                    answer="",
                    warnings=[
                        "Select a saved target company to prepare this answer."
                    ],
                ),
                "",
            )

        company_reason = (
            company.why_company_en
            or ""
        ).strip()

        fit_reason = (
            company.why_fit_en
            or ""
        ).strip()

        parts = []

        if company_reason:
            parts.append(
                company_reason
            )

        if fit_reason:
            parts.append(
                fit_reason
            )

        warnings = []

        if not parts:
            warnings.append(
                "This target company does not yet contain verified "
                "'Why this company' or 'Why I fit' notes."
            )

        return (
            PreparedAnswer(
                question=question,
                answer=" ".join(
                    parts
                ),
                source_summary=(
                    "Saved target-company research"
                ),
                warnings=warnings,
            ),
            company.company_name,
        )

    question = (
        "Warum möchten Sie bei diesem Unternehmen arbeiten?"
    )

    if company is None:
        return (
            PreparedAnswer(
                question=question,
                answer="",
                warnings=[
                    "Bitte wählen Sie ein gespeichertes Zielunternehmen aus."
                ],
            ),
            "",
        )

    company_reason = (
        company.why_company_de
        or ""
    ).strip()

    fit_reason = (
        company.why_fit_de
        or ""
    ).strip()

    parts = []

    if company_reason:
        parts.append(
            company_reason
        )

    if fit_reason:
        parts.append(
            fit_reason
        )

    warnings = []

    if not parts:
        warnings.append(
            "Für dieses Zielunternehmen sind noch keine verifizierten "
            "Notizen zu 'Warum dieses Unternehmen' oder "
            "'Warum ich passe' gespeichert."
        )

    return (
        PreparedAnswer(
            question=question,
            answer=" ".join(
                parts
            ),
            source_summary=(
                "Gespeicherte Recherche zum Zielunternehmen"
            ),
            warnings=warnings,
        ),
        company.company_name,
    )


def _make_strengths(
    request: InterviewPreparationRequest,
    profile,
    stories,
) -> PreparedAnswer:
    skills = _clean(
        profile.technical_skills,
        3,
    )

    competencies = []

    for story in _verified(
        stories
    ):
        competencies.extend(
            story.competencies
        )

    competencies = _clean(
        competencies,
        2,
    )

    strengths = _clean(
        [
            *skills,
            *competencies,
        ],
        4,
    )

    if request.language == "English":
        question = (
            "What are your main strengths?"
        )

        if strengths:
            answer = (
                "My main strengths are "
                + _join_natural(
                    strengths,
                    "English",
                )
                + ". I can support these strengths with verified "
                "examples from my work, projects and STAR stories."
            )
        else:
            answer = ""

        warning = (
            []
            if strengths
            else [
                "No verified skills or STAR competencies are available."
            ]
        )

    else:
        question = (
            "Was sind Ihre wichtigsten Stärken?"
        )

        if strengths:
            answer = (
                "Zu meinen wichtigsten Stärken gehören "
                + _join_natural(
                    strengths,
                    "Deutsch",
                )
                + ". Diese Stärken kann ich mit verifizierten "
                "Beispielen aus Berufserfahrung, Projekten und "
                "STAR-Stories belegen."
            )
        else:
            answer = ""

        warning = (
            []
            if strengths
            else [
                "Es sind keine verifizierten Kenntnisse oder "
                "STAR-Kompetenzen verfügbar."
            ]
        )

    return PreparedAnswer(
        question=question,
        answer=answer,
        source_summary=(
            "Verified skills and STAR competencies"
            if request.language == "English"
            else (
                "Verifizierte Kenntnisse und STAR-Kompetenzen"
            )
        ),
        warnings=warning,
    )


def _make_weakness(
    request: InterviewPreparationRequest,
) -> PreparedAnswer:
    area = (
        request.development_area
        or ""
    ).strip()

    action = (
        request.improvement_action
        or ""
    ).strip()

    evidence = (
        request.improvement_evidence
        or ""
    ).strip()

    if request.language == "English":
        question = (
            "What is one area you are currently working to improve?"
        )

        if not area or not action:
            return PreparedAnswer(
                question=question,
                answer="",
                warnings=[
                    "Enter a real development area and the action you "
                    "are taking to improve it. The Career Agent will "
                    "not invent a weakness for you."
                ],
            )

        answer = (
            f"One area I am currently working to improve is {area}. "
            f"To address it, {action}."
        )

        if evidence:
            answer += (
                f" A concrete sign of progress is {evidence}."
            )

        answer += (
            " I treat this as an active development area and review "
            "my progress regularly."
        )

    else:
        question = (
            "An welchem Entwicklungsbereich arbeiten Sie derzeit?"
        )

        if not area or not action:
            return PreparedAnswer(
                question=question,
                answer="",
                warnings=[
                    "Bitte geben Sie einen echten Entwicklungsbereich "
                    "und Ihre konkrete Verbesserungsmaßnahme ein. "
                    "Der Career Agent erfindet keine Schwäche."
                ],
            )

        answer = (
            f"Ein Bereich, an dem ich derzeit arbeite, ist {area}. "
            f"Um mich darin zu verbessern, {action}."
        )

        if evidence:
            answer += (
                f" Ein konkreter Fortschritt ist {evidence}."
            )

        answer += (
            " Ich betrachte das als aktiven Entwicklungsbereich und "
            "überprüfe meinen Fortschritt regelmäßig."
        )

    return PreparedAnswer(
        question=question,
        answer=answer,
        source_summary=(
            "User-provided development area"
            if request.language == "English"
            else (
                "Vom Nutzer angegebener Entwicklungsbereich"
            )
        ),
    )


def _behavioral_question(
    category: str,
    language: str,
) -> str:
    english = {
        "Problem Solving": (
            "Tell me about a time you solved a difficult problem."
        ),
        "Leadership": (
            "Tell me about a time you demonstrated leadership."
        ),
        "Teamwork": (
            "Tell me about a time you worked effectively in a team."
        ),
        "Conflict": (
            "Tell me about a time you handled a conflict."
        ),
        "Failure / Mistake": (
            "Tell me about a mistake or failure and what you learned."
        ),
        "Technical Challenge": (
            "Tell me about a difficult technical challenge you solved."
        ),
        "Pressure / Deadline": (
            "Tell me about a time you worked under pressure or a tight deadline."
        ),
        "Process Improvement": (
            "Tell me about a process you improved."
        ),
        "Achievement": (
            "Tell me about an achievement you are proud of."
        ),
        "Communication": (
            "Tell me about a time clear communication was important."
        ),
    }

    german = {
        "Problem Solving": (
            "Erzählen Sie von einer Situation, in der Sie ein schwieriges Problem gelöst haben."
        ),
        "Leadership": (
            "Erzählen Sie von einer Situation, in der Sie Führung übernommen haben."
        ),
        "Teamwork": (
            "Erzählen Sie von einer Situation, in der Sie erfolgreich im Team gearbeitet haben."
        ),
        "Conflict": (
            "Erzählen Sie von einer Situation, in der Sie einen Konflikt gelöst haben."
        ),
        "Failure / Mistake": (
            "Erzählen Sie von einem Fehler oder Misserfolg und was Sie daraus gelernt haben."
        ),
        "Technical Challenge": (
            "Erzählen Sie von einer schwierigen technischen Herausforderung, die Sie gelöst haben."
        ),
        "Pressure / Deadline": (
            "Erzählen Sie von einer Situation mit hohem Zeitdruck."
        ),
        "Process Improvement": (
            "Erzählen Sie von einem Prozess, den Sie verbessert haben."
        ),
        "Achievement": (
            "Erzählen Sie von einem Erfolg, auf den Sie besonders stolz sind."
        ),
        "Communication": (
            "Erzählen Sie von einer Situation, in der klare Kommunikation besonders wichtig war."
        ),
    }

    mapping = (
        english
        if language == "English"
        else german
    )

    return mapping.get(
        category,
        (
            "Tell me about a relevant professional example."
            if language == "English"
            else (
                "Erzählen Sie von einem passenden beruflichen Beispiel."
            )
        ),
    )


def _format_star_answer(
    story,
    language: str,
) -> str:
    if language == "English":
        situation = (
            story.situation_en
            or story.situation_de
        ).strip()

        task = (
            story.task_en
            or story.task_de
        ).strip()

        action = (
            story.action_en
            or story.action_de
        ).strip()

        result = (
            story.result_en
            or story.result_de
        ).strip()

        lesson = (
            story.lesson_en
            or story.lesson_de
        ).strip()

        labels = (
            "Situation",
            "Task",
            "Action",
            "Result",
            "Lesson",
        )

    else:
        situation = (
            story.situation_de
            or story.situation_en
        ).strip()

        task = (
            story.task_de
            or story.task_en
        ).strip()

        action = (
            story.action_de
            or story.action_en
        ).strip()

        result = (
            story.result_de
            or story.result_en
        ).strip()

        lesson = (
            story.lesson_de
            or story.lesson_en
        ).strip()

        labels = (
            "Situation",
            "Aufgabe",
            "Vorgehen",
            "Ergebnis",
            "Lerneffekt",
        )

    parts = [
        f"{labels[0]}: {situation}",
        f"{labels[1]}: {task}",
        f"{labels[2]}: {action}",
        f"{labels[3]}: {result}",
    ]

    if lesson:
        parts.append(
            f"{labels[4]}: {lesson}"
        )

    if story.metric_value.strip():
        metric_label = (
            "Measured result"
            if language == "English"
            else "Messbares Ergebnis"
        )

        parts.append(
            f"{metric_label}: "
            + story.metric_value.strip()
        )

    return "\n".join(
        part
        for part in parts
        if not part.endswith(": ")
    )


def _make_behavioral_answers(
    request: InterviewPreparationRequest,
    stories,
) -> list[BehavioralAnswer]:
    verified_stories = _verified(
        stories
    )

    results = []

    for story in verified_stories[:6]:
        if request.language == "English":
            title = (
                story.title_en
                or story.title_de
            ).strip()
        else:
            title = (
                story.title_de
                or story.title_en
            ).strip()

        results.append(
            BehavioralAnswer(
                category=(
                    story.category
                    or "Other"
                ),
                story_title=title,
                question=_behavioral_question(
                    story.category,
                    request.language,
                ),
                answer=_format_star_answer(
                    story,
                    request.language,
                ),
            )
        )

    return results


def _technical_focus(
    profile,
    projects,
) -> list[str]:
    values = list(
        profile.technical_skills
        or []
    )

    for project in _verified(
        projects
    ):
        values.extend(
            project.technologies
        )

        values.extend(
            project.skills
        )

    return _clean(
        values,
        12,
    )


def generate_interview_preparation_pack(
    request: InterviewPreparationRequest,
) -> InterviewPreparationPack:
    if request.language not in (
        "English",
        "Deutsch",
    ):
        raise ValueError(
            "language must be English or Deutsch"
        )

    profile = load_profile()

    experiences = get_work_experiences()
    education = get_education_records()
    projects = get_project_records()
    achievements = get_achievement_records()
    stories = get_star_stories()

    warnings = []

    if not profile.verified:
        warnings.append(
            "Master Career Profile is not verified."
            if request.language == "English"
            else (
                "Das Master-Karriereprofil ist noch nicht verifiziert."
            )
        )

    # Access these collections deliberately so future extensions can
    # use the same verified source set without changing the API.
    _ = (
        _verified(
            experiences
        ),
        _verified(
            education
        ),
        _verified(
            achievements
        ),
    )

    why_company, company_name = (
        _make_why_company(
            request
        )
    )

    behavioral = (
        _make_behavioral_answers(
            request,
            stories,
        )
    )

    if not behavioral:
        warnings.append(
            "No verified STAR stories are available for behavioral answers."
            if request.language == "English"
            else (
                "Für Verhaltensfragen sind noch keine "
                "verifizierten STAR-Stories verfügbar."
            )
        )

    return InterviewPreparationPack(
        language=request.language,
        target_role=(
            request.target_role
        ),
        company_name=company_name,
        tell_me_about_yourself=(
            _make_tell_me_about_yourself(
                request
            )
        ),
        why_this_role=_make_why_role(
            request,
            profile,
            projects,
        ),
        why_this_company=(
            why_company
        ),
        strengths=_make_strengths(
            request,
            profile,
            stories,
        ),
        weakness=_make_weakness(
            request
        ),
        behavioral_answers=(
            behavioral
        ),
        technical_focus=(
            _technical_focus(
                profile,
                projects,
            )
        ),
        warnings=warnings,
    )
