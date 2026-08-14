from __future__ import annotations

from typing import Any

from playwright.sync_api import Page, sync_playwright


FORM_SELECTOR = (
    "input:not([type='hidden']):not([type='submit']):"
    "not([type='button']):not([type='reset']), "
    "textarea, select"
)

SAFE_TEXT_INPUT_TYPES = {
    "",
    "text",
    "email",
    "tel",
    "url",
    "search",
    "number",
    "date",
}

MANUAL_ONLY_INPUT_TYPES = {
    "checkbox",
    "radio",
}

UNSAFE_INPUT_TYPES = {
    "password",
    "hidden",
    "submit",
    "button",
    "reset",
    "image",
}


def _contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    return any(
        keyword in text
        for keyword in keywords
    )


def classify_application_field(
    field: dict,
) -> str:
    """
    Convert a detected form field into a standard
    Application Agent profile key.

    The classifier is intentionally conservative.
    Unknown or ambiguous fields remain "unknown".
    """

    searchable_text = " ".join(
        [
            str(field.get("label", "")),
            str(field.get("name", "")),
            str(field.get("id", "")),
            str(field.get("placeholder", "")),
            str(field.get("autocomplete", "")),
        ]
    ).lower()

    field_type = str(
        field.get("type", "")
    ).lower()

    autocomplete = str(
        field.get("autocomplete", "")
    ).lower()

    if field_type == "file":
        return "resume"

    if autocomplete == "given-name":
        return "first_name"

    if autocomplete == "family-name":
        return "last_name"

    if autocomplete == "name":
        return "full_name"

    if autocomplete == "email":
        return "email"

    if autocomplete in {
        "tel",
        "tel-national",
    }:
        return "phone"

    if autocomplete == "street-address":
        return "address"

    if autocomplete == "postal-code":
        return "postal_code"

    if autocomplete in {
        "address-level2",
        "address-level1",
    }:
        return "city"

    if autocomplete == "country-name":
        return "country"

    if _contains_any(
        searchable_text,
        [
            "first name",
            "firstname",
            "first_name",
            "given name",
            "given_name",
            "vorname",
        ],
    ):
        return "first_name"

    if _contains_any(
        searchable_text,
        [
            "last name",
            "lastname",
            "last_name",
            "surname",
            "family name",
            "family_name",
            "nachname",
        ],
    ):
        return "last_name"

    if _contains_any(
        searchable_text,
        [
            "full name",
            "fullname",
            "full_name",
            "your name",
        ],
    ):
        return "full_name"

    if (
        field_type == "email"
        or _contains_any(
            searchable_text,
            [
                "email",
                "e-mail",
            ],
        )
    ):
        return "email"

    if (
        field_type == "tel"
        or _contains_any(
            searchable_text,
            [
                "phone",
                "telephone",
                "mobile",
                "telefon",
                "handy",
            ],
        )
    ):
        return "phone"

    if "linkedin" in searchable_text:
        return "linkedin"

    if "github" in searchable_text:
        return "github"

    if _contains_any(
        searchable_text,
        [
            "portfolio",
            "personal website",
            "personal site",
            "website url",
            "website",
        ],
    ):
        return "portfolio"

    if _contains_any(
        searchable_text,
        [
            "postal code",
            "postcode",
            "zip code",
            "zipcode",
            "plz",
        ],
    ):
        return "postal_code"

    if _contains_any(
        searchable_text,
        [
            "street address",
            "address line",
            "anschrift",
            "straße",
            "strasse",
        ],
    ):
        return "address"

    if _contains_any(
        searchable_text,
        [
            "city",
            "town",
            "stadt",
            "ort",
        ],
    ):
        return "city"

    if _contains_any(
        searchable_text,
        [
            "country",
            "land",
        ],
    ):
        return "country"

    if _contains_any(
        searchable_text,
        [
            "current location",
            "location",
            "wohnort",
        ],
    ):
        return "location"

    if _contains_any(
        searchable_text,
        [
            "work authorization",
            "work authorisation",
            "authorized to work",
            "authorised to work",
            "work permit",
            "arbeitserlaubnis",
        ],
    ):
        return "work_authorization"

    if _contains_any(
        searchable_text,
        [
            "visa sponsorship",
            "visa sponsor",
            "sponsorship required",
            "require sponsorship",
            "need sponsorship",
        ],
    ):
        return "visa_sponsorship"

    if _contains_any(
        searchable_text,
        [
            "salary expectation",
            "salary expectations",
            "expected salary",
            "desired salary",
            "salary requirement",
            "compensation expectation",
            "gehaltsvorstellung",
            "gehaltswunsch",
        ],
    ):
        return "salary_expectation"

    if _contains_any(
        searchable_text,
        [
            "notice period",
            "kündigungsfrist",
            "kuendigungsfrist",
        ],
    ):
        return "notice_period"

    if _contains_any(
        searchable_text,
        [
            "available start",
            "available from",
            "availability date",
            "start date",
            "earliest start",
            "frühester eintritt",
            "fruehester eintritt",
        ],
    ):
        return "availability_date"

    if _contains_any(
        searchable_text,
        [
            "years of experience",
            "years experience",
            "years professional experience",
            "berufserfahrung in jahren",
        ],
    ):
        return "years_experience"

    if _contains_any(
        searchable_text,
        [
            "german level",
            "german language",
            "deutschkenntnisse",
            "deutsch niveau",
        ],
    ):
        return "german_level"

    if _contains_any(
        searchable_text,
        [
            "english level",
            "english language",
            "englischkenntnisse",
            "englisch niveau",
        ],
    ):
        return "english_level"

    if _contains_any(
        searchable_text,
        [
            "cover letter",
            "cover_letter",
            "motivation letter",
            "motivation",
            "anschreiben",
        ],
    ):
        return "cover_letter"

    return "unknown"


