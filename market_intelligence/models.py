from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class JobMarketRecord:
    """
    Universal normalized representation of a job advertisement.

    This model is intentionally job-agnostic. It can represent jobs from
    Data Engineering, Software Engineering, Automotive, Hospitality,
    Sales, HR, Finance, Healthcare, and other industries.
    """

    # ------------------------------------------------------------------
    # Basic job information
    # ------------------------------------------------------------------
    job_title: str
    company: str = ""
    location: str = ""
    country: str = ""

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    industry: str = ""
    job_family: str = ""
    occupation: str = ""
    seniority: str = ""

    # ------------------------------------------------------------------
    # Job requirements
    # ------------------------------------------------------------------
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)

    required_languages: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    education_level: str = ""
    experience_years: Optional[float] = None

    # ------------------------------------------------------------------
    # Employment information
    # ------------------------------------------------------------------
    employment_type: str = ""
    work_mode: str = ""

    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = ""
    salary_period: str = ""

    # ------------------------------------------------------------------
    # Original advertisement
    # ------------------------------------------------------------------
    description: str = ""
    source: str = ""
    source_url: str = ""

    # ------------------------------------------------------------------
    # Dates
    # ------------------------------------------------------------------
    posted_date: Optional[str] = None
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # AI metadata
    # ------------------------------------------------------------------
    parser_version: str = "1.0"
    classification_confidence: Optional[float] = None

    def all_skills(self) -> List[str]:
        """
        Return all required and preferred skills without duplicates.
        """

        combined = self.required_skills + self.preferred_skills

        seen = set()
        result = []

        for skill in combined:
            normalized = skill.strip()

            if not normalized:
                continue

            key = normalized.lower()

            if key not in seen:
                seen.add(key)
                result.append(normalized)

        return result

    def to_dict(self) -> dict:
        """
        Convert the record into a dictionary suitable for JSON/database use.
        """

        return {
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "country": self.country,
            "industry": self.industry,
            "job_family": self.job_family,
            "occupation": self.occupation,
            "seniority": self.seniority,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "required_languages": self.required_languages,
            "certifications": self.certifications,
            "education_level": self.education_level,
            "experience_years": self.experience_years,
            "employment_type": self.employment_type,
            "work_mode": self.work_mode,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_period": self.salary_period,
            "description": self.description,
            "source": self.source,
            "source_url": self.source_url,
            "posted_date": self.posted_date,
            "collected_at": self.collected_at,
            "parser_version": self.parser_version,
            "classification_confidence": self.classification_confidence,
        }