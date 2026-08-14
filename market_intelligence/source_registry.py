import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from market_intelligence.collection_filter import (
    MarketCollectionFilter,
)
from market_intelligence.providers.base import (
    JobSourceProvider,
)
from market_intelligence.providers.greenhouse import (
    GreenhouseProvider,
)
from market_intelligence.providers.lever import (
    LeverProvider,
)


@dataclass
class JobSourceConfig:
    provider: str

    company: str = ""

    board: str = ""
    site: str = ""

    instance: str = "global"

    enabled: bool = True


class JobSourceRegistry:
    """
    Load external job sources and global collection
    filters from config/job_sources.json.
    """

    SUPPORTED_PROVIDERS = {
        "greenhouse",
        "lever",
    }

    def __init__(
        self,
        config_path: str | Path = (
            "config/job_sources.json"
        ),
    ):
        self.config_path = Path(
            config_path
        )

    # ======================================================
    # RAW CONFIG
    # ======================================================
    def _load_raw_config(
        self,
    ) -> dict:

        if not self.config_path.exists():
            raise FileNotFoundError(
                "Job source configuration "
                f"not found: {self.config_path}"
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            config = json.load(
                file
            )

        if not isinstance(
            config,
            dict,
        ):
            raise ValueError(
                "Job source configuration "
                "must be a JSON object."
            )

        return config

    # ======================================================
    # FILTER
    # ======================================================
    def load_collection_filter(
        self,
    ) -> MarketCollectionFilter:

        raw_config = (
            self._load_raw_config()
        )

        raw_filter = (
            raw_config.get(
                "filters",
                {},
            )
            or {}
        )

        if not isinstance(
            raw_filter,
            dict,
        ):
            raise ValueError(
                "'filters' must be an object."
            )

        def clean_list(
            name: str,
        ) -> List[str]:

            values = (
                raw_filter.get(
                    name,
                    [],
                )
                or []
            )

            if not isinstance(
                values,
                list,
            ):
                raise ValueError(
                    f"Filter '{name}' "
                    "must be a list."
                )

            return [
                str(value).strip()
                for value in values
                if str(value).strip()
            ]

        return MarketCollectionFilter(
            allowed_countries=(
                clean_list(
                    "countries"
                )
            ),
            allowed_job_families=(
                clean_list(
                    "job_families"
                )
            ),
            title_keywords=(
                clean_list(
                    "title_keywords"
                )
            ),
            excluded_title_keywords=(
                clean_list(
                    "excluded_title_keywords"
                )
            ),
        )

    # ======================================================
    # SOURCES
    # ======================================================
    def load_sources(
        self,
    ) -> List[JobSourceConfig]:

        raw_config = (
            self._load_raw_config()
        )

        raw_sources = raw_config.get(
            "sources",
            [],
        )

        if not isinstance(
            raw_sources,
            list,
        ):
            raise ValueError(
                "'sources' must be a list."
            )

        sources = []

        for index, raw_source in enumerate(
            raw_sources,
            start=1,
        ):

            if not isinstance(
                raw_source,
                dict,
            ):
                raise ValueError(
                    f"Source #{index} "
                    "must be an object."
                )

            provider = (
                str(
                    raw_source.get(
                        "provider",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            if not provider:
                raise ValueError(
                    f"Source #{index} "
                    "has no provider."
                )

            if provider not in (
                self.SUPPORTED_PROVIDERS
            ):
                raise ValueError(
                    f"Unsupported provider "
                    f"'{provider}'."
                )

            source = JobSourceConfig(
                provider=provider,

                company=str(
                    raw_source.get(
                        "company",
                        "",
                    )
                    or ""
                ).strip(),

                board=str(
                    raw_source.get(
                        "board",
                        "",
                    )
                    or ""
                ).strip(),

                site=str(
                    raw_source.get(
                        "site",
                        "",
                    )
                    or ""
                ).strip(),

                instance=str(
                    raw_source.get(
                        "instance",
                        "global",
                    )
                    or "global"
                ).strip().lower(),

                enabled=bool(
                    raw_source.get(
                        "enabled",
                        True,
                    )
                ),
            )

            self._validate_source(
                source
            )

            sources.append(
                source
            )

        return sources

    @staticmethod
    def _validate_source(
        source: JobSourceConfig,
    ) -> None:

        if source.provider == "greenhouse":

            if not source.board:
                raise ValueError(
                    "Greenhouse source "
                    "requires 'board'."
                )

        elif source.provider == "lever":

            if not source.site:
                raise ValueError(
                    "Lever source "
                    "requires 'site'."
                )

            if source.instance not in {
                "global",
                "eu",
            }:
                raise ValueError(
                    "Lever instance must be "
                    "'global' or 'eu'."
                )

    def enabled_sources(
        self,
    ) -> List[JobSourceConfig]:

        return [
            source
            for source in self.load_sources()
            if source.enabled
        ]

    @staticmethod
    def build_provider(
        source: JobSourceConfig,
    ) -> JobSourceProvider:

        if source.provider == "greenhouse":

            return GreenhouseProvider(
                board_token=(
                    source.board
                ),
                company_name=(
                    source.company
                ),
            )

        if source.provider == "lever":

            return LeverProvider(
                site=(
                    source.site
                ),
                company_name=(
                    source.company
                ),
                instance=(
                    source.instance
                ),
            )

        raise ValueError(
            "Unsupported provider: "
            f"{source.provider}"
        )