def _validate_job_url(
    job_url: str,
) -> str:
    normalized_url = job_url.strip()

    if not normalized_url:
        raise ValueError(
            "Job URL is required."
        )

    if not normalized_url.startswith(
        (
            "http://",
            "https://",
        )
    ):
        raise ValueError(
            "Job URL must start with http:// or https://"
        )

    return normalized_url


def _is_login_required(
    final_url: str,
    page_title: str,
) -> bool:
    normalized_url = final_url.lower()
    normalized_title = page_title.lower()

    return (
        "login" in normalized_url
        or "signin" in normalized_url
        or "sign-in" in normalized_url
        or "sign in" in normalized_title
        or "log in" in normalized_title
    )


def _detect_application_fields(
    page: Page,
) -> list[dict]:
    """
    Detect standard HTML form fields and classify them.
    """

    field_locator = page.locator(
        FORM_SELECTOR
    )

    detected_fields = field_locator.evaluate_all(
        """
        elements => elements.map((element, index) => {
            const tag = element.tagName.toLowerCase();

            const type =
                element.getAttribute("type")
                || tag;

            const id =
                element.getAttribute("id")
                || "";

            const name =
                element.getAttribute("name")
                || "";

            const placeholder =
                element.getAttribute("placeholder")
                || "";

            const ariaLabel =
                element.getAttribute("aria-label")
                || "";

            const autocomplete =
                element.getAttribute("autocomplete")
                || "";

            const value =
                element.getAttribute("value")
                || "";

            let label = "";

            if (id) {
                const labelElement =
                    document.querySelector(
                        `label[for="${CSS.escape(id)}"]`
                    );

                if (labelElement) {
                    label =
                        labelElement.innerText.trim();
                }
            }

            if (!label) {
                const parentLabel =
                    element.closest("label");

                if (parentLabel) {
                    label =
                        parentLabel.innerText.trim();
                }
            }

            if (!label) {
                const parent =
                    element.parentElement;

                if (parent) {
                    const nearbyLabel =
                        parent.querySelector("label");

                    if (nearbyLabel) {
                        label =
                            nearbyLabel.innerText.trim();
                    }
                }
            }

            if (!label) {
                label =
                    ariaLabel
                    || placeholder
                    || name
                    || id
                    || `Field ${index + 1}`;
            }

            const style =
                window.getComputedStyle(element);

            const visible = (
                type.toLowerCase() === "file"
                || (
                    style.display !== "none"
                    && style.visibility !== "hidden"
                    && element.getClientRects().length > 0
                )
            );

            let options = [];

            if (tag === "select") {
                options = Array.from(
                    element.options
                ).map(option => ({
                    value:
                        option.value || "",
                    text:
                        option.textContent.trim(),
                    disabled:
                        option.disabled === true,
                }));
            }

            return {
                index: index,
                tag: tag,
                type: type,
                id: id,
                name: name,
                label: label,
                placeholder: placeholder,
                autocomplete: autocomplete,
                value: value,
                required:
                    element.required === true,
                disabled:
                    element.disabled === true,
                visible: visible,
                multiple:
                    element.multiple === true,
                options: options,
            };
        })
        """
    )

    for field in detected_fields:
        field["field_key"] = (
            classify_application_field(
                field
            )
        )

    return detected_fields


