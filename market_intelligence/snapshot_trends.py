from dataclasses import dataclass
from typing import List, Optional

from market_intelligence.market_history import (
    MarketRefreshHistory,
)


@dataclass
class SnapshotSkillPoint:
    refresh_run_id: int
    completed_at: str

    snapshot_jobs: int
    companies_count: int

    skill: str
    job_count: int
    demand_percentage: float


@dataclass
class SnapshotSkillChange:
    skill: str

    earlier_run_id: int
    later_run_id: int

    earlier_percentage: float
    later_percentage: float

    percentage_point_change: float

    earlier_job_count: int
    later_job_count: int

    trend: str


@dataclass
class MarketSnapshotChange:
    earlier_run_id: int
    later_run_id: int

    earlier_jobs: int
    later_jobs: int

    job_change: int
    job_change_percentage: Optional[float]

    earlier_companies: int
    later_companies: int

    company_change: int


class SnapshotTrendAnalyzer:
    """
    Analyze Job Market Intelligence using persistent
    refresh snapshots.

    This replaces dependence on provider posted_date.

    Example:

        Snapshot #1
            Python demand = 68%

        Snapshot #5
            Python demand = 74%

        Change:
            +6 percentage points
    """

    RISING_THRESHOLD = 2.0
    FALLING_THRESHOLD = -2.0

    def __init__(
        self,
        history: Optional[
            MarketRefreshHistory
        ] = None,
    ):
        self.history = (
            history
            if history is not None
            else MarketRefreshHistory()
        )

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _trend_label(
        change: float,
    ) -> str:

        if (
            change
            >= SnapshotTrendAnalyzer
            .RISING_THRESHOLD
        ):
            return "RISING"

        if (
            change
            <= SnapshotTrendAnalyzer
            .FALLING_THRESHOLD
        ):
            return "FALLING"

        return "STABLE"

    # ======================================================
    # SNAPSHOTS
    # ======================================================

    def snapshots(
        self,
        limit: int = 100,
    ) -> List[dict]:
        """
        Return snapshots in chronological order.
        """

        rows = (
            self.history.recent_refreshes(
                limit=limit
            )
        )

        return list(
            reversed(
                rows
            )
        )

    def snapshot(
        self,
        refresh_run_id: int,
    ) -> Optional[dict]:

        for row in self.snapshots():

            if (
                row["id"]
                == refresh_run_id
            ):
                return row

        return None

    # ======================================================
    # SKILL DEMAND
    # ======================================================

    def skill_trend(
        self,
        skill: str,
    ) -> List[SnapshotSkillPoint]:
        """
        Return demand for one skill for every snapshot.

        A skill absent from a snapshot receives:

            count = 0
            demand = 0%

        This is important because disappearance of a skill
        is itself meaningful trend information.
        """

        snapshots = self.snapshots()

        history_rows = (
            self.history.skill_history(
                skill
            )
        )

        history_map = {
            row["refresh_run_id"]: row
            for row in history_rows
        }

        points = []

        for snapshot in snapshots:

            run_id = snapshot["id"]

            skill_row = (
                history_map.get(
                    run_id
                )
            )

            if skill_row:

                job_count = (
                    skill_row[
                        "job_count"
                    ]
                )

                percentage = (
                    skill_row[
                        "demand_percentage"
                    ]
                )

            else:

                job_count = 0
                percentage = 0.0

            points.append(
                SnapshotSkillPoint(
                    refresh_run_id=(
                        run_id
                    ),
                    completed_at=(
                        snapshot[
                            "completed_at"
                        ]
                    ),
                    snapshot_jobs=(
                        snapshot[
                            "snapshot_jobs"
                        ]
                    ),
                    companies_count=(
                        snapshot[
                            "companies_count"
                        ]
                    ),
                    skill=skill,
                    job_count=job_count,
                    demand_percentage=(
                        percentage
                    ),
                )
            )

        return points

    # ======================================================
    # SKILL COMPARISON
    # ======================================================

    def compare_skill(
        self,
        skill: str,
        earlier_run_id: int,
        later_run_id: int,
    ) -> SnapshotSkillChange:

        points = self.skill_trend(
            skill
        )

        point_map = {
            point.refresh_run_id: point
            for point in points
        }

        if (
            earlier_run_id
            not in point_map
        ):
            raise ValueError(
                "Earlier snapshot does not exist."
            )

        if (
            later_run_id
            not in point_map
        ):
            raise ValueError(
                "Later snapshot does not exist."
            )

        earlier = point_map[
            earlier_run_id
        ]

        later = point_map[
            later_run_id
        ]

        change = round(
            (
                later.demand_percentage
                - earlier.demand_percentage
            ),
            2,
        )

        return SnapshotSkillChange(
            skill=skill,

            earlier_run_id=(
                earlier_run_id
            ),

            later_run_id=(
                later_run_id
            ),

            earlier_percentage=(
                earlier.demand_percentage
            ),

            later_percentage=(
                later.demand_percentage
            ),

            percentage_point_change=(
                change
            ),

            earlier_job_count=(
                earlier.job_count
            ),

            later_job_count=(
                later.job_count
            ),

            trend=(
                self._trend_label(
                    change
                )
            ),
        )

    # ======================================================
    # RISING / FALLING SKILLS
    # ======================================================

    def changing_skills(
        self,
        earlier_run_id: int,
        later_run_id: int,
        direction: str = "rising",
        limit: int = 15,
    ) -> List[SnapshotSkillChange]:

        direction = (
            direction
            .strip()
            .casefold()
        )

        if direction not in {
            "rising",
            "falling",
        }:
            raise ValueError(
                "direction must be "
                "'rising' or 'falling'."
            )

        results = []

        for skill in (
            self.history.available_skills()
        ):

            comparison = (
                self.compare_skill(
                    skill=skill,
                    earlier_run_id=(
                        earlier_run_id
                    ),
                    later_run_id=(
                        later_run_id
                    ),
                )
            )

            if (
                direction == "rising"
                and comparison
                .percentage_point_change
                > 0
            ):
                results.append(
                    comparison
                )

            elif (
                direction == "falling"
                and comparison
                .percentage_point_change
                < 0
            ):
                results.append(
                    comparison
                )

        if direction == "rising":

            results.sort(
                key=lambda item: (
                    item.percentage_point_change,
                    item.later_percentage,
                    item.later_job_count,
                ),
                reverse=True,
            )

        else:

            results.sort(
                key=lambda item: (
                    item.percentage_point_change,
                    -item.later_percentage,
                )
            )

        return results[
            :limit
        ]

    # ======================================================
    # OVERALL MARKET CHANGE
    # ======================================================

    def market_change(
        self,
        earlier_run_id: int,
        later_run_id: int,
    ) -> MarketSnapshotChange:

        earlier = self.snapshot(
            earlier_run_id
        )

        later = self.snapshot(
            later_run_id
        )

        if earlier is None:
            raise ValueError(
                "Earlier snapshot does not exist."
            )

        if later is None:
            raise ValueError(
                "Later snapshot does not exist."
            )

        earlier_jobs = (
            earlier[
                "snapshot_jobs"
            ]
        )

        later_jobs = (
            later[
                "snapshot_jobs"
            ]
        )

        job_change = (
            later_jobs
            - earlier_jobs
        )

        if earlier_jobs:

            percentage_change = round(
                (
                    job_change
                    / earlier_jobs
                )
                * 100,
                2,
            )

        else:
            percentage_change = None

        earlier_companies = (
            earlier[
                "companies_count"
            ]
        )

        later_companies = (
            later[
                "companies_count"
            ]
        )

        return MarketSnapshotChange(
            earlier_run_id=(
                earlier_run_id
            ),
            later_run_id=(
                later_run_id
            ),

            earlier_jobs=(
                earlier_jobs
            ),
            later_jobs=(
                later_jobs
            ),
            job_change=(
                job_change
            ),
            job_change_percentage=(
                percentage_change
            ),

            earlier_companies=(
                earlier_companies
            ),
            later_companies=(
                later_companies
            ),

            company_change=(
                later_companies
                - earlier_companies
            ),
        )
