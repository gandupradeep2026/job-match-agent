import html
import json
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from market_intelligence.providers.base import (
    JobSourceProvider,
    ProviderJob,
)


class _HTMLTextExtractor(HTMLParser):
    """
    Convert small HTML fragments into plain text.
    """

    def __init__(self):
        super().__init__()
        self.parts: List[str] = []

    def handle_data(
        self,
        data: str,
    ) -> None:

        cleaned = (
            data or ""
        ).strip()

        if cleaned:
            self.parts.append(
                cleaned
            )

    def get_text(self) -> str:
        return "\n".join(
            self.parts
        )


def _html_to_text(
    value: str,
) -> str:

    if not value:
        return ""

    decoded = html.unescape(
        value
    )

    parser = _HTMLTextExtractor()

    try:
        parser.feed(
            decoded
        )
        parser.close()

        return parser.get_text()

    except Exception:
        return decoded.strip()


class LeverProvider(
    JobSourceProvider
):
    """
    Fetch published jobs from one Lever careers site.

    Lever supports:

        global:
            https://api.lever.co

        EU:
            https://api.eu.lever.co

    Each company has a Lever site identifier.
    """

    GLOBAL_BASE_URL = (
        "https://api.lever.co"
    )

    EU_BASE_URL = (
        "https://api.eu.lever.co"
    )

    COUNTRY_CODES = {
        "DE": "Germany",
        "AT": "Austria",
        "CH": "Switzerland",
        "FR": "France",
        "IT": "Italy",
        "ES": "Spain",
        "NL": "Netherlands",
        "BE": "Belgium",
        "PL": "Poland",
        "SE": "Sweden",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "IE": "Ireland",
        "GB": "United Kingdom",
        "UK": "United Kingdom",
        "US": "United States",
        "CA": "Canada",
        "AU": "Australia",
        "NZ": "New Zealand",
        "IN": "India",
        "SG": "Singapore",
    }

    def __init__(
        self,
        site: str,
        company_name: str = "",
        instance: str = "global",
        page_size: int = 100,
        fetch_json: Optional[
            Callable[[str], List[Dict]]
        ] = None,
    ):
        cleaned_site = (
            site or ""
        ).strip()

        if not cleaned_site:
            raise ValueError(
                "Lever site is required."
            )

        cleaned_instance = (
            instance
            or "global"
        ).strip().lower()

        if cleaned_instance not in {
            "global",
            "eu",
        }:
            raise ValueError(
                "Lever instance must be "
                "'global' or 'eu'."
            )

        if page_size <= 0:
            raise ValueError(
                "page_size must be greater than zero."
            )

        self.site = cleaned_site
        self.company_name = (
            company_name or ""
        ).strip()

        self.instance = (
            cleaned_instance
        )

        self.page_size = (
            page_size
        )

        self._fetch_json_override = (
            fetch_json
        )

    @property
    def provider_name(
        self,
    ) -> str:
        return "Lever"

    # ======================================================
    # BASE URL
    # ======================================================
    @property
    def base_url(
        self,
    ) -> str:

        if self.instance == "eu":
            return self.EU_BASE_URL

        return self.GLOBAL_BASE_URL

    # ======================================================
    # HTTP
    # ======================================================
    @staticmethod
    def _default_fetch_json(
        url: str,
    ) -> List[Dict]:

        request = Request(
            url,
            headers={
                "Accept": (
                    "application/json"
                ),
                "User-Agent": (
                    "JobMatchAgent/1.0"
                ),
            },
        )

        with urlopen(
            request,
            timeout=30,
        ) as response:

            raw = response.read()

        decoded = raw.decode(
            "utf-8"
        )

        data = json.loads(
            decoded
        )

        if not isinstance(
            data,
            list,
        ):
            raise ValueError(
                "Unexpected Lever API response."
            )

        return data

    def _fetch_json(
        self,
        url: str,
    ) -> List[Dict]:

        if (
            self._fetch_json_override
            is not None
        ):
            return (
                self._fetch_json_override(
                    url
                )
            )

        return (
            self._default_fetch_json(
                url
            )
        )

    # ======================================================
    # URL
    # ======================================================
    def _jobs_url(
        self,
        skip: int,
    ) -> str:

        site = quote(
            self.site,
            safe="",
        )

        query = urlencode(
            {
                "mode": "json",
                "skip": skip,
                "limit": (
                    self.page_size
                ),
            }
        )

        return (
            f"{self.base_url}"
            f"/v0/postings/"
            f"{site}"
            f"?{query}"
        )

    # ======================================================
    # COMPANY
    # ======================================================
    def _resolve_company_name(
        self,
    ) -> str:

        if self.company_name:
            return self.company_name

        return self.site

    # ======================================================
    # COUNTRY
    # ======================================================
    @classmethod
    def _country_name(
        cls,
        country_code: str,
    ) -> str:

        code = (
            country_code or ""
        ).strip().upper()

        return cls.COUNTRY_CODES.get(
            code,
            code,
        )

    # ======================================================
    # DESCRIPTION
    # ======================================================
    @staticmethod
    def _build_description(
        raw_job: Dict,
    ) -> str:

        parts = []

        description_plain = (
            raw_job.get(
                "descriptionPlain",
                "",
            )
            or ""
        ).strip()

        if description_plain:
            parts.append(
                description_plain
            )

        else:
            description_html = (
                raw_job.get(
                    "description",
                    "",
                )
                or ""
            )

            cleaned = (
                _html_to_text(
                    description_html
                )
            )

            if cleaned:
                parts.append(
                    cleaned
                )

        lists = (
            raw_job.get(
                "lists",
                [],
            )
            or []
        )

        for item in lists:

            heading = (
                item.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            content = (
                item.get(
                    "content",
                    "",
                )
                or ""
            )

            cleaned_content = (
                _html_to_text(
                    content
                )
            )

            if heading:
                parts.append(
                    heading
                )

            if cleaned_content:
                parts.append(
                    cleaned_content
                )

        additional_plain = (
            raw_job.get(
                "additionalPlain",
                "",
            )
            or ""
        ).strip()

        if additional_plain:
            parts.append(
                additional_plain
            )

        elif raw_job.get(
            "additional"
        ):
            cleaned_additional = (
                _html_to_text(
                    raw_job.get(
                        "additional",
                        "",
                    )
                )
            )

            if cleaned_additional:
                parts.append(
                    cleaned_additional
                )

        return "\n\n".join(
            part
            for part in parts
            if part.strip()
        )

    # ======================================================
    # FETCH
    # ======================================================
    def fetch_jobs(
        self,
    ) -> List[ProviderJob]:

        company = (
            self._resolve_company_name()
        )

        results = []

        skip = 0

        while True:

            page = self._fetch_json(
                self._jobs_url(
                    skip=skip
                )
            )

            if not page:
                break

            for raw_job in page:

                title = (
                    raw_job.get(
                        "text",
                        "",
                    )
                    or ""
                ).strip()

                if not title:
                    continue

                categories = (
                    raw_job.get(
                        "categories",
                        {},
                    )
                    or {}
                )

                location = (
                    categories.get(
                        "location",
                        "",
                    )
                    or ""
                ).strip()

                country = (
                    self._country_name(
                        raw_job.get(
                            "country",
                            "",
                        )
                    )
                )

                description = (
                    self._build_description(
                        raw_job
                    )
                )

                source_url = (
                    raw_job.get(
                        "hostedUrl",
                        "",
                    )
                    or ""
                ).strip()

                external_id = str(
                    raw_job.get(
                        "id",
                        "",
                    )
                    or ""
                ).strip()

                results.append(
                    ProviderJob(
                        job_title=title,
                        company=company,
                        location=location,
                        country=country,
                        description=(
                            description
                        ),
                        source="Lever",
                        source_url=(
                            source_url
                        ),
                        # Lever's documented public
                        # postings schema does not expose
                        # a reliable original posted date.
                        posted_date=None,
                        external_id=(
                            external_id
                        ),
                    )
                )

            if len(page) < self.page_size:
                break

            skip += (
                self.page_size
            )

        return results
