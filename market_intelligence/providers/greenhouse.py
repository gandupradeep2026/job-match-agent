import html
import json
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen

from market_intelligence.providers.base import (
    JobSourceProvider,
    ProviderJob,
)


class _HTMLTextExtractor(HTMLParser):
    """
    Convert a small HTML fragment into readable text.
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
    """
    Greenhouse job content may contain encoded HTML.

    Decode HTML entities first and then remove tags.
    """

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


class GreenhouseProvider(
    JobSourceProvider
):
    """
    Fetch published jobs from one Greenhouse job board.

    Greenhouse boards are addressed using their board token.

    Example conceptual career URL:

        boards.greenhouse.io/companyname

    where:

        companyname

    is commonly the board token.

    A company name may optionally be supplied manually.
    Otherwise this provider attempts to read the board name.
    """

    BASE_URL = (
        "https://boards-api.greenhouse.io"
        "/v1/boards"
    )

    def __init__(
        self,
        board_token: str,
        company_name: str = "",
        fetch_json: Optional[
            Callable[[str], Dict]
        ] = None,
    ):
        cleaned_token = (
            board_token or ""
        ).strip()

        if not cleaned_token:
            raise ValueError(
                "Greenhouse board token "
                "is required."
            )

        self.board_token = (
            cleaned_token
        )

        self.company_name = (
            company_name or ""
        ).strip()

        self._fetch_json_override = (
            fetch_json
        )

    @property
    def provider_name(
        self,
    ) -> str:
        return "Greenhouse"

    # ======================================================
    # HTTP
    # ======================================================
    @staticmethod
    def _default_fetch_json(
        url: str,
    ) -> Dict:

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

        return json.loads(
            decoded
        )

    def _fetch_json(
        self,
        url: str,
    ) -> Dict:

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
    # URLS
    # ======================================================
    def _board_url(
        self,
    ) -> str:

        token = quote(
            self.board_token,
            safe="",
        )

        return (
            f"{self.BASE_URL}/"
            f"{token}"
        )

    def _jobs_url(
        self,
    ) -> str:

        return (
            self._board_url()
            + "/jobs?content=true"
        )

    # ======================================================
    # COMPANY
    # ======================================================
    def _resolve_company_name(
        self,
    ) -> str:

        if self.company_name:
            return self.company_name

        try:
            data = self._fetch_json(
                self._board_url()
            )

            name = (
                data.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if name:
                self.company_name = (
                    name
                )

                return name

        except Exception:
            pass

        return self.board_token

    # ======================================================
    # LOCATION
    # ======================================================
    @staticmethod
    def _extract_location(
        job: Dict,
    ) -> str:

        location = (
            job.get(
                "location",
                {},
            )
            or {}
        )

        name = (
            location.get(
                "name",
                "",
            )
            or ""
        ).strip()

        if name:
            return name

        offices = (
            job.get(
                "offices",
                [],
            )
            or []
        )

        for office in offices:

            office_location = (
                office.get(
                    "location",
                    "",
                )
                or ""
            ).strip()

            if office_location:
                return (
                    office_location
                )

            office_name = (
                office.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if office_name:
                return office_name

        return ""

    @staticmethod
    def _infer_country(
        location: str,
    ) -> str:
        """
        Conservative country inference.

        We only assign a country when the location text
        explicitly contains a recognized country name.
        """

        normalized = (
            location or ""
        ).lower()

        country_patterns = {
            "germany": "Germany",
            "deutschland": "Germany",
            "austria": "Austria",
            "österreich": "Austria",
            "switzerland": "Switzerland",
            "schweiz": "Switzerland",
            "united kingdom": (
                "United Kingdom"
            ),
            "uk": "United Kingdom",
            "united states": (
                "United States"
            ),
            "usa": "United States",
            "canada": "Canada",
            "india": "India",
            "france": "France",
            "spain": "Spain",
            "italy": "Italy",
            "netherlands": (
                "Netherlands"
            ),
            "belgium": "Belgium",
            "sweden": "Sweden",
            "norway": "Norway",
            "denmark": "Denmark",
            "finland": "Finland",
            "poland": "Poland",
            "ireland": "Ireland",
        }

        for pattern, country in (
            country_patterns.items()
        ):
            if pattern in normalized:
                return country

        return ""

    # ======================================================
    # FETCH
    # ======================================================
    def fetch_jobs(
        self,
    ) -> List[ProviderJob]:

        company = (
            self._resolve_company_name()
        )

        data = self._fetch_json(
            self._jobs_url()
        )

        raw_jobs = (
            data.get(
                "jobs",
                [],
            )
            or []
        )

        results = []

        for raw_job in raw_jobs:

            title = (
                raw_job.get(
                    "title",
                    "",
                )
                or ""
            ).strip()

            if not title:
                continue

            content = (
                raw_job.get(
                    "content",
                    "",
                )
                or ""
            )

            description = (
                _html_to_text(
                    content
                )
            )

            location = (
                self._extract_location(
                    raw_job
                )
            )

            country = (
                self._infer_country(
                    location
                )
            )

            absolute_url = (
                raw_job.get(
                    "absolute_url",
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
                    description=description,
                    source=(
                        "Greenhouse"
                    ),
                    source_url=(
                        absolute_url
                    ),
                    # Greenhouse exposes updated_at,
                    # but that is not necessarily the
                    # original publication date.
                    # We therefore do not pretend it
                    # is posted_date.
                    posted_date=None,
                    external_id=(
                        external_id
                    ),
                )
            )

        return results
