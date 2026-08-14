import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from market_intelligence.database import (
    JobMarketDatabase,
)


class MarketRefreshHistory:
    """
    Persistent history for Job Market Intelligence refreshes.

    Stores:

        - refresh runs
        - source-level health/results
        - market size snapshots
        - employer count
        - skill-demand snapshots

    Default database:

        database/market_history.db
    """

    def __init__(
        self,
        database_path: str | Path = (
            "database/market_history.db"
        ),
    ):
        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    # ======================================================
    # CONNECTION
    # ======================================================

    def _connect(
        self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            str(self.database_path)
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def _initialize_database(
        self,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS refresh_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,

                    jobs_before INTEGER NOT NULL,
                    jobs_after INTEGER NOT NULL,

                    snapshot_jobs INTEGER NOT NULL,
                    companies_count INTEGER NOT NULL,

                    sources_attempted INTEGER NOT NULL,
                    source_errors INTEGER NOT NULL,

                    fetched INTEGER NOT NULL,
                    inserted INTEGER NOT NULL,
                    filtered_out INTEGER NOT NULL,
                    duplicates INTEGER NOT NULL,
                    failed_jobs INTEGER NOT NULL,

                    filter_json TEXT NOT NULL DEFAULT '{}',

                    created_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS source_refresh_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    refresh_run_id INTEGER NOT NULL,

                    company TEXT,
                    provider TEXT,

                    fetched INTEGER NOT NULL,
                    inserted INTEGER NOT NULL,
                    filtered_out INTEGER NOT NULL,
                    duplicates INTEGER NOT NULL,
                    failed INTEGER NOT NULL,

                    source_error TEXT,
                    healthy INTEGER NOT NULL,

                    FOREIGN KEY (
                        refresh_run_id
                    )
                    REFERENCES refresh_runs(id)
                    ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS skill_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    refresh_run_id INTEGER NOT NULL,

                    skill TEXT NOT NULL,

                    job_count INTEGER NOT NULL,
                    demand_percentage REAL NOT NULL,

                    FOREIGN KEY (
                        refresh_run_id
                    )
                    REFERENCES refresh_runs(id)
                    ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_source_refresh_run
                ON source_refresh_runs(
                    refresh_run_id
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_skill_snapshot_run
                ON skill_snapshots(
                    refresh_run_id
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_skill_snapshot_skill
                ON skill_snapshots(
                    skill
                )
                """
            )

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _now_iso(
    ) -> str:

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )

    @staticmethod
    def _filter_to_dict(
        collection_filter,
    ) -> dict:

        if collection_filter is None:
            return {}

        return {
            "countries": list(
                getattr(
                    collection_filter,
                    "allowed_countries",
                    [],
                )
                or []
            ),
            "job_families": list(
                getattr(
                    collection_filter,
                    "allowed_job_families",
                    [],
                )
                or []
            ),
            "title_keywords": list(
                getattr(
                    collection_filter,
                    "title_keywords",
                    [],
                )
                or []
            ),
            "excluded_title_keywords": list(
                getattr(
                    collection_filter,
                    "excluded_title_keywords",
                    [],
                )
                or []
            ),
        }

    @staticmethod
    def _snapshot_jobs(
        market_database: JobMarketDatabase,
        collection_filter=None,
    ):

        jobs = (
            market_database.get_all_jobs()
        )

        if (
            collection_filter is None
            or not collection_filter.is_active()
        ):
            return jobs

        return [
            job
            for job in jobs
            if collection_filter.allows(
                job
            )
        ]

    # ======================================================
    # RECORD REFRESH + SNAPSHOT
    # ======================================================

    def record_refresh(
        self,
        result,
        market_database: JobMarketDatabase,
        collection_filter=None,
    ) -> int:
        """
        Save one refresh execution and a snapshot of the
        resulting market.

        Each skill is counted at most once per job.
        """

        jobs = self._snapshot_jobs(
            market_database=(
                market_database
            ),
            collection_filter=(
                collection_filter
            ),
        )

        total_jobs = len(
            jobs
        )

        companies = {
            (job.company or "").strip()
            for job in jobs
            if (job.company or "").strip()
        }

        skill_counts = Counter()

        for job in jobs:

            unique_skills = {
                skill.strip()
                for skill in job.all_skills()
                if skill.strip()
            }

            skill_counts.update(
                unique_skills
            )

        filter_json = json.dumps(
            self._filter_to_dict(
                collection_filter
            ),
            ensure_ascii=False,
            sort_keys=True,
        )

        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO refresh_runs (
                    started_at,
                    completed_at,

                    jobs_before,
                    jobs_after,

                    snapshot_jobs,
                    companies_count,

                    sources_attempted,
                    source_errors,

                    fetched,
                    inserted,
                    filtered_out,
                    duplicates,
                    failed_jobs,

                    filter_json,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?
                )
                """,
                (
                    result.started_at,
                    result.completed_at,

                    result.jobs_before,
                    result.jobs_after,

                    total_jobs,
                    len(companies),

                    result.sources_attempted,
                    result.source_errors,

                    result.fetched,
                    result.inserted,
                    result.filtered_out,
                    result.duplicates,
                    result.failed_jobs,

                    filter_json,
                    self._now_iso(),
                ),
            )

            refresh_run_id = int(
                cursor.lastrowid
            )

            for source in (
                result.source_results
            ):

                connection.execute(
                    """
                    INSERT INTO source_refresh_runs (
                        refresh_run_id,

                        company,
                        provider,

                        fetched,
                        inserted,
                        filtered_out,
                        duplicates,
                        failed,

                        source_error,
                        healthy
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                    """,
                    (
                        refresh_run_id,

                        source.company,
                        source.provider,

                        source.fetched,
                        source.inserted,
                        source.filtered_out,
                        source.duplicates,
                        source.failed,

                        source.source_error,
                        1 if source.healthy else 0,
                    ),
                )

            for skill, count in (
                skill_counts.items()
            ):

                percentage = (
                    round(
                        (
                            count
                            / total_jobs
                        )
                        * 100,
                        2,
                    )
                    if total_jobs
                    else 0.0
                )

                connection.execute(
                    """
                    INSERT INTO skill_snapshots (
                        refresh_run_id,
                        skill,
                        job_count,
                        demand_percentage
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        refresh_run_id,
                        skill,
                        count,
                        percentage,
                    ),
                )

        return refresh_run_id

    # ======================================================
    # REFRESH HISTORY
    # ======================================================

    def count_refreshes(
        self,
    ) -> int:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM refresh_runs
                """
            ).fetchone()

        return int(
            row["count"]
        )

    def recent_refreshes(
        self,
        limit: int = 20,
    ) -> list[dict]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM refresh_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    limit,
                ),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def latest_refresh(
        self,
    ) -> Optional[dict]:

        rows = self.recent_refreshes(
            limit=1
        )

        if not rows:
            return None

        return rows[0]

    # ======================================================
    # SOURCE HISTORY
    # ======================================================

    def source_results(
        self,
        refresh_run_id: int,
    ) -> list[dict]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM source_refresh_runs
                WHERE refresh_run_id = ?
                ORDER BY company
                """,
                (
                    refresh_run_id,
                ),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ======================================================
    # SKILL HISTORY
    # ======================================================

    def available_skills(
        self,
    ) -> list[str]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT DISTINCT skill
                FROM skill_snapshots
                ORDER BY skill COLLATE NOCASE
                """
            ).fetchall()

        return [
            row["skill"]
            for row in rows
        ]

    def skill_history(
        self,
        skill: str,
        limit: int = 100,
    ) -> list[dict]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    r.id AS refresh_run_id,
                    r.completed_at,
                    r.snapshot_jobs,
                    r.companies_count,

                    s.skill,
                    s.job_count,
                    s.demand_percentage

                FROM skill_snapshots AS s

                JOIN refresh_runs AS r
                    ON r.id = s.refresh_run_id

                WHERE LOWER(s.skill) = LOWER(?)

                ORDER BY r.id ASC

                LIMIT ?
                """,
                (
                    skill,
                    limit,
                ),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]
