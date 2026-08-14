from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ProviderJob:
    """
    Normalized job returned by an external job provider.

    This object is intentionally independent from
    JobMarketRecord so multiple external providers can
    share the same collection pipeline.
    """

    job_title: str

    company: str = ""
    location: str = ""
    country: str = ""

    description: str = ""

    source: str = ""
    source_url: str = ""

    posted_date: Optional[str] = None

    external_id: str = ""


class JobSourceProvider(ABC):
    """
    Base interface for an external job source.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def fetch_jobs(self) -> List[ProviderJob]:
        """
        Fetch currently available jobs from the provider.
        """
        raise NotImplementedError
