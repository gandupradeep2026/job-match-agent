from __future__ import annotations

import json
import sys
from pathlib import Path

from services.application_browser import (
    open_filled_application_for_review,
)


def main() -> int:
    if len(
        sys.argv
    ) != 2:
        print(
            "Usage: python -m "
            "services.application_browser_runner "
            "<payload.json>"
        )
        return 2

    payload_path = Path(
        sys.argv[1]
    )

    if not payload_path.exists():
        print(
            f"Payload file not found: "
            f"{payload_path}"
        )
        return 2

    payload = json.loads(
        payload_path.read_text(
            encoding="utf-8"
        )
    )

    try:
        result = (
            open_filled_application_for_review(
                job_url=payload[
                    "job_url"
                ],
                applicant_profile=(
                    payload.get(
                        "applicant_profile",
                        {},
                    )
                ),
                resume_path=(
                    payload.get(
                        "resume_path"
                    )
                ),
                field_mapping_overrides=(
                    payload.get(
                        "field_mapping_overrides",
                        {},
                    )
                ),
                custom_answers=(
                    payload.get(
                        "custom_answers",
                        {},
                    )
                ),
            )
        )

        result_path = (
            payload_path.parent
            / "result.json"
        )

        result_path.write_text(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return 0

    except Exception as error:
        error_path = (
            payload_path.parent
            / "error.txt"
        )

        error_path.write_text(
            f"{type(error).__name__}: "
            f"{error}",
            encoding="utf-8",
        )

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
