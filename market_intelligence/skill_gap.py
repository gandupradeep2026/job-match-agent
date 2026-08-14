from dataclasses import dataclass, field
from typing import List, Optional

from market_intelligence.cv_market_comparator import (
    CVMarketComparator,
    SkillMarketMatch,
)
from market_intelligence.database import JobMarketDatabase


@dataclass
class SkillGapRecommendation:
    skill: str
    market_count: int
    market_percentage: float

    priority: str
    priority_score: float

    reason: str


@dataclass
class SkillGapAnalysisResult:
    total_jobs_analyzed: int

    job_family: Optional[str] = None
    country: Optional[str] = None

    market_coverage_percentage: float = 0.0

    recommendations: List[SkillGapRecommendation] = field(
        default_factory=list
    )


class SkillGapPrioritizer:
    """
    Prioritize missing candidate skills based on market demand.

    The prioritizer builds on CVMarketComparator and converts
    missing skills into actionable recommendations.
    """

    def __init__(
        self,
        database: JobMarketDatabase,
    ):
        self.database = database

        self.comparator = CVMarketComparator(
            database
        )

    @staticmethod
    def _priority_from_percentage(
        percentage: float,
    ) -> str:
        """
        Convert market demand percentage into a priority tier.
        """

        if percentage >= 50:
            return "CRITICAL"

        if percentage >= 30:
            return "HIGH"

        if percentage >= 15:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _priority_score(
        market_percentage: float,
        market_count: int,
        total_jobs: int,
    ) -> float:
        """
        Calculate normalized priority score.

        Main signal:
            market demand percentage

        Small secondary signal:
            raw number of jobs requesting the skill
        """

        if total_jobs <= 0:
            return 0.0

        demand_component = market_percentage

        count_component = min(
            (market_count / total_jobs) * 10,
            10,
        )

        score = (
            demand_component
            + count_component
        )

        return round(
            min(score, 100.0),
            2,
        )

    @staticmethod
    def _build_reason(
        skill: SkillMarketMatch,
        total_jobs: int,
        priority: str,
    ) -> str:

        return (
            f"{skill.skill} appears in "
            f"{skill.market_count} of "
            f"{total_jobs} analysed jobs "
            f"({skill.market_percentage:.2f}% demand). "
            f"Priority: {priority}."
        )

    def analyze(
        self,
        candidate_skills: List[str],
        job_family: Optional[str] = None,
        country: Optional[str] = None,
        top_n: int = 30,
        required_only: bool = False,
    ) -> SkillGapAnalysisResult:
        """
        Analyze and prioritize missing market skills.

        Args:
            candidate_skills:
                Skills currently present in candidate profile/CV.

            job_family:
                Optional filter, e.g. "Data & Analytics".

            country:
                Optional filter, e.g. "Germany".

            top_n:
                Number of top market skills to consider.

            required_only:
                If True, consider only required skills.

        Returns:
            SkillGapAnalysisResult
        """

        comparison = self.comparator.compare(
            candidate_skills=candidate_skills,
            job_family=job_family,
            country=country,
            top_n=top_n,
            required_only=required_only,
        )

        recommendations = []

        for missing_skill in comparison.missing_market_skills:

            priority = self._priority_from_percentage(
                missing_skill.market_percentage
            )

            score = self._priority_score(
                market_percentage=missing_skill.market_percentage,
                market_count=missing_skill.market_count,
                total_jobs=comparison.total_jobs_analyzed,
            )

            recommendation = SkillGapRecommendation(
                skill=missing_skill.skill,
                market_count=missing_skill.market_count,
                market_percentage=missing_skill.market_percentage,
                priority=priority,
                priority_score=score,
                reason=self._build_reason(
                    skill=missing_skill,
                    total_jobs=comparison.total_jobs_analyzed,
                    priority=priority,
                ),
            )

            recommendations.append(
                recommendation
            )

        recommendations.sort(
            key=lambda item: (
                item.priority_score,
                item.market_percentage,
                item.market_count,
            ),
            reverse=True,
        )

        return SkillGapAnalysisResult(
            total_jobs_analyzed=(
                comparison.total_jobs_analyzed
            ),
            job_family=job_family,
            country=country,
            market_coverage_percentage=(
                comparison.market_coverage_percentage
            ),
            recommendations=recommendations,
        )
