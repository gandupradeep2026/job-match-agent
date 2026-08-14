from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from market_intelligence.database import JobMarketDatabase
from market_intelligence.models import JobMarketRecord
from market_intelligence.skill_extractor import UniversalSkillExtractor
from market_intelligence.statistics import MarketStatisticsEngine


@dataclass
class SkillTrendPoint:
    period: str
    total_jobs: int
    jobs_with_skill: int
    demand_percentage: float


@dataclass
class SkillTrendComparison:
    skill: str

    earlier_period: str
    later_period: str

    earlier_percentage: float
    later_percentage: float

    percentage_point_change: float
    relative_change_percentage: Optional[float]

    trend: str


@dataclass
class RisingSkill:
    skill: str

    earlier_percentage: float
    later_percentage: float

    percentage_point_change: float

    earlier_count: int
    later_count: int

    trend: str


class MarketTrendAnalyzer:
    """
    Analyze how job-market demand changes over time.

    Current trend granularity:
        Monthly (YYYY-MM)

    Examples:
        - Jobs posted per month
        - Python demand over time
        - Airflow demand increase
        - Fastest rising skills
        - Falling skills

    The analyzer can optionally filter by:
        - job family
        - country
    """

    def __init__(
        self,
        database: JobMarketDatabase,
    ):
        self.database = database

        self.statistics = MarketStatisticsEngine(
            database
        )

        self.skill_extractor = (
            UniversalSkillExtractor()
        )

        self.alias_to_canonical = (
            self._build_alias_mapping()
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            (value or "").lower().strip().split()
        )

    def _build_alias_mapping(self) -> Dict[str, str]:
        """
        Build aliases such as:

        gcp -> Google Cloud Platform
        airflow -> Apache Airflow
        kafka -> Apache Kafka
        spark -> Apache Spark
        """

        mapping = {}

        for canonical, aliases in (
            self.skill_extractor.SKILL_ALIASES.items()
        ):
            mapping[
                self._normalize(canonical)
            ] = canonical

            for alias in aliases:
                mapping[
                    self._normalize(alias)
                ] = canonical

        return mapping

    def _canonicalize_skill(
        self,
        skill: str,
    ) -> str:

        normalized = self._normalize(skill)

        return self.alias_to_canonical.get(
            normalized,
            skill.strip(),
        )

    @staticmethod
    def _extract_month(
        date_value: Optional[str],
    ) -> Optional[str]:
        """
        Convert supported date values into YYYY-MM.

        Supports:
            2026-08-14
            2026-08-14T10:30:00
            2026-08-14T10:30:00+00:00
            2026-08-14T10:30:00Z
        """

        if not date_value:
            return None

        cleaned = str(date_value).strip()

        if not cleaned:
            return None

        try:
            parsed = datetime.fromisoformat(
                cleaned.replace(
                    "Z",
                    "+00:00",
                )
            )

            return parsed.strftime(
                "%Y-%m"
            )

        except ValueError:
            pass

        try:
            parsed = datetime.strptime(
                cleaned[:10],
                "%Y-%m-%d",
            )

            return parsed.strftime(
                "%Y-%m"
            )

        except ValueError:
            return None

    def _get_filtered_jobs(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[JobMarketRecord]:

        return self.statistics.get_jobs(
            job_family=job_family,
            country=country,
        )

    def _group_jobs_by_month(
        self,
        jobs: List[JobMarketRecord],
    ) -> Dict[str, List[JobMarketRecord]]:

        grouped = defaultdict(list)

        for job in jobs:

            month = self._extract_month(
                job.posted_date
            )

            if month:
                grouped[month].append(job)

        return dict(grouped)

    def job_volume_by_month(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:
        """
        Return number of job advertisements per month.
        """

        jobs = self._get_filtered_jobs(
            job_family=job_family,
            country=country,
        )

        grouped = self._group_jobs_by_month(
            jobs
        )

        return [
            {
                "period": month,
                "job_count": len(
                    grouped[month]
                ),
            }
            for month in sorted(grouped)
        ]

    def skill_trend(
        self,
        skill: str,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[SkillTrendPoint]:
        """
        Return monthly demand for one skill.

        Demand percentage:

            jobs containing skill
            --------------------- * 100
            all jobs that month
        """

        canonical_skill = (
            self._canonicalize_skill(skill)
        )

        canonical_key = self._normalize(
            canonical_skill
        )

        jobs = self._get_filtered_jobs(
            job_family=job_family,
            country=country,
        )

        grouped = self._group_jobs_by_month(
            jobs
        )

        results = []

        for month in sorted(grouped):

            monthly_jobs = grouped[month]

            skill_count = 0

            for job in monthly_jobs:

                job_skills = {
                    self._normalize(
                        self._canonicalize_skill(
                            job_skill
                        )
                    )
                    for job_skill in job.all_skills()
                    if job_skill.strip()
                }

                if canonical_key in job_skills:
                    skill_count += 1

            percentage = round(
                (
                    skill_count
                    / len(monthly_jobs)
                )
                * 100,
                2,
            )

            results.append(
                SkillTrendPoint(
                    period=month,
                    total_jobs=len(
                        monthly_jobs
                    ),
                    jobs_with_skill=skill_count,
                    demand_percentage=percentage,
                )
            )

        return results

    @staticmethod
    def _trend_label(
        change: float,
    ) -> str:

        if change >= 5:
            return "RISING"

        if change <= -5:
            return "FALLING"

        return "STABLE"

    def compare_skill_periods(
        self,
        skill: str,
        earlier_period: str,
        later_period: str,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> SkillTrendComparison:
        """
        Compare demand for one skill between two months.
        """

        canonical_skill = (
            self._canonicalize_skill(skill)
        )

        trend_points = self.skill_trend(
            skill=canonical_skill,
            job_family=job_family,
            country=country,
        )

        point_map = {
            point.period: point
            for point in trend_points
        }

        earlier_percentage = (
            point_map[
                earlier_period
            ].demand_percentage
            if earlier_period in point_map
            else 0.0
        )

        later_percentage = (
            point_map[
                later_period
            ].demand_percentage
            if later_period in point_map
            else 0.0
        )

        change = round(
            later_percentage
            - earlier_percentage,
            2,
        )

        if earlier_percentage > 0:

            relative_change = round(
                (
                    change
                    / earlier_percentage
                )
                * 100,
                2,
            )

        else:
            relative_change = None

        return SkillTrendComparison(
            skill=canonical_skill,

            earlier_period=earlier_period,
            later_period=later_period,

            earlier_percentage=(
                earlier_percentage
            ),

            later_percentage=(
                later_percentage
            ),

            percentage_point_change=change,

            relative_change_percentage=(
                relative_change
            ),

            trend=self._trend_label(
                change
            ),
        )

    def top_changing_skills(
        self,
        earlier_period: str,
        later_period: str,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 10,
        direction: str = "rising",
    ) -> List[RisingSkill]:
        """
        Find skills whose demand changed the most.

        direction:
            rising
            falling
        """

        direction = (
            direction
            .strip()
            .lower()
        )

        if direction not in {
            "rising",
            "falling",
        }:
            raise ValueError(
                "direction must be "
                "'rising' or 'falling'."
            )

        jobs = self._get_filtered_jobs(
            job_family=job_family,
            country=country,
        )

        grouped = self._group_jobs_by_month(
            jobs
        )

        earlier_jobs = grouped.get(
            earlier_period,
            [],
        )

        later_jobs = grouped.get(
            later_period,
            [],
        )

        def skill_counts(
            period_jobs: List[JobMarketRecord],
        ) -> Counter:

            counter = Counter()

            for job in period_jobs:

                unique_skills = {
                    self._canonicalize_skill(
                        skill
                    )
                    for skill in job.all_skills()
                    if skill.strip()
                }

                counter.update(
                    unique_skills
                )

            return counter

        earlier_counts = skill_counts(
            earlier_jobs
        )

        later_counts = skill_counts(
            later_jobs
        )

        all_skills = (
            set(earlier_counts)
            | set(later_counts)
        )

        results = []

        for skill in all_skills:

            earlier_count = (
                earlier_counts.get(
                    skill,
                    0,
                )
            )

            later_count = (
                later_counts.get(
                    skill,
                    0,
                )
            )

            earlier_percentage = (
                round(
                    (
                        earlier_count
                        / len(earlier_jobs)
                    )
                    * 100,
                    2,
                )
                if earlier_jobs
                else 0.0
            )

            later_percentage = (
                round(
                    (
                        later_count
                        / len(later_jobs)
                    )
                    * 100,
                    2,
                )
                if later_jobs
                else 0.0
            )

            change = round(
                later_percentage
                - earlier_percentage,
                2,
            )

            trend = self._trend_label(
                change
            )

            results.append(
                RisingSkill(
                    skill=skill,

                    earlier_percentage=(
                        earlier_percentage
                    ),

                    later_percentage=(
                        later_percentage
                    ),

                    percentage_point_change=(
                        change
                    ),

                    earlier_count=(
                        earlier_count
                    ),

                    later_count=(
                        later_count
                    ),

                    trend=trend,
                )
            )

        if direction == "rising":

            results = [
                item
                for item in results
                if item.percentage_point_change > 0
            ]

            results.sort(
                key=lambda item: (
                    item.percentage_point_change,
                    item.later_percentage,
                    item.later_count,
                ),
                reverse=True,
            )

        else:

            results = [
                item
                for item in results
                if item.percentage_point_change < 0
            ]

            results.sort(
                key=lambda item: (
                    item.percentage_point_change,
                    -item.later_percentage,
                )
            )

        return results[:limit]

    def available_periods(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[str]:
        """
        Return available months in chronological order.
        """

        jobs = self._get_filtered_jobs(
            job_family=job_family,
            country=country,
        )

        periods = {
            month
            for job in jobs
            if (
                month := self._extract_month(
                    job.posted_date
                )
            )
        }

        return sorted(periods)
