from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CareerProfile:
    """
    Master career profile.

    This profile is the trusted source of truth for later
    CV, interview, elevator-pitch and application features.

    English and German professional summaries are stored
    separately so that German content can be written
    naturally rather than being a literal translation.
    """

    # --------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------
    full_name: str = ""
    email: str = ""
    phone: str = ""

    city: str = ""
    country: str = ""

    linkedin_url: str = ""
    github_url: str = ""

    # --------------------------------------------------
    # PROFESSIONAL PROFILE
    # --------------------------------------------------
    professional_summary_en: str = ""
    professional_summary_de: str = ""

    # --------------------------------------------------
    # CAREER TARGETS
    # --------------------------------------------------
    target_roles: list[str] = field(
        default_factory=list
    )

    preferred_locations: list[str] = field(
        default_factory=list
    )

    employment_types: list[str] = field(
        default_factory=list
    )

    # --------------------------------------------------
    # SKILLS
    # --------------------------------------------------
    technical_skills: list[str] = field(
        default_factory=list
    )

    languages: list[str] = field(
        default_factory=list
    )

    certifications: list[str] = field(
        default_factory=list
    )

    # --------------------------------------------------
    # TRUTH LOCK
    # --------------------------------------------------
    verified: bool = False

    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the profile into a regular dictionary.
        """

        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "country": self.country,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "professional_summary_en": (
                self.professional_summary_en
            ),
            "professional_summary_de": (
                self.professional_summary_de
            ),
            "target_roles": list(
                self.target_roles
            ),
            "preferred_locations": list(
                self.preferred_locations
            ),
            "employment_types": list(
                self.employment_types
            ),
            "technical_skills": list(
                self.technical_skills
            ),
            "languages": list(
                self.languages
            ),
            "certifications": list(
                self.certifications
            ),
            "verified": self.verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def has_basic_identity(self) -> bool:
        """
        Return True when the minimum identity fields exist.
        """

        return bool(
            self.full_name.strip()
            and self.email.strip()
        )

    def is_truth_locked(self) -> bool:
        """
        Return whether the user has verified this profile.
        """

        return bool(
            self.verified
        )
