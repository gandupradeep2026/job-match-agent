from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ElevatorPitchRequest:
    language: str
    duration_seconds: int
    audience: str
    target_role: str


@dataclass
class ElevatorPitchResult:
    language: str
    duration_seconds: int
    audience: str
    target_role: str
    text: str
    warnings: list[str]
    evidence_count: int
