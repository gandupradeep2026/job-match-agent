import json

import streamlit as st

from services.interview_coach import (
    generate_interview_questions,
)
from services.interview_simulator import (
    build_question_bank,
    calculate_session_summary,
    evaluate_interview_answer,
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

def reset_interview_simulator() -> None:
    """
    Clear all simulator-specific session state.
    """

    keys = [
        "interview_simulator_questions",
        "interview_simulator_index",
        "interview_simulator_evaluations",
        "interview_simulator_answer",
        "interview_simulator_last_feedback",
        "interview_simulator_complete",
    ]

    for key in keys:
        st.session_state.pop(
            key,
            None,
        )


def render_feedback_scores(
    feedback: dict,
) -> None:
    """
    Display the score breakdown for one answer.
    """

    scores = feedback.get(
        "scores",
        {},
    )

    score_col1, score_col2, score_col3, score_col4, score_col5 = (
        st.columns(5)
    )

    score_configuration = [
        (
            score_col1,
            "Relevance",
            "relevance",
        ),
        (
            score_col2,
            "Clarity",
            "clarity",
        ),
        (
            score_col3,
            "Evidence",
            "evidence",
        ),
        (
            score_col4,
            "Structure",
            "structure",
        ),
        (
            score_col5,
            "Confidence",
            "confidence",
        ),
    ]

    for column, label, key in score_configuration:
        with column:
            st.metric(
                label,
                f"{scores.get(key, 0)}/10",
            )


def render_interview_simulator(
    cv_text: str,
    job_text: str,
    interview_result: dict,
) -> None:
    """
    Render the interactive one-question-at-a-time simulator.
    """

    st.divider()
    st.header(
        "Interactive Interview Simulator"
    )

    st.caption(
        "Answer one question at a time and receive local-AI feedback "
        "on relevance, clarity, evidence, structure, and confidence."
    )

    if not interview_result:
        st.info(
            "Generate interview preparation first. "
            "The simulator uses those role-specific questions."
        )
        return

    control_col1, control_col2, control_col3 = (
        st.columns(3)
    )

    with control_col1:
        language = st.selectbox(
            "Simulator language",
            [
                "English",
                "German",
            ],
            key="interview_simulator_language",
        )

    with control_col2:
        question_count = st.selectbox(
            "Number of questions",
            [
                3,
                5,
                8,
                10,
            ],
            index=1,
            key="interview_simulator_question_count",
        )

    with control_col3:
        st.write("")
        st.write("")

        if st.button(
            "Start New Simulation",
            type="primary",
            use_container_width=True,
            key="start_interview_simulator",
        ):
            questions = build_question_bank(
                interview_result=interview_result,
                language=language,
                maximum_questions=question_count,
            )

            if not questions:
                st.error(
                    "No simulator questions are available."
                )
            else:
                reset_interview_simulator()

                st.session_state[
                    "interview_simulator_questions"
                ] = questions

                st.session_state[
                    "interview_simulator_index"
                ] = 0

                st.session_state[
                    "interview_simulator_evaluations"
                ] = []

                st.session_state[
                    "interview_simulator_complete"
                ] = False

                st.rerun()

    questions = st.session_state.get(
        "interview_simulator_questions",
        [],
    )

    if not questions:
        return

    current_index = int(
        st.session_state.get(
            "interview_simulator_index",
            0,
        )
    )

    evaluations = st.session_state.get(
        "interview_simulator_evaluations",
        [],
    )

    if current_index >= len(
        questions
    ):
        st.session_state[
            "interview_simulator_complete"
        ] = True

    if st.session_state.get(
        "interview_simulator_complete",
        False,
    ):
        summary = calculate_session_summary(
            evaluations
        )

        st.success(
            "Interview simulation completed."
        )

        summary_col1, summary_col2, summary_col3, summary_col4 = (
            st.columns(4)
        )

        with summary_col1:
            st.metric(
                "Average Score",
                f"{summary.get('average_score', 0)}/10",
            )

        with summary_col2:
            st.metric(
                "Questions Answered",
                summary.get(
                    "answered_questions",
                    0,
                ),
            )

        with summary_col3:
            st.metric(
                "Strongest Area",
                summary.get(
                    "strongest_area",
                    "",
                ),
            )

        with summary_col4:
            st.metric(
                "Weakest Area",
                summary.get(
                    "weakest_area",
                    "",
                ),
            )

        if st.button(
            "Restart Simulation",
            use_container_width=True,
            key="restart_interview_simulator",
        ):
            reset_interview_simulator()
            st.rerun()

        return

    current_item = questions[
        current_index
    ]

    st.progress(
        (current_index + 1)
        / len(
            questions
        )
    )

    st.write(
        f"**Question {current_index + 1} "
        f"of {len(questions)}**"
    )

    st.caption(
        f"Category: "
        f"{current_item.get('category', '')}"
    )

    st.subheader(
        current_item.get(
            "question",
            "",
        )
    )

    answer = st.text_area(
        "Your answer",
        height=220,
        key="interview_simulator_answer",
        placeholder=(
            "Type the answer you would give in the real interview..."
        ),
    )

    if st.button(
        "Evaluate Answer",
        type="primary",
        use_container_width=True,
        key="evaluate_interview_answer",
    ):
        if not answer.strip():
            st.error(
                "Please enter your answer first."
            )
        else:
            try:
                with st.spinner(
                    "Evaluating your answer..."
                ):
                    feedback = evaluate_interview_answer(
                        question=current_item.get(
                            "question",
                            "",
                        ),
                        answer=answer,
                        cv_text=cv_text,
                        job_text=job_text,
                        language=language,
                    )

                evaluation_record = {
                    **feedback,
                    "question": current_item.get(
                        "question",
                        "",
                    ),
                    "answer": answer,
                    "category": current_item.get(
                        "category",
                        "",
                    ),
                }

                evaluations.append(
                    evaluation_record
                )

                st.session_state[
                    "interview_simulator_evaluations"
                ] = evaluations

                st.session_state[
                    "interview_simulator_last_feedback"
                ] = feedback

            except Exception as error:
                st.error(
                    "Answer evaluation failed."
                )

                st.code(
                    f"{type(error).__name__}: {error}"
                )

                st.info(
                    "Confirm that Ollama is running."
                )

    feedback = st.session_state.get(
        "interview_simulator_last_feedback",
        {},
    )

    if feedback:
        st.subheader(
            "Answer Feedback"
        )

        st.metric(
            "Overall Score",
            f"{feedback.get('overall_score', 0)}/10",
        )

        render_feedback_scores(
            feedback
        )

        summary_text = feedback.get(
            "summary",
            "",
        )

        if summary_text:
            st.info(
                summary_text
            )

        feedback_col1, feedback_col2 = (
            st.columns(2)
        )

        with feedback_col1:
            st.write(
                "### Strengths"
            )

            strengths = feedback.get(
                "strengths",
                [],
            )

            if strengths:
                for strength in strengths:
                    st.success(
                        strength
                    )
            else:
                st.caption(
                    "No specific strengths were returned."
                )

        with feedback_col2:
            st.write(
                "### Improvements"
            )

            improvements = feedback.get(
                "improvements",
                [],
            )

            if improvements:
                for improvement in improvements:
                    st.warning(
                        improvement
                    )
            else:
                st.caption(
                    "No specific improvements were returned."
                )

        suggested_answer = feedback.get(
            "suggested_answer",
            "",
        )

        if suggested_answer:
            st.write(
                "### Stronger Truthful Answer"
            )

            st.text_area(
                "Suggested answer",
                value=suggested_answer,
                height=220,
                key=(
                    f"interview_suggested_answer_"
                    f"{current_index}"
                ),
            )

        warnings = feedback.get(
            "warnings",
            [],
        )

        for warning in warnings:
            st.error(
                warning
            )

        if st.button(
            "Next Question",
            type="primary",
            use_container_width=True,
            key="next_interview_question",
        ):
            st.session_state[
                "interview_simulator_index"
            ] = current_index + 1

            st.session_state.pop(
                "interview_simulator_answer",
                None,
            )

            st.session_state.pop(
                "interview_simulator_last_feedback",
                None,
            )

            st.rerun()

    st.warning(
        "Use feedback to improve your communication, but never "
        "memorize or repeat a claim that is not true."
    )
