from __future__ import annotations

from typing import Iterable, List

from market_intelligence.models import JobMarketRecord


PRIORITY_TECHNOLOGIES = [
    "Google Cloud Platform",
    "AWS",
    "Microsoft Azure",
    "BigQuery",
    "Apache Spark",
    "PySpark",
    "Databricks",
    "Apache Airflow",
    "dbt",
    "Apache Kafka",
    "Snowflake",
    "Terraform",
    "Kubernetes",
    "Docker",
    "Python",
    "SQL",
    "Machine Learning",
    "Generative AI",
    "Large Language Models",
    "PyTorch",
    "TensorFlow",
    "AUTOSAR",
    "ADAS",
    "CAN Bus",
    "CANoe",
    "ISO 26262",
    "MATLAB",
    "Simulink",
]


def _normalize(value: str) -> str:
    return " ".join(
        (value or "").casefold().strip().split()
    )


def available_technologies(
    jobs: Iterable[JobMarketRecord],
) -> List[str]:
    # Return distinct extracted skills for the selected market.
    skill_map = {}

    for job in jobs:
        for skill in job.all_skills():
            cleaned = (skill or "").strip()

            if not cleaned:
                continue

            key = _normalize(cleaned)

            if key not in skill_map:
                skill_map[key] = cleaned

    priority_keys = [
        _normalize(skill)
        for skill in PRIORITY_TECHNOLOGIES
    ]

    result = []

    for priority_skill, priority_key in zip(
        PRIORITY_TECHNOLOGIES,
        priority_keys,
    ):
        if priority_key in skill_map:
            result.append(
                skill_map.pop(
                    priority_key
                )
            )

    result.extend(
        sorted(
            skill_map.values(),
            key=lambda value: value.casefold(),
        )
    )

    return result


def job_has_technology(
    job: JobMarketRecord,
    technology: str,
) -> bool:
    selected = _normalize(
        technology
    )

    if not selected:
        return True

    return any(
        _normalize(skill) == selected
        for skill in job.all_skills()
    )


def filter_jobs_by_technology(
    jobs: Iterable[JobMarketRecord],
    technology: str | None,
) -> List[JobMarketRecord]:
    jobs = list(
        jobs
    )

    if not technology:
        return jobs

    return [
        job
        for job in jobs
        if job_has_technology(
            job,
            technology,
        )
    ]
