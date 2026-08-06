import json

import streamlit as st

from services.interview_coach import (
    generate_interview_questions,
)
from services.logging_service import (
    get_logger,
    log_event,
    log_exception,
)


logger = get_logger(
    "interview_coach"
)


SECTION_LABELS = {
    "hr_and_motivation": (
        "HR and Motivation"
    ),
    "technical": (
        "Technical Questions"
    ),
    "role_specific": (
        "Role-Specific Questions"
    ),
    "missing_skill_questions": (
        "Missing-Skill Questions"
    ),
    "questions_for_employer": (
        "Questions to Ask the Employer"
    ),
}


def render_question_list(
    title: str,
    questions: list[str],
) -> None:
    """
    Display one interview-question category.
    """

    st.subheader(
        title
    )

    if not questions:
        st.caption(
            "No questions were generated "
            "for this category."
        )

        return

    for question_number, question in enumerate(
        questions,
        start=1,
    ):
        st.write(
            f"**{question_number}.** "
            f"{question}"
        )


def render_language_questions(
    language_result: dict,
) -> None:
    """
    Display all question groups for one language.
    """

    for section_name, section_label in (
        SECTION_LABELS.items()
    ):
        questions = language_result.get(
            section_name,
            [],
        )

        render_question_list(
            title=section_label,
            questions=questions,
        )

        st.divider()


def build_interview_text(
    result: dict,
) -> str:
    """
    Convert the interview preparation set into
    downloadable plain text.
    """

    lines = [
        "JOB MATCH AGENT",
        "BILINGUAL INTERVIEW PREPARATION",
        "=" * 50,
        "",
    ]

    language_configuration = [
        (
            "ENGLISH",
            result.get(
                "english",
                {},
            ),
        ),
        (
            "GERMAN / DEUTSCH",
            result.get(
                "german",
                {},
            ),
        ),
    ]

    for language_heading, language_result in (
        language_configuration
    ):
        lines.extend(
            [
                language_heading,
                "=" * len(
                    language_heading
                ),
                "",
            ]
        )

        for section_name, section_label in (
            SECTION_LABELS.items()
        ):
            lines.append(
                section_label.upper()
            )

            questions = language_result.get(
                section_name,
                [],
            )

            if not questions:
                lines.append(
                    "No questions generated."
                )

            else:
                for question_number, question in enumerate(
                    questions,
                    start=1,
                ):
                    lines.append(
                        f"{question_number}. "
                        f"{question}"
                    )

            lines.append("")

    lines.extend(
        [
            "PREPARATION TIPS",
            "=" * 16,
        ]
    )

    preparation_tips = result.get(
        "preparation_tips",
        [],
    )

    for tip_number, tip in enumerate(
        preparation_tips,
        start=1,
    ):
        lines.append(
            f"{tip_number}. {tip}"
        )

    lines.extend(
        [
            "",
            "WARNINGS",
            "=" * 8,
        ]
    )

    warnings = result.get(
        "warnings",
        [],
    )

    for warning_number, warning in enumerate(
        warnings,
        start=1,
    ):
        lines.append(
            f"{warning_number}. {warning}"
        )

    lines.extend(
        [
            "",
            (
                "Review all generated questions and "
                "prepare only truthful answers."
            ),
        ]
    )

    return "\n".join(
        lines
    )


def render_interview_results(
    result: dict,
) -> None:
    """
    Display the complete bilingual interview set.
    """

    st.success(
        "Interview preparation was generated."
    )

    english_tab, german_tab, preparation_tab = (
        st.tabs(
            [
                "English Questions",
                "German Questions",
                "Preparation Guidance",
            ]
        )
    )

    with english_tab:
        render_language_questions(
            result.get(
                "english",
                {},
            )
        )

    with german_tab:
        render_language_questions(
            result.get(
                "german",
                {},
            )
        )

    with preparation_tab:
        render_question_list(
            title="Preparation Tips",
            questions=result.get(
                "preparation_tips",
                [],
            ),
        )

        st.divider()

        warnings = result.get(
            "warnings",
            [],
        )

        st.subheader(
            "Important Warnings"
        )

        if warnings:
            for warning in warnings:
                st.warning(
                    warning
                )

        else:
            st.caption(
                "No additional warnings "
                "were generated."
            )

    st.divider()

    interview_text = build_interview_text(
        result
    )

    result_json = json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    )

    download_col1, download_col2 = (
        st.columns(2)
    )

    with download_col1:
        st.download_button(
            label=(
                "Download Interview Questions"
            ),
            data=interview_text.encode(
                "utf-8"
            ),
            file_name=(
                "interview_preparation.txt"
            ),
            mime="text/plain",
            width="stretch",
            key=(
                "download_interview_questions"
            ),
        )

    with download_col2:
        st.download_button(
            label=(
                "Download Structured JSON"
            ),
            data=result_json.encode(
                "utf-8"
            ),
            file_name=(
                "interview_preparation.json"
            ),
            mime="application/json",
            width="stretch",
            key=(
                "download_interview_json"
            ),
        )


def render_interview_coach(
    cv_text: str,
    job_text: str,
    extracted_job_details: dict,
    match_result: dict,
    category_match_result: dict,
    german_recruiter_report: dict,
) -> None:
    """
    Render the bilingual AI Interview Coach.
    """

    st.divider()

    st.header(
        "AI Interview Coach"
    )

    st.caption(
        "Generate realistic English and German "
        "interview questions based on your CV "
        "and the selected job."
    )

    st.info(
        "The coach uses your local Ollama model. "
        "Generated questions may take some time."
    )

    if st.button(
        "Generate Interview Preparation",
        type="primary",
        width="stretch",
        key=(
            "generate_interview_preparation"
        ),
    ):
        try:
            with st.spinner(
                "Generating English and German "
                "interview questions..."
            ):
                result = (
                    generate_interview_questions(
                        cv_text=cv_text,
                        job_text=job_text,
                        extracted_job_details=(
                            extracted_job_details
                        ),
                        match_result=match_result,
                        category_match_result=(
                            category_match_result
                        ),
                        german_recruiter_report=(
                            german_recruiter_report
                        ),
                    )
                )

            st.session_state[
                "interview_coach_result"
            ] = result

            log_event(
                logger=logger,
                message=(
                    "Interview preparation generated."
                ),
                context={
                    "company": (
                        extracted_job_details.get(
                            "company",
                            "",
                        )
                    ),
                    "job_title": (
                        extracted_job_details.get(
                            "job_title",
                            "",
                        )
                    ),
                },
            )

        except Exception as error:
            log_exception(
                logger=logger,
                error=error,
                message=(
                    "Interview preparation "
                    "generation failed."
                ),
                context={
                    "company": (
                        extracted_job_details.get(
                            "company",
                            "",
                        )
                    ),
                    "job_title": (
                        extracted_job_details.get(
                            "job_title",
                            "",
                        )
                    ),
                },
            )

            st.error(
                "Interview preparation "
                "could not be generated."
            )

            st.code(
                f"{type(error).__name__}: {error}"
            )

            st.info(
                "Confirm that Ollama is running "
                "and check Settings → Logs."
            )

    result = st.session_state.get(
        "interview_coach_result"
    )

    if result:
        render_interview_results(
            result
        )