from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from pathlib import Path


RUN_DIRECTORY = Path(
    "uploads/application_agent_runs"
)


def _safe_filename(
    filename: str,
) -> str:
    cleaned = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        filename,
    ).strip(
        "._"
    )

    return (
        cleaned
        or "resume.bin"
    )


def launch_application_review(
    job_url: str,
    applicant_profile: dict,
    resume_upload=None,
    field_mapping_overrides: dict | None = None,
    custom_answers: dict | None = None,
) -> dict:
    """
    Start a separate headed Playwright process.

    The child process fills supported fields and leaves the
    browser open for manual review. It never submits the form.
    """

    normalized_url = (
        job_url
        or ""
    ).strip()

    if not normalized_url:
        raise ValueError(
            "Job URL is required."
        )

    RUN_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_id = uuid.uuid4().hex

    run_directory = (
        RUN_DIRECTORY
        / run_id
    )

    run_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    resume_path = None

    if resume_upload is not None:
        resume_name = _safe_filename(
            getattr(
                resume_upload,
                "name",
                "resume.bin",
            )
        )

        resume_file_path = (
            run_directory
            / resume_name
        )

        resume_file_path.write_bytes(
            resume_upload.getvalue()
        )

        resume_path = str(
            resume_file_path.resolve()
        )

    serializable_profile = {
        key: value
        for key, value
        in (
            applicant_profile
            or {}
        ).items()
        if key != "resume"
    }

    payload = {
        "run_id": run_id,
        "job_url": normalized_url,
        "applicant_profile": (
            serializable_profile
        ),
        "resume_path": resume_path,
        "field_mapping_overrides": (
            field_mapping_overrides
            or {}
        ),
        "custom_answers": (
            custom_answers
            or {}
        ),
    }

    payload_path = (
        run_directory
        / "payload.json"
    )

    payload_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    log_path = (
        run_directory
        / "review_browser.log"
    )

    command = [
        sys.executable,
        "-m",
        "services.application_browser_runner",
        str(
            payload_path.resolve()
        ),
    ]

    creation_flags = 0

    if sys.platform.startswith(
        "win"
    ):
        creation_flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
        )

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as log_file:
        process = subprocess.Popen(
            command,
            cwd=str(
                Path.cwd()
            ),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags,
        )

    return {
        "run_id": run_id,
        "pid": process.pid,
        "payload_path": str(
            payload_path
        ),
        "log_path": str(
            log_path
        ),
    }