def resolve_effective_field_key(
    field: dict,
    field_mapping_overrides: dict | None,
) -> str:
    """
    Resolve the final mapping for one detected field.
    """

    field_index = field.get(
        "index",
        -1,
    )

    overrides = (
        field_mapping_overrides
        or {}
    )

    override_key = (
        overrides.get(
            str(field_index)
        )
        or overrides.get(
            field_index
        )
    )

    if override_key == "__skip__":
        return "skip"

    if override_key == "__custom__":
        return "custom_answer"

    if override_key:
        return str(
            override_key
        )

    return str(
        field.get(
            "field_key",
            "unknown",
        )
    )


def _get_field_value(
    field_key: str,
    field_index: int,
    applicant_profile: dict,
    custom_answers: dict | None,
) -> str:
    if field_key == "custom_answer":
        answers = (
            custom_answers
            or {}
        )

        value = (
            answers.get(
                str(field_index)
            )
            or answers.get(
                field_index
            )
            or ""
        )

        return str(
            value
        ).strip()

    value = applicant_profile.get(
        field_key,
        "",
    )

    if value is None:
        return ""

    return str(
        value
    ).strip()


def _select_exact_option(
    locator,
    field: dict,
    value: str,
) -> bool:
    """
    Select an option only when there is an exact
    case-insensitive text or value match.
    """

    normalized_value = (
        value.strip().casefold()
    )

    if not normalized_value:
        return False

    for option in (
        field.get(
            "options",
            [],
        )
        or []
    ):
        if option.get(
            "disabled"
        ):
            continue

        option_value = str(
            option.get(
                "value",
                "",
            )
        )

        option_text = str(
            option.get(
                "text",
                "",
            )
        )

        if (
            option_value.strip().casefold()
            == normalized_value
        ):
            locator.select_option(
                value=option_value
            )
            return True

        if (
            option_text.strip().casefold()
            == normalized_value
        ):
            locator.select_option(
                label=option_text
            )
            return True

    return False


def fill_application_page(
    page: Page,
    applicant_profile: dict,
    resume_file: dict | str | None = None,
    field_mapping_overrides: dict | None = None,
    custom_answers: dict | None = None,
) -> list[dict]:
    """
    Fill supported fields on the already-open page.

    This never clicks navigation or submission buttons.
    Consent checkboxes and radio buttons are always left
    for manual review.
    """

    detected_fields = (
        _detect_application_fields(
            page
        )
    )

    all_fields = page.locator(
        FORM_SELECTOR
    )

    actions = []

    for field in detected_fields:
        field_index = int(
            field.get(
                "index",
                -1,
            )
        )

        field_label = field.get(
            "label",
            "Unnamed field",
        )

        field_key = (
            resolve_effective_field_key(
                field=field,
                field_mapping_overrides=(
                    field_mapping_overrides
                ),
            )
        )

        field_type = str(
            field.get(
                "type",
                "",
            )
        ).lower()

        field_tag = str(
            field.get(
                "tag",
                "",
            )
        ).lower()

        action = {
            "index": field_index,
            "label": field_label,
            "field_key": field_key,
            "type": field_type,
            "status": "skipped",
            "reason": "",
        }

        if field_index < 0:
            action["reason"] = (
                "Invalid field index."
            )
            actions.append(
                action
            )
            continue

        if field.get(
            "disabled"
        ):
            action["reason"] = (
                "Field is disabled."
            )
            actions.append(
                action
            )
            continue

        if (
            not field.get(
                "visible",
                True,
            )
            and field_type != "file"
        ):
            action["reason"] = (
                "Field is not visible."
            )
            actions.append(
                action
            )
            continue

        if field_key == "skip":
            action["reason"] = (
                "User chose not to fill this field."
            )
            actions.append(
                action
            )
            continue

        if field_key == "unknown":
            action["reason"] = (
                "Field needs manual review."
            )
            actions.append(
                action
            )
            continue

        locator = all_fields.nth(
            field_index
        )

        try:
            if field_key == "resume":
                if field_type != "file":
                    action["reason"] = (
                        "Resume mapping is not "
                        "a file input."
                    )

                elif not resume_file:
                    action["reason"] = (
                        "No resume was provided."
                    )

                else:
                    if isinstance(
                        resume_file,
                        str,
                    ):
                        locator.set_input_files(
                            resume_file,
                            timeout=10_000,
                        )

                    else:
                        locator.set_input_files(
                            files=[
                                resume_file
                            ],
                            timeout=10_000,
                        )

                    action["status"] = (
                        "filled"
                    )
                    action["reason"] = (
                        "Resume attached."
                    )

            elif field_type in (
                MANUAL_ONLY_INPUT_TYPES
            ):
                action["reason"] = (
                    "Checkboxes and radio buttons "
                    "require manual review."
                )

            elif field_type in (
                UNSAFE_INPUT_TYPES
            ):
                action["reason"] = (
                    "Unsafe or non-data input type."
                )

            else:
                field_value = (
                    _get_field_value(
                        field_key=field_key,
                        field_index=field_index,
                        applicant_profile=(
                            applicant_profile
                        ),
                        custom_answers=(
                            custom_answers
                        ),
                    )
                )

                if not field_value:
                    action["reason"] = (
                        "No value was supplied."
                    )

                elif field_tag == "select":
                    if _select_exact_option(
                        locator=locator,
                        field=field,
                        value=field_value,
                    ):
                        action["status"] = (
                            "filled"
                        )
                        action["reason"] = (
                            "Exact dropdown option selected."
                        )

                    else:
                        action["reason"] = (
                            "No exact dropdown option "
                            "matched the supplied value."
                        )

                elif (
                    field_tag == "textarea"
                    or field_type
                    in SAFE_TEXT_INPUT_TYPES
                ):
                    locator.fill(
                        field_value,
                        timeout=10_000,
                    )

                    action["status"] = (
                        "filled"
                    )
                    action["reason"] = (
                        "Value inserted."
                    )

                else:
                    action["reason"] = (
                        "Unsupported field type."
                    )

        except Exception as error:
            action["status"] = (
                "error"
            )
            action["reason"] = (
                f"{type(error).__name__}: "
                f"{error}"
            )

        actions.append(
            action
        )

    return actions


