from collections import Counter
from typing import Dict, List, Optional

from market_intelligence.database import JobMarketDatabase
from market_intelligence.models import JobMarketRecord


class MarketStatisticsEngine:
    """
    Calculate market-level statistics from stored job advertisements.

    This engine is job-agnostic and can analyse any combination of
    professions, industries, countries, and job families.
    """

    def __init__(
        self,
        database: JobMarketDatabase,
    ):
        self.database = database

    @staticmethod
    def _percentage(
        count: int,
        total: int,
    ) -> float:
        if total <= 0:
            return 0.0

        return round(
            (count / total) * 100,
            2,
        )

    @staticmethod
    def _counter_to_results(
        counter: Counter,
        denominator: int,
        limit: Optional[int] = 10,
    ) -> List[Dict]:
        """
        Convert a Counter into a sorted analytics result.
        """

        items = counter.most_common(limit)

        return [
            {
                "name": name,
                "count": count,
                "percentage": MarketStatisticsEngine._percentage(
                    count,
                    denominator,
                ),
            }
            for name, count in items
        ]

    @staticmethod
    def _filter_jobs(
        jobs: List[JobMarketRecord],
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[JobMarketRecord]:

        filtered = jobs

        if job_family:
            filtered = [
                job
                for job in filtered
                if job.job_family.lower()
                == job_family.strip().lower()
            ]

        if country:
            filtered = [
                job
                for job in filtered
                if job.country.lower()
                == country.strip().lower()
            ]

        return filtered

    def get_jobs(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[JobMarketRecord]:
        """
        Retrieve jobs with optional filters.
        """

        jobs = self.database.get_all_jobs()

        return self._filter_jobs(
            jobs=jobs,
            job_family=job_family,
            country=country,
        )

    def summary(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict:
        """
        Return a high-level market summary.
        """

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        return {
            "total_jobs": len(jobs),
            "unique_companies": len(
                {
                    job.company.strip().lower()
                    for job in jobs
                    if job.company.strip()
                }
            ),
            "unique_locations": len(
                {
                    job.location.strip().lower()
                    for job in jobs
                    if job.location.strip()
                }
            ),
            "unique_job_families": len(
                {
                    job.job_family.strip().lower()
                    for job in jobs
                    if job.job_family.strip()
                }
            ),
        }

    def top_skills(
        self,
        limit: int = 20,
        required_only: bool = False,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:
        """
        Calculate skill demand.

        Each skill is counted at most once per job.

        percentage means:
            jobs containing skill / total analysed jobs * 100
        """

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter()

        for job in jobs:

            if required_only:
                skills = job.required_skills
            else:
                skills = job.all_skills()

            unique_skills = {
                skill.strip()
                for skill in skills
                if skill.strip()
            }

            counter.update(unique_skills)

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def top_job_families(
        self,
        limit: int = 20,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            country=country,
        )

        counter = Counter(
            job.job_family
            for job in jobs
            if job.job_family.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def top_occupations(
        self,
        limit: int = 20,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.occupation
            for job in jobs
            if job.occupation.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def top_countries(
        self,
        limit: int = 20,
    ) -> List[Dict]:

        jobs = self.get_jobs()

        counter = Counter(
            job.country
            for job in jobs
            if job.country.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def top_locations(
        self,
        limit: int = 20,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.location
            for job in jobs
            if job.location.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def languages(
        self,
        limit: int = 20,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter()

        for job in jobs:

            unique_languages = {
                language.strip()
                for language in job.required_languages
                if language.strip()
            }

            counter.update(unique_languages)

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )

    def work_modes(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.work_mode
            for job in jobs
            if job.work_mode.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=None,
        )

    def employment_types(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.employment_type
            for job in jobs
            if job.employment_type.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=None,
        )

    def seniority_levels(
        self,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.seniority
            for job in jobs
            if job.seniority.strip()
            and job.seniority != "Not specified"
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=None,
        )

    def top_companies(
        self,
        limit: int = 20,
        job_family: Optional[str] = None,
        country: Optional[str] = None,
    ) -> List[Dict]:

        jobs = self.get_jobs(
            job_family=job_family,
            country=country,
        )

        counter = Counter(
            job.company
            for job in jobs
            if job.company.strip()
        )

        return self._counter_to_results(
            counter=counter,
            denominator=len(jobs),
            limit=limit,
        )
