from __future__ import annotations

import json
import re

from ollama import chat
from pydantic import BaseModel, Field, ValidationError

from career.polishing import (
    CareerPolishRequest,
    CareerPolishResult,
)
from services.local_ai_service import (
    get_ollama_model,
)


class LocalPolishResponse(BaseModel):
    polished_text: str = ""
    changes_made: list[str] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(
        default_factory=list
    )


def _extract_numbers(
    value: str,
) -> set[str]:
    return set(
        re.findall(
            r"(?<!\w)[+-]?\d+(?:[.,]\d+)?%?(?!\w)",
            value or "",
        )
    )


def _extract_emails(
    value: str,
) -> set[str]:
    return {
        item.casefold()
        for item in re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            value or "",
        )
    }


def _extract_urls(
    value: str,
) -> set[str]:
    return {
        item.rstrip(
            ".,);]"
        ).casefold()
        for item in re.findall(
            r"https?://[^\s]+",
            value or "",
        )
    }


def _truth_lock_warnings(
    source_text: str,
    polished_text: str,
) -> list[str]:
    warnings = []

    new_numbers = (
        _extract_numbers(
            polished_text
        )
        - _extract_numbers(
            source_text
        )
    )

    if new_numbers:
        warnings.append(
            "Truth Lock blocked newly introduced numeric claims: "
            + ", ".join(
                sorted(
                    new_numbers
                )
            )
        )

    new_emails = (
        _extract_emails(
            polished_text
        )
        - _extract_emails(
            source_text
        )
    )

    if new_emails:
        warnings.append(
            "Truth Lock blocked newly introduced email addresses."
        )

    new_urls = (
        _extract_urls(
            polished_text
        )
        - _extract_urls(
            source_text
        )
    )

    if new_urls:
        warnings.append(
            "Truth Lock blocked newly introduced URLs."
        )

    return warnings


def build_career_polish_prompt(
    request: CareerPolishRequest,
) -> str:
    schema_text = json.dumps(
        LocalPolishResponse.model_json_schema(),
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are a conservative professional career-writing editor.

Your task is to improve ONLY the wording of the supplied verified source text.

Output language: {request.language}
Content type: {request.content_type}
Preferred style: {request.style}

TRUTH LOCK — mandatory rules:

1. The source text is the complete factual boundary.
2. Do not add any new employer, company, university, project, technology,
   skill, certification, responsibility, achievement, date, duration,
   percentage, money amount, user count, team size, location, language level,
   qualification or other factual claim.
3. Do not infer facts that are not explicitly present in the source text.
4. Do not strengthen a statement beyond what the source actually says.
5. Do not create quantified results.
6. Preserve all existing names, numbers, dates, URLs and email addresses accurately.
7. You may improve grammar, sentence flow, clarity, concision, professional tone
   and spoken naturalness when appropriate.
8. For German, write natural professional German rather than literal translation.
9. For interview answers, prefer natural spoken language rather than CV-style fragments.
10. For CV content, prefer concise ATS-readable wording.
11. If the source is too vague to improve safely, keep it close to the original
    and put the limitation in warnings.
12. Return only JSON matching the supplied schema.
13. Do not include markdown outside the JSON.

JSON schema:

{schema_text}

--- START VERIFIED SOURCE TEXT ---

{request.source_text}

--- END VERIFIED SOURCE TEXT ---
""".strip()


def polish_career_text(
    request: CareerPolishRequest,
) -> CareerPolishResult:
    source_text = (
        request.source_text
        or ""
    ).strip()

    if not source_text:
        raise ValueError(
            "Source text is empty."
        )

    if request.language not in (
        "English",
        "Deutsch",
    ):
        raise ValueError(
            "language must be English or Deutsch"
        )

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": (
                    build_career_polish_prompt(
                        request
                    )
                ),
            }
        ],
        format=(
            LocalPolishResponse.model_json_schema()
        ),
        options={
            "temperature": 0,
        },
    )

    response_text = (
        response.message.content
        or ""
    ).strip()

    if not response_text:
        raise ValueError(
            "The local AI returned an empty response."
        )

    try:
        parsed = (
            LocalPolishResponse
            .model_validate_json(
                response_text
            )
        )

    except ValidationError as error:
        raise ValueError(
            "The local AI response did not match the required structure."
        ) from error

    polished_text = (
        parsed.polished_text
        or ""
    ).strip()

    if not polished_text:
        raise ValueError(
            "The local AI returned empty polished text."
        )

    safety_warnings = (
        _truth_lock_warnings(
            source_text,
            polished_text,
        )
    )

    if safety_warnings:
        # Do not return unsafe rewritten content as the active result.
        return CareerPolishResult(
            source_text=source_text,
            polished_text=source_text,
            language=request.language,
            content_type=request.content_type,
            style=request.style,
            changes_made=[],
            warnings=[
                *parsed.warnings,
                *safety_warnings,
                (
                    "The rewritten version was rejected and the verified "
                    "source text was restored."
                ),
            ],
            safety_passed=False,
        )

    return CareerPolishResult(
        source_text=source_text,
        polished_text=polished_text,
        language=request.language,
        content_type=request.content_type,
        style=request.style,
        changes_made=[
            item.strip()
            for item in parsed.changes_made
            if item.strip()
        ],
        warnings=[
            item.strip()
            for item in parsed.warnings
            if item.strip()
        ],
        safety_passed=True,
    )
