import streamlit as st

from services.job_url_importer import (
    JobURLImportError,
    import_job_from_url,
)


def clear_imported_job() -> None:
    """
    Remove all previously imported job-page information.
    """

    keys_to_remove = [
        "imported_job_text",
        "imported_job_url",
        "imported_job_title",
        "imported_job_confidence",
        "imported_job_method",
        "imported_job_warnings",
        "imported_job_text_editor",
        "public_job_url",
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None,
        )


def render_job_description_input() -> dict:
    """
    Render all supported job-description input methods.

    Returns:
        A dictionary containing:
        - method
        - file
        - text
        - job_url
    """

    st.subheader(
        "2. Provide the job description"
    )

    input_method = st.radio(
        "Choose how you want to provide the job description:",
        [
            "Upload document",
            "Paste as text",
            "Import public job URL",
        ],
        horizontal=True,
        key="job_input_method",
    )

    result = {
        "method": input_method,
        "file": None,
        "text": "",
        "job_url": "",
    }

    # ==================================================
    # DOCUMENT UPLOAD
    # ==================================================
    if input_method == "Upload document":
        result["file"] = st.file_uploader(
            "Upload the job description",
            type=[
                "pdf",
                "docx",
                "txt",
            ],
            key="job_file",
        )

        return result

    # ==================================================
    # PASTED TEXT
    # ==================================================
    if input_method == "Paste as text":
        result["text"] = st.text_area(
            "Paste the job description",
            height=300,
            key="job_text",
            placeholder=(
                "Paste the complete job description here..."
            ),
        )

        return result

    # ==================================================
    # PUBLIC JOB URL
    # ==================================================
    st.info(
        "Use a public company career-page URL that opens "
        "without signing in. LinkedIn, Indeed and StepStone "
        "may block automatic reading."
    )

    job_url = st.text_input(
        "Public job-page URL",
        key="public_job_url",
        placeholder=(
            "https://company.example.com/careers/job/123"
        ),
    )

    import_col, clear_col = st.columns(2)

    with import_col:
        import_clicked = st.button(
            "Import Job Page",
            type="primary",
            width="stretch",
            key="import_public_job_url",
        )

    with clear_col:
        clear_clicked = st.button(
            "Clear Imported Job",
            width="stretch",
            key="clear_public_job_url",
        )

    if clear_clicked:
        clear_imported_job()
        st.rerun()

    if import_clicked:
        if not job_url.strip():
            st.error(
                "Please enter a public job-page URL."
            )

        else:
            try:
                with st.spinner(
                    "Downloading and extracting the public job page..."
                ):
                    imported_result = import_job_from_url(
                        job_url
                    )

                imported_text = imported_result.get(
                    "text",
                    "",
                )

                st.session_state[
                    "imported_job_text"
                ] = imported_text

                st.session_state[
                    "imported_job_text_editor"
                ] = imported_text

                st.session_state[
                    "imported_job_url"
                ] = imported_result.get(
                    "final_url",
                    "",
                )

                st.session_state[
                    "imported_job_title"
                ] = imported_result.get(
                    "title",
                    "",
                )

                st.session_state[
                    "imported_job_confidence"
                ] = imported_result.get(
                    "job_page_confidence",
                    "unknown",
                )

                st.session_state[
                    "imported_job_method"
                ] = imported_result.get(
                    "extraction_method",
                    "",
                )

                st.session_state[
                    "imported_job_warnings"
                ] = imported_result.get(
                    "warnings",
                    [],
                )

                st.success(
                    "The public job page was imported successfully."
                )

            except JobURLImportError as error:
                st.error(
                    "The job page could not be imported."
                )

                st.warning(
                    str(error)
                )

                st.info(
                    "Open the job manually, copy the complete "
                    "description and use Paste as text."
                )

            except Exception as error:
                st.error(
                    "An unexpected URL-import error occurred."
                )

                st.code(
                    f"{type(error).__name__}: {error}"
                )

    imported_text = st.session_state.get(
        "imported_job_text",
        "",
    )

    imported_url = st.session_state.get(
        "imported_job_url",
        "",
    )

    if imported_text:
        title = st.session_state.get(
            "imported_job_title",
            "",
        )

        confidence = st.session_state.get(
            "imported_job_confidence",
            "unknown",
        )

        extraction_method = st.session_state.get(
            "imported_job_method",
            "",
        )

        warnings = st.session_state.get(
            "imported_job_warnings",
            [],
        ) or []

        st.success(
            "A job description is ready for verification."
        )

        information_col1, information_col2 = (
            st.columns(2)
        )

        with information_col1:
            st.write(
                f"**Page title:** "
                f"{title or 'Not detected'}"
            )

            st.write(
                f"**Job-page confidence:** "
                f"{confidence.title()}"
            )

        with information_col2:
            st.write(
                f"**Extraction method:** "
                f"{extraction_method or 'Unknown'}"
            )

            st.write(
                f"**Characters extracted:** "
                f"{len(imported_text)}"
            )

        for warning in warnings:
            st.warning(
                warning
            )

        st.write(
            "**Review and edit the extracted job description:**"
        )

        edited_job_text = st.text_area(
            "Imported job-description text",
            height=450,
            key="imported_job_text_editor",
        )

        st.session_state[
            "imported_job_text"
        ] = edited_job_text

        if imported_url:
            st.write(
                f"**Final job URL:** {imported_url}"
            )

        result["text"] = edited_job_text
        result["job_url"] = imported_url

    return result