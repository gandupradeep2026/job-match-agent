from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.source_registry import (
    JobSourceRegistry,
)


@dataclass
class HealthCheck:
    name: str
    status: str
    message: str

    value: str = ""


@dataclass
class SystemHealthReport:
    overall_status: str

    production_jobs: int
    companies: int
    enabled_sources: int
    snapshots: int

    latest_refresh_at: str = ""

    checks: List[
        HealthCheck
    ] = field(
        default_factory=list
    )


class MarketSystemHealthService:
    """
    Production health checks for Job Market Intelligence.

    Checks:

        - production database
        - employer diversity
        - configured job sources
        - refresh history
        - refresh age
        - source-level failures
        - individual failed job records
    """

    STATUS_HEALTHY = "HEALTHY"
    STATUS_WARNING = "WARNING"
    STATUS_CRITICAL = "CRITICAL"

    def __init__(
        self,
        database: Optional[
            JobMarketDatabase
        ] = None,
        history: Optional[
            MarketRefreshHistory
        ] = None,
        registry: Optional[
            JobSourceRegistry
        ] = None,
        max_refresh_age_hours: int = 48,
    ):
        self.database = (
            database
            if database is not None
            else JobMarketDatabase()
        )

        self.history = (
            history
            if history is not None
            else MarketRefreshHistory()
        )

        self.registry = (
            registry
            if registry is not None
            else JobSourceRegistry()
        )

        self.max_refresh_age_hours = (
            max_refresh_age_hours
        )

    # ======================================================
    # TIME
    # ======================================================

    @staticmethod
    def _parse_datetime(
        value: str,
    ) -> Optional[datetime]:

        if not value:
            return None

        try:

            parsed = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed

        except ValueError:
            return None

    @classmethod
    def _hours_since(
        cls,
        value: str,
    ) -> Optional[float]:

        parsed = cls._parse_datetime(
            value
        )

        if parsed is None:
            return None

        now = datetime.now(
            timezone.utc
        )

        difference = (
            now
            - parsed.astimezone(
                timezone.utc
            )
        )

        return (
            difference.total_seconds()
            / 3600
        )

    # ======================================================
    # STATUS
    # ======================================================

    @classmethod
    def _overall_status(
        cls,
        checks: List[
            HealthCheck
        ],
    ) -> str:

        statuses = {
            check.status
            for check in checks
        }

        if (
            cls.STATUS_CRITICAL
            in statuses
        ):
            return cls.STATUS_CRITICAL

        if (
            cls.STATUS_WARNING
            in statuses
        ):
            return cls.STATUS_WARNING

        return cls.STATUS_HEALTHY

    # ======================================================
    # REPORT
    # ======================================================

    def evaluate(
        self,
    ) -> SystemHealthReport:

        checks = []

        jobs = (
            self.database.get_all_jobs()
        )

        production_jobs = len(
            jobs
        )

        companies = len(
            {
                (
                    job.company
                    or ""
                ).strip()
                for job in jobs
                if (
                    job.company
                    or ""
                ).strip()
            }
        )

        # ==================================================
        # DATABASE
        # ==================================================

        if production_jobs <= 0:

            checks.append(
                HealthCheck(
                    name=(
                        "Production database"
                    ),
                    status=(
                        self.STATUS_CRITICAL
                    ),
                    message=(
                        "Production market database "
                        "contains no jobs."
                    ),
                    value="0 jobs",
                )
            )

        else:

            checks.append(
                HealthCheck(
                    name=(
                        "Production database"
                    ),
                    status=(
                        self.STATUS_HEALTHY
                    ),
                    message=(
                        "Production database "
                        "contains market jobs."
                    ),
                    value=(
                        f"{production_jobs} jobs"
                    ),
                )
            )

        # ==================================================
        # COMPANY DIVERSITY
        # ==================================================

        if companies < 5:

            company_status = (
                self.STATUS_WARNING
            )

            company_message = (
                "Market dataset contains jobs "
                "from very few employers."
            )

        else:

            company_status = (
                self.STATUS_HEALTHY
            )

            company_message = (
                "Employer diversity is available "
                "in the current market sample."
            )

        checks.append(
            HealthCheck(
                name="Employer diversity",
                status=company_status,
                message=company_message,
                value=(
                    f"{companies} companies"
                ),
            )
        )

        # ==================================================
        # SOURCES
        # ==================================================

        try:

            sources = (
                self.registry
                .enabled_sources()
            )

            enabled_sources = len(
                sources
            )

        except Exception as error:

            enabled_sources = 0

            checks.append(
                HealthCheck(
                    name=(
                        "Source configuration"
                    ),
                    status=(
                        self.STATUS_CRITICAL
                    ),
                    message=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                )
            )

        else:

            if enabled_sources <= 0:

                checks.append(
                    HealthCheck(
                        name=(
                            "Source configuration"
                        ),
                        status=(
                            self.STATUS_CRITICAL
                        ),
                        message=(
                            "No enabled external "
                            "job sources exist."
                        ),
                        value="0 sources",
                    )
                )

            else:

                checks.append(
                    HealthCheck(
                        name=(
                            "Source configuration"
                        ),
                        status=(
                            self.STATUS_HEALTHY
                        ),
                        message=(
                            "External job sources "
                            "are configured."
                        ),
                        value=(
                            f"{enabled_sources} sources"
                        ),
                    )
                )

        # ==================================================
        # SNAPSHOTS
        # ==================================================

        snapshots = (
            self.history
            .count_refreshes()
        )

        if snapshots <= 0:

            checks.append(
                HealthCheck(
                    name="Market history",
                    status=(
                        self.STATUS_WARNING
                    ),
                    message=(
                        "No historical market "
                        "snapshots exist yet."
                    ),
                    value="0 snapshots",
                )
            )

        else:

            checks.append(
                HealthCheck(
                    name="Market history",
                    status=(
                        self.STATUS_HEALTHY
                    ),
                    message=(
                        "Persistent market "
                        "history is available."
                    ),
                    value=(
                        f"{snapshots} snapshots"
                    ),
                )
            )

        # ==================================================
        # LATEST REFRESH
        # ==================================================

        latest = (
            self.history.latest_refresh()
        )

        latest_refresh_at = ""

        if latest is None:

            checks.append(
                HealthCheck(
                    name="Latest refresh",
                    status=(
                        self.STATUS_WARNING
                    ),
                    message=(
                        "No refresh execution "
                        "has been recorded."
                    ),
                )
            )

        else:

            latest_refresh_at = (
                latest.get(
                    "completed_at",
                    "",
                )
                or ""
            )

            age_hours = (
                self._hours_since(
                    latest_refresh_at
                )
            )

            if age_hours is None:

                checks.append(
                    HealthCheck(
                        name="Latest refresh",
                        status=(
                            self.STATUS_WARNING
                        ),
                        message=(
                            "Latest refresh timestamp "
                            "could not be interpreted."
                        ),
                    )
                )

            elif (
                age_hours
                > self.max_refresh_age_hours
            ):

                checks.append(
                    HealthCheck(
                        name="Latest refresh",
                        status=(
                            self.STATUS_WARNING
                        ),
                        message=(
                            "Market data may be stale. "
                            "The latest refresh is older "
                            f"than {self.max_refresh_age_hours} "
                            "hours."
                        ),
                        value=(
                            f"{age_hours:.1f} hours ago"
                        ),
                    )
                )

            else:

                checks.append(
                    HealthCheck(
                        name="Latest refresh",
                        status=(
                            self.STATUS_HEALTHY
                        ),
                        message=(
                            "Market data was refreshed "
                            "recently."
                        ),
                        value=(
                            f"{age_hours:.1f} hours ago"
                        ),
                    )
                )

            # ==============================================
            # SOURCE ERRORS
            # ==============================================

            source_errors = int(
                latest.get(
                    "source_errors",
                    0,
                )
                or 0
            )

            if source_errors:

                checks.append(
                    HealthCheck(
                        name="Source health",
                        status=(
                            self.STATUS_WARNING
                        ),
                        message=(
                            f"{source_errors} source(s) "
                            "failed during the latest refresh."
                        ),
                        value=(
                            f"{source_errors} errors"
                        ),
                    )
                )

            else:

                checks.append(
                    HealthCheck(
                        name="Source health",
                        status=(
                            self.STATUS_HEALTHY
                        ),
                        message=(
                            "All configured sources "
                            "completed without "
                            "source-level errors."
                        ),
                        value="0 errors",
                    )
                )

            # ==============================================
            # INDIVIDUAL JOB FAILURES
            # ==============================================

            failed_jobs = int(
                latest.get(
                    "failed_jobs",
                    0,
                )
                or 0
            )

            if failed_jobs:

                checks.append(
                    HealthCheck(
                        name="Job processing",
                        status=(
                            self.STATUS_WARNING
                        ),
                        message=(
                            f"{failed_jobs} individual "
                            "job record(s) could not be "
                            "processed during the latest "
                            "refresh."
                        ),
                        value=(
                            f"{failed_jobs} skipped"
                        ),
                    )
                )

            else:

                checks.append(
                    HealthCheck(
                        name="Job processing",
                        status=(
                            self.STATUS_HEALTHY
                        ),
                        message=(
                            "No individual job records "
                            "failed during the latest "
                            "refresh."
                        ),
                        value="0 skipped",
                    )
                )

        return SystemHealthReport(
            overall_status=(
                self._overall_status(
                    checks
                )
            ),

            production_jobs=(
                production_jobs
            ),

            companies=companies,

            enabled_sources=(
                enabled_sources
            ),

            snapshots=snapshots,

            latest_refresh_at=(
                latest_refresh_at
            ),

            checks=checks,
        )