def _summarize_actions(
    actions: list[dict],
) -> dict:
    return {
        "filled_count": sum(
            1
            for action in actions
            if action.get(
                "status"
            )
            == "filled"
        ),
        "skipped_count": sum(
            1
            for action in actions
            if action.get(
                "status"
            )
            == "skipped"
        ),
        "error_count": sum(
            1
            for action in actions
            if action.get(
                "status"
            )
            == "error"
        ),
    }


def open_job_page(
    job_url: str,
) -> dict:
    """
    Open and inspect a job application page.

    The temporary browser is closed after inspection.
    No fields are modified.
    """

    normalized_url = (
        _validate_job_url(
            job_url
        )
    )

    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(
                headless=False,
            )
        )

        page = browser.new_page()

        try:
            page.goto(
                normalized_url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            final_url = page.url
            page_title = (
                page.title()
            )

            login_required = (
                _is_login_required(
                    final_url=final_url,
                    page_title=page_title,
                )
            )

            detected_fields = []
            page_text = ""

            if not login_required:
                detected_fields = (
                    _detect_application_fields(
                        page
                    )
                )

                try:
                    page_text = (
                        page.locator(
                            "body"
                        ).inner_text(
                            timeout=5_000
                        )
                    )[:20_000]

                except Exception:
                    page_text = ""

            return {
                "requested_url": (
                    normalized_url
                ),
                "url": final_url,
                "title": page_title,
                "login_required": (
                    login_required
                ),
                "fields": detected_fields,
                "field_count": len(
                    detected_fields
                ),
                "page_text": page_text,
            }

        finally:
            browser.close()


def preview_autofill_job_page(
    job_url: str,
    applicant_profile: dict,
    resume_file: dict | None = None,
    field_mapping_overrides: dict | None = None,
    custom_answers: dict | None = None,
) -> dict:
    """
    Fill supported fields in a temporary headless browser
    and return a screenshot plus an action report.

    The preview never submits the form.
    """

    normalized_url = (
        _validate_job_url(
            job_url
        )
    )

    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(
                headless=True,
            )
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )

        try:
            page.goto(
                normalized_url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            final_url = page.url
            page_title = (
                page.title()
            )

            login_required = (
                _is_login_required(
                    final_url=final_url,
                    page_title=page_title,
                )
            )

            if login_required:
                screenshot = (
                    page.screenshot(
                        full_page=True,
                    )
                )

                return {
                    "requested_url": (
                        normalized_url
                    ),
                    "url": final_url,
                    "title": page_title,
                    "login_required": True,
                    "actions": [],
                    "filled_count": 0,
                    "skipped_count": 0,
                    "error_count": 0,
                    "screenshot": screenshot,
                    "field_mapping_overrides": (
                        field_mapping_overrides
                        or {}
                    ),
                    "custom_answers": (
                        custom_answers
                        or {}
                    ),
                }

            actions = (
                fill_application_page(
                    page=page,
                    applicant_profile=(
                        applicant_profile
                    ),
                    resume_file=resume_file,
                    field_mapping_overrides=(
                        field_mapping_overrides
                    ),
                    custom_answers=(
                        custom_answers
                    ),
                )
            )

            try:
                screenshot = (
                    page.screenshot(
                        full_page=True,
                    )
                )

            except Exception:
                screenshot = (
                    page.screenshot()
                )

            summary = (
                _summarize_actions(
                    actions
                )
            )

            return {
                "requested_url": (
                    normalized_url
                ),
                "url": final_url,
                "title": page_title,
                "login_required": False,
                "actions": actions,
                "screenshot": screenshot,
                "field_mapping_overrides": (
                    field_mapping_overrides
                    or {}
                ),
                "custom_answers": (
                    custom_answers
                    or {}
                ),
                **summary,
            }

        finally:
            browser.close()


def _inject_review_banner(
    page: Page,
    filled_count: int,
    skipped_count: int,
    error_count: int,
) -> None:
    """
    Add a visible reminder to the headed review browser.
    """

    page.evaluate(
        """
        ({filledCount, skippedCount, errorCount}) => {
            const existing =
                document.getElementById(
                    "job-match-agent-review-banner"
                );

            if (existing) {
                existing.remove();
            }

            const banner =
                document.createElement("div");

            banner.id =
                "job-match-agent-review-banner";

            banner.textContent =
                `Job Match Agent review mode — `
                + `${filledCount} filled, `
                + `${skippedCount} skipped, `
                + `${errorCount} errors. `
                + `Review every answer before submitting manually.`;

            Object.assign(
                banner.style,
                {
                    position: "fixed",
                    top: "0",
                    left: "0",
                    right: "0",
                    zIndex: "2147483647",
                    background: "#111827",
                    color: "#ffffff",
                    padding: "12px 16px",
                    fontFamily: "Arial, sans-serif",
                    fontSize: "14px",
                    textAlign: "center",
                    boxShadow:
                        "0 2px 8px rgba(0,0,0,0.35)",
                }
            );

            document.body.appendChild(
                banner
            );
        }
        """,
        {
            "filledCount": filled_count,
            "skippedCount": skipped_count,
            "errorCount": error_count,
        },
    )


def open_filled_application_for_review(
    job_url: str,
    applicant_profile: dict,
    resume_path: str | None = None,
    field_mapping_overrides: dict | None = None,
    custom_answers: dict | None = None,
) -> dict:
    """
    Open a visible browser, fill supported fields,
    and leave the browser open for manual review.

    The function never clicks a submit/apply/continue button.
    The user must review and submit manually.
    """

    normalized_url = (
        _validate_job_url(
            job_url
        )
    )

    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(
                headless=False,
            )
        )

        page = browser.new_page()

        page.goto(
            normalized_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        final_url = page.url
        page_title = page.title()

        login_required = (
            _is_login_required(
                final_url=final_url,
                page_title=page_title,
            )
        )

        actions = []

        if not login_required:
            actions = (
                fill_application_page(
                    page=page,
                    applicant_profile=(
                        applicant_profile
                    ),
                    resume_file=(
                        resume_path
                    ),
                    field_mapping_overrides=(
                        field_mapping_overrides
                    ),
                    custom_answers=(
                        custom_answers
                    ),
                )
            )

        summary = (
            _summarize_actions(
                actions
            )
        )

        try:
            _inject_review_banner(
                page=page,
                filled_count=(
                    summary[
                        "filled_count"
                    ]
                ),
                skipped_count=(
                    summary[
                        "skipped_count"
                    ]
                ),
                error_count=(
                    summary[
                        "error_count"
                    ]
                ),
            )

        except Exception:
            pass

        result = {
            "requested_url": (
                normalized_url
            ),
            "url": final_url,
            "title": page_title,
            "login_required": (
                login_required
            ),
            "actions": actions,
            **summary,
        }

        print(
            "Application Agent review browser opened."
        )
        print(
            result
        )
        print(
            "Close the browser window when finished."
        )

        try:
            while browser.is_connected():
                page.wait_for_timeout(
                    1000
                )

        except Exception:
            pass

        finally:
            try:
                browser.close()

            except Exception:
                pass

        return result
