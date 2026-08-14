from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.market_refresh import (
    MarketRefreshResult,
    MarketRefreshService,
)


@dataclass
class RefreshExecutionResult:
    refresh_result: MarketRefreshResult
    snapshot_id: int


class MarketRefreshRunner:
    """
    Execute a complete production market refresh.

    One execution performs:

        1. Refresh all enabled external job sources.
        2. Add new matching jobs to job_market.db.
        3. Protect existing jobs from duplicates.
        4. Save a persistent historical snapshot.
        5. Return refresh and snapshot information.

    This runner can be reused by:

        - Streamlit
        - command-line scripts
        - Windows Task Scheduler
        - future cloud deployments
    """

    def __init__(
        self,
        market_database: Optional[
            JobMarketDatabase
        ] = None,
        history_database: Optional[
            MarketRefreshHistory
        ] = None,
        config_path: str = (
            "config/job_sources.json"
        ),
    ):
        self.market_database = (
            market_database
            if market_database is not None
            else JobMarketDatabase()
        )

        self.history_database = (
            history_database
            if history_database is not None
            else MarketRefreshHistory()
        )

        self.refresh_service = (
            MarketRefreshService(
                database=self.market_database,
                config_path=config_path,
            )
        )

    def run(
        self,
    ) -> RefreshExecutionResult:
        """
        Run refresh and save one historical snapshot.
        """

        refresh_result = (
            self.refresh_service.refresh()
        )

        collection_filter = (
            self.refresh_service
            .registry
            .load_collection_filter()
        )

        snapshot_id = (
            self.history_database
            .record_refresh(
                result=refresh_result,
                market_database=(
                    self.market_database
                ),
                collection_filter=(
                    collection_filter
                ),
            )
        )

        return RefreshExecutionResult(
            refresh_result=(
                refresh_result
            ),
            snapshot_id=(
                snapshot_id
            ),
        )
