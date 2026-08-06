import re

import streamlit as st

from services.cover_letter_service import (
    create_cover_letter,
)


def create_safe_filename(
    company: str,
    job_title: str,
    language: str,
) -> str:
    """
    Create a Windows-safe download filename.
    """

    filename = (
        f"cover_letter_"
        f"{company}_"
        f"{job_title}_"
        f"{language}"
    )

    filename = filename.lower()

    filename = re.sub(
        r"[^a-z0-9äöüß]+",
        "_",
        filename,
    )

    filename = filename.strip("_")

    if not filename:
        filename = "cover_letter"

    return f"{filename}.txt"


def render_cover_letter_generator(
    cv_text: str,
    job_text: str,
    extracted_job_details: dict,
) -> None:
    """
    Display the local-AI cover-letter generator.
    """

    st.divider()
    st.header("Tailored Cover Letter")

    st.caption(
        "The letter is generated locally with Ollama. "
        "Review every sentence before using it."
    )

    candidate_name = st.text_input(
        "Your full name",
        key="cover_letter_candidate_name",
        placeholder="Enter your full name",
    )

    language = st.selectbox(
        "Cover-letter language",
        [
            "English",
            "German",
        ],
        key="cover_letter_language",
    )

    company = extracted_job_details.get(
        "company",
        "",
    )

    job_title = extracted_job_details.get(
        "job_title",
        "",
    )

    information_col1, information_col2 = (
        st.columns(2)
    )

    with information_col1:
        st.write(
            f"**Company:** "
            f"{company or 'Not detected'}"
        )

    with information_col2:
        st.write(
            f"**Position:** "
            f"{job_title or 'Not detected'}"
        )

    if st.button(
        "Generate Tailored Cover Letter",
        type="primary",
        use_container_width=True,
        key="generate_cover_letter_button",
    ):
        if not candidate_name.strip():
            st.error(
                "Please enter your full name."
            )

        else:
            try:
                with st.spinner(
                    "Generating your tailored cover letter "
                    "with the local AI model..."
                ):
                    result = create_cover_letter(
                        cv_text=cv_text,
                        job_text=job_text,
                        job_details=(
                            extracted_job_details
                        ),
                        language=language,
                        candidate_name=(
                            candidate_name
                        ),
                    )

                st.session_state[
                    "generated_cover_letter"
                ] = result["complete_text"]

                st.session_state[
                    "cover_letter_warnings"
                ] = result["warnings"]

                st.session_state[
                    "cover_letter_filename"
                ] = create_safe_filename(
                    company=company,
                    job_title=job_title,
                    language=language,
                )

                st.success(
                    "Cover letter generated successfully."
                )

            except Exception as error:
                st.error(
                    f"Cover-letter generation failed: "
                    f"{error}"
                )

    generated_letter = st.session_state.get(
        "generated_cover_letter",
        "",
    )

    warnings = st.session_state.get(
        "cover_letter_warnings",
        [],
    )

    if warnings:
        st.subheader("Generation Warnings")

        for warning in warnings:
            st.warning(warning)

    if generated_letter:
        st.subheader(
            "Review and Edit Your Letter"
        )

        edited_letter = st.text_area(
            "Cover letter",
            value=generated_letter,
            height=600,
            key="editable_cover_letter",
        )

        filename = st.session_state.get(
            "cover_letter_filename",
            "cover_letter.txt",
        )

        st.download_button(
            label="Download Cover Letter",
            data=edited_letter.encode(
                "utf-8"
            ),
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
            key="download_cover_letter",
        )

        st.warning(
            "Do not send the letter before verifying "
            "all claims, names and contact details."
        )