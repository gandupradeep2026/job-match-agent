from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CareerPolishRequest:
    source_text: str
    language: str
    content_type: str
    style: str


@dataclass
class CareerPolishResult:
    source_text: str
    polished_text: str
    language: str
    content_type: str
    style: str

    changes_made: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    safety_passed: bool = True
