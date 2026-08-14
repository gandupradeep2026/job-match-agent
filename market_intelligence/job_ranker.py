from dataclasses import dataclass, field
from typing import List, Optional, Set

from market_intelligence.database import JobMarketDatabase
from market_intelligence.models import JobMarketRecord
from market_intelligence.skill_extractor import UniversalSkillExtractor
from market_intelligence.statistics import MarketStatisticsEngine


@dataclass
class RankedJob:
    rank: int

    job_title: str
    company: str
    location: str
    country: str

    job_family: str
    occupation: str
    seniority: str

    fit_score: float

    required_skill_score: float
    preferred_skill_score: float

    matched_required_skills: List[str] = field(
        default_factory=list
    )

    missing_required_skills: List[str] = field(
        default_factory=list
    )

    matched_preferred_skills: List[str] = field(
        default_factory=list
    )

    missing_preferred_skills: List[str] = field(
        default_factory=list
    )

    source: str = ""
    source_url: str = ""


@dataclass
class JobRankingResult:
    total_jobs_considered: int

    candidate_skills: List[str] = field(
        default_factory=list
    )

    ranked_jobs: List[RankedJob] = field(
        default_factory=list
    )

    job_family: Optional[str] = None
    country: Optional[str] = None


class JobRanker:
    """
    Rank stored jobs according to candidate skill fit.

    Ranking logic:

    Required skills:
        80% of score

    Preferred skills:
        20% of score

    If a job has no preferred skills, required skills account
    for 100% of the score.

    The ranker also canonicalizes aliases such as:

        GCP -> Google Cloud Platform
        Kafka -> Apache Kafka
        Airflow -> Apache Airflow
    """

    REQUIRED_WEIGHT = 0.80
    PREFERRED_WEIGHT = 0.20

    def __init__(
        self,
        database: JobMarketDatabase,
    ):
        self.database = database

        self.statistics = MarketStatisticsEngine(
            database
        )

        self.skill_extractor = UniversalSkillExtractor()

        self.alias_to_canonical = (
            self._build_alias_mapping()
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            (value or "").lower().strip().split()
        )

    def _build_alias_mapping(self) -> dict:
        """
        Build alias -> canonical skill lookup.
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

    def _canonicalize_candidate_skills(
        self,
        candidate_skills: List[str],
    ) -> Set[str]:

        canonical = set()

        for skill in candidate_skills:

            if not (skill or "").strip():
                continue

            resolved = self._canonicalize_skill(
                skill
            )

            canonical.add(
                self._normalize(resolved)
            )

        return canonical

    def _candidate_has_skill(
        self,
        candidate_skills: Set[str],
        skill: str,
    ) -> bool:

        canonical_skill = self._canonicalize_skill(
            skill
        )

        normalized = self._normalize(
            canonical_skill
        )

        return normalized in candidate_skills

    def _analyse_skill_group(
        self,
        candidate_skills: Set[str],
        job_skills: List[str],
    ) -> tuple[List[str], List[str], float]:

        if not job_skills:
            return [], [], 0.0

        matched = []
        missing = []

        seen = set()

        for skill in job_skills:

            canonical_skill = self._canonicalize_skill(
                skill
            )

            key = self._normalize(
                canonical_skill
            )

            if key in seen:
                continue

            seen.add(key)

            if self._candidate_has_skill(
                candidate_skills,
                canonical_skill,
            ):
                matched.append(
                    canonical_skill
                )
            else:
                missing.append(
                    canonical_skill
                )

        total = len(matched) + len(missing)

        if total == 0:
            score = 0.0
        else:
            score = round(
                (len(matched) / total) * 100,
                2,
            )

        return matched, missing, score

    def _calculate_fit_score(
        self,
        required_score: float,
        preferred_score: float,
        has_required: bool,
        has_preferred: bool,
    ) -> float:

        if not has_required and not has_preferred:
            return 0.0

        if has_required and not has_preferred:
            return round(
                required_score,
                2,
            )

        if not has_required and has_preferred:
            return round(
                preferred_score,
                2,
            )

        score = (
            required_score
            * self.REQUIRED_WEIGHT
            +
            preferred_score
            * self.PREFERRED_WEIGHT
        )

        return round(
            min(score, 100.0),
            2,
        )

    def _rank_one_job(
        self,
        job: JobMarketRecord,
        candidate_skills: Set[str],
    ) -> RankedJob:

        (
            matched_required,
            missing_required,
            required_score,
        ) = self._analyse_skill_group(
            candidate_skills,
            job.required_skills,
        )

        (
            matched_preferred,
            missing_preferred,
            preferred_score,
        ) = self._analyse_skill_group(
            candidate_skills,
            job.preferred_skills,
        )

        fit_score = self._calculate_fit_score(
            required_score=required_score,
            preferred_score=preferred_score,
            has_required=bool(
                job.required_skills
            ),
            has_preferred=bool(
                job.preferred_skills
            ),
        )

        return RankedJob(
            rank=0,

            job_title=job.job_title,
            company=job.company,
            location=job.location,
            country=job.country,

            job_family=job.job_family,
            occupation=job.occupation,
            seniority=job.seniority,

            fit_score=fit_score,

            required_skill_score=required_score,
            preferred_skill_score=preferred_score,

            matched_required_skills=(
                matched_required
            ),

            missing_required_skills=(
                missing_required
            ),

            matched_preferred_skills=(
                matched_preferred
            ),

            missing_preferred_skills=(
                missing_preferred
            ),

            source=job.source,
            source_url=job.source_url,
        )

    def rank_jobs(
        self,
        candidate_skills: List[str],
        job_family: Optional[str] = None,
        country: Optional[str] = None,
        minimum_score: float = 0.0,
        limit: Optional[int] = None,
    ) -> JobRankingResult:
        """
        Rank available jobs by candidate skill fit.
        """

        jobs = self.statistics.get_jobs(
            job_family=job_family,
            country=country,
        )

        canonical_candidate_skills = (
            self._canonicalize_candidate_skills(
                candidate_skills
            )
        )

        ranked = [
            self._rank_one_job(
                job=job,
                candidate_skills=(
                    canonical_candidate_skills
                ),
            )
            for job in jobs
        ]

        ranked = [
            job
            for job in ranked
            if job.fit_score >= minimum_score
        ]

        ranked.sort(
            key=lambda item: (
                item.fit_score,
                item.required_skill_score,
                len(
                    item.matched_required_skills
                ),
            ),
            reverse=True,
        )

        if limit is not None:
            ranked = ranked[:limit]

        for index, job in enumerate(
            ranked,
            start=1,
        ):
            job.rank = index

        return JobRankingResult(
            total_jobs_considered=len(jobs),
            candidate_skills=candidate_skills,
            ranked_jobs=ranked,
            job_family=job_family,
            country=country,
        )
