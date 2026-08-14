from dataclasses import dataclass, field
from typing import Dict, List, Optional

from market_intelligence.database import JobMarketDatabase
from market_intelligence.statistics import MarketStatisticsEngine


@dataclass
class SkillMarketMatch:
    skill: str
    market_count: int
    market_percentage: float
    candidate_has_skill: bool


@dataclass
class CVMarketComparisonResult:
    total_jobs_analyzed: int
    candidate_skills: List[str] = field(default_factory=list)

    matched_market_skills: List[SkillMarketMatch] = field(
        default_factory=list
    )

    missing_market_skills: List[SkillMarketMatch] = field(
        default_factory=list
    )

    market_coverage_percentage: float = 0.0

    matched_demand_score: float = 0.0
    total_demand_score: float = 0.0

    job_family: Optional[str] = None
    country: Optional[str] = None


class CVMarketComparator:
    """
    Compare candidate CV skills against job-market demand.

    The comparator does not depend directly on the current CV parser.
    It accepts a list of normalized/extracted candidate skills.

    This keeps it reusable and allows us to connect the existing
    Job Agent CV parser in a later integration step.
    """

    def __init__(
        self,
        database: JobMarketDatabase,
    ):
        self.database = database
        self.statistics = MarketStatisticsEngine(database)

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        return " ".join(
            (skill or "").lower().strip().split()
        )

    @classmethod
    def _build_candidate_skill_map(
        cls,
        candidate_skills: List[str],
    ) -> Dict[str, str]:
        """
        Create normalized -> original skill mapping.
        """

        result = {}

        for skill in candidate_skills:

            cleaned = (skill or "").strip()

            if not cleaned:
                continue

            normalized = cls._normalize_skill(cleaned)

            if normalized not in result:
                result[normalized] = cleaned

        return result

    def compare(
        self,
        candidate_skills: List[str],
        job_family: Optional[str] = None,
        country: Optional[str] = None,
        top_n: int = 30,
        required_only: bool = False,
    ) -> CVMarketComparisonResult:
        """
        Compare CV skills against market skill demand.

        Args:
            candidate_skills:
                Skills extracted from the CV.

            job_family:
                Optional market filter, e.g. "Data & Analytics".

            country:
                Optional filter, e.g. "Germany".

            top_n:
                Number of most demanded market skills considered.

            required_only:
                If True, only required job skills are considered.

        Returns:
            CVMarketComparisonResult
        """

        jobs = self.statistics.get_jobs(
            job_family=job_family,
            country=country,
        )

        total_jobs = len(jobs)

        candidate_map = self._build_candidate_skill_map(
            candidate_skills
        )

        market_skills = self.statistics.top_skills(
            limit=top_n,
            required_only=required_only,
            job_family=job_family,
            country=country,
        )

        matched = []
        missing = []

        matched_demand_score = 0.0
        total_demand_score = 0.0

        for market_skill in market_skills:

            skill_name = market_skill["name"]
            count = market_skill["count"]
            percentage = market_skill["percentage"]

            normalized_market_skill = self._normalize_skill(
                skill_name
            )

            candidate_has_skill = (
                normalized_market_skill
                in candidate_map
            )

            skill_match = SkillMarketMatch(
                skill=skill_name,
                market_count=count,
                market_percentage=percentage,
                candidate_has_skill=candidate_has_skill,
            )

            total_demand_score += percentage

            if candidate_has_skill:
                matched.append(skill_match)
                matched_demand_score += percentage
            else:
                missing.append(skill_match)

        if total_demand_score > 0:
            market_coverage = round(
                (
                    matched_demand_score
                    / total_demand_score
                )
                * 100,
                2,
            )
        else:
            market_coverage = 0.0

        # Highest-demand missing skills first.
        missing.sort(
            key=lambda item: (
                item.market_percentage,
                item.market_count,
            ),
            reverse=True,
        )

        matched.sort(
            key=lambda item: (
                item.market_percentage,
                item.market_count,
            ),
            reverse=True,
        )

        return CVMarketComparisonResult(
            total_jobs_analyzed=total_jobs,
            candidate_skills=list(
                candidate_map.values()
            ),
            matched_market_skills=matched,
            missing_market_skills=missing,
            market_coverage_percentage=market_coverage,
            matched_demand_score=round(
                matched_demand_score,
                2,
            ),
            total_demand_score=round(
                total_demand_score,
                2,
            ),
            job_family=job_family,
            country=country,
        )
