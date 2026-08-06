import re

import streamlit as st

from services.cv_generator_service import (
    create_tailored_cv,
)


def create_cv_filename(
    candidate_name: str,
    company: str,
    extension: str,
) -> str:
    """
    Create a safe download filename.
    """

    filename = (
        f"tailored_cv_"
        f"{candidate_name}_"
        f"{company}"
    ).lower()

    filename = re.sub(
        r"[^a-z0-9äöüß]+",
        "_",
        filename,
    ).strip("_")

    if not filename:
        filename = "tailored_cv"

    return f"{filename}.{extension}"


def render_cv_generator(
    cv_text: str,
    job_text: str,
    extracted_job_details: dict,
) -> None:
    """
    Render the local-AI tailored CV generator.
    """

    st.divider()
    st.header(
        "Tailored CV Generator"
    )

    st.caption(
        "The local AI rewrites and reorganizes only "
        "information already present in your original CV."
    )

    candidate_name = st.text_input(
        "Candidate name",
        key="tailored_cv_candidate_name",
        placeholder="Enter your full name",
    )

    language = st.selectbox(
        "Tailored CV language",
        [
            "English",
            "German",
        ],
        key="tailored_cv_language",
    )

    company = extracted_job_details.get(
        "company",
        "",
    )

    job_title = extracted_job_details.get(
        "job_title",
        "",
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(
            f"**Target company:** "
            f"{company or 'Not detected'}"
        )

    with info_col2:
        st.write(
            f"**Target role:** "
            f"{job_title or 'Not detected'}"
        )

    if st.button(
        "Generate Tailored CV",
        type="primary",
        use_container_width=True,
        key="generate_tailored_cv",
    ):
        if not candidate_name.strip():
            st.error(
                "Please enter the candidate name."
            )

        else:
            try:
                with st.spinner(
                    "Generating the tailored CV "
                    "with the local AI model..."
                ):
                    result = create_tailored_cv(
                        cv_text=cv_text,
                        job_text=job_text,
                        job_details=(
                            extracted_job_details
                        ),
                        language=language,
                    )

                st.session_state[
                    "tailored_cv_text"
                ] = result["text"]

                st.session_state[
                    "tailored_cv_docx"
                ] = result["docx"]

                st.session_state[
                    "tailored_cv_warnings"
                ] = result["warnings"]

                st.session_state[
                    "tailored_cv_txt_filename"
                ] = create_cv_filename(
                    candidate_name=(
                        candidate_name
                    ),
                    company=company,
                    extension="txt",
                )

                st.session_state[
                    "tailored_cv_docx_filename"
                ] = create_cv_filename(
                    candidate_name=(
                        candidate_name
                    ),
                    company=company,
                    extension="docx",
                )

                st.success(
                    "Tailored CV generated successfully."
                )

            except Exception as error:
                st.error(
                    "Tailored CV generation failed: "
                    f"{error}"
                )

    warnings = st.session_state.get(
        "tailored_cv_warnings",
        [],
    )

    for warning in warnings:
        st.warning(
            warning
        )

    generated_text = st.session_state.get(
        "tailored_cv_text",
        "",
    )

    generated_docx = st.session_state.get(
        "tailored_cv_docx",
        None,
    )

    if generated_text:
        st.subheader(
            "Review the Tailored CV"
        )

        edited_text = st.text_area(
            "Tailored CV text",
            value=generated_text,
            height=700,
            key="editable_tailored_cv",
        )

        download_col1, download_col2 = (
            st.columns(2)
        )

        with download_col1:
            st.download_button(
                label="Download CV as TXT",
                data=edited_text.encode(
                    "utf-8"
                ),
                file_name=st.session_state.get(
                    "tailored_cv_txt_filename",
                    "tailored_cv.txt",
                ),
                mime="text/plain",
                use_container_width=True,
                key="download_tailored_cv_txt",
            )

        with download_col2:
            if generated_docx:
                st.download_button(
                    label="Download CV as DOCX",
                    data=generated_docx,
                    file_name=st.session_state.get(
                        "tailored_cv_docx_filename",
                        "tailored_cv.docx",
                    ),
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.wordprocessingml.document"
                    ),
                    use_container_width=True,
                    key="download_tailored_cv_docx",
                )

        st.warning(
            "Check every section before applying. "
            "Delete any sentence that is not fully accurate."
        )