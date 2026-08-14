import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from market_intelligence.models import JobMarketRecord


DEFAULT_DATABASE_PATH = Path("database/job_market.db")


class JobMarketDatabase:
    """
    SQLite storage layer for Job Market Intelligence.

    Stores normalized JobMarketRecord objects and allows them to be
    retrieved later for analytics, CV matching, skill-gap analysis,
    trend analysis, and recommendations.
    """

    def __init__(
        self,
        database_path: str | Path = DEFAULT_DATABASE_PATH,
    ):
        self.database_path = Path(database_path)

        # Automatically create parent folder.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:
        """
        Create database tables and indexes if they do not already exist.
        """

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    job_title TEXT NOT NULL,
                    company TEXT,
                    location TEXT,
                    country TEXT,

                    industry TEXT,
                    job_family TEXT,
                    occupation TEXT,
                    seniority TEXT,

                    required_skills TEXT NOT NULL DEFAULT '[]',
                    preferred_skills TEXT NOT NULL DEFAULT '[]',
                    required_languages TEXT NOT NULL DEFAULT '[]',
                    certifications TEXT NOT NULL DEFAULT '[]',

                    education_level TEXT,
                    experience_years REAL,

                    employment_type TEXT,
                    work_mode TEXT,

                    salary_min REAL,
                    salary_max REAL,
                    salary_currency TEXT,
                    salary_period TEXT,

                    description TEXT,

                    source TEXT,
                    source_url TEXT,

                    posted_date TEXT,
                    collected_at TEXT NOT NULL,

                    parser_version TEXT,
                    classification_confidence REAL,

                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_job_title
                ON jobs(job_title)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_job_family
                ON jobs(job_family)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_country
                ON jobs(country)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_location
                ON jobs(location)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_posted_date
                ON jobs(posted_date)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_source_url
                ON jobs(source_url)
                """
            )

            connection.commit()

    @staticmethod
    def _serialize_list(values: List[str]) -> str:
        return json.dumps(
            values or [],
            ensure_ascii=False,
        )

    @staticmethod
    def _deserialize_list(value: Optional[str]) -> List[str]:
        if not value:
            return []

        try:
            data = json.loads(value)

            if isinstance(data, list):
                return data

        except json.JSONDecodeError:
            pass

        return []

    def job_exists_by_url(
        self,
        source_url: str,
    ) -> bool:
        """
        Check whether a job with the same source URL already exists.
        """

        source_url = (source_url or "").strip()

        if not source_url:
            return False

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT id
                FROM jobs
                WHERE source_url = ?
                LIMIT 1
                """,
                (source_url,),
            ).fetchone()

        return row is not None

    def add_job(
        self,
        job: JobMarketRecord,
        prevent_duplicates: bool = True,
    ) -> Optional[int]:
        """
        Insert a JobMarketRecord.

        Returns:
            New database row ID.

        Returns None if duplicate prevention is enabled and
        source_url already exists.
        """

        if (
            prevent_duplicates
            and job.source_url
            and self.job_exists_by_url(job.source_url)
        ):
            return None

        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO jobs (
                    job_title,
                    company,
                    location,
                    country,

                    industry,
                    job_family,
                    occupation,
                    seniority,

                    required_skills,
                    preferred_skills,
                    required_languages,
                    certifications,

                    education_level,
                    experience_years,

                    employment_type,
                    work_mode,

                    salary_min,
                    salary_max,
                    salary_currency,
                    salary_period,

                    description,

                    source,
                    source_url,

                    posted_date,
                    collected_at,

                    parser_version,
                    classification_confidence
                )
                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?,
                    ?, ?,
                    ?, ?,
                    ?, ?
                )
                """,
                (
                    job.job_title,
                    job.company,
                    job.location,
                    job.country,

                    job.industry,
                    job.job_family,
                    job.occupation,
                    job.seniority,

                    self._serialize_list(
                        job.required_skills
                    ),

                    self._serialize_list(
                        job.preferred_skills
                    ),

                    self._serialize_list(
                        job.required_languages
                    ),

                    self._serialize_list(
                        job.certifications
                    ),

                    job.education_level,
                    job.experience_years,

                    job.employment_type,
                    job.work_mode,

                    job.salary_min,
                    job.salary_max,
                    job.salary_currency,
                    job.salary_period,

                    job.description,

                    job.source,
                    job.source_url,

                    job.posted_date,
                    job.collected_at,

                    job.parser_version,
                    job.classification_confidence,
                ),
            )

            connection.commit()

            return cursor.lastrowid

    def add_jobs(
        self,
        jobs: List[JobMarketRecord],
        prevent_duplicates: bool = True,
    ) -> dict:
        """
        Insert multiple jobs.

        Returns summary:
        {
            "inserted": ...,
            "duplicates": ...
        }
        """

        inserted = 0
        duplicates = 0

        for job in jobs:

            job_id = self.add_job(
                job=job,
                prevent_duplicates=prevent_duplicates,
            )

            if job_id is None:
                duplicates += 1
            else:
                inserted += 1

        return {
            "inserted": inserted,
            "duplicates": duplicates,
        }

    def get_job(
        self,
        job_id: int,
    ) -> Optional[JobMarketRecord]:
        """
        Retrieve one job by database ID.
        """

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM jobs
                WHERE id = ?
                """,
                (job_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_job(row)

    def get_all_jobs(
        self,
        limit: Optional[int] = None,
    ) -> List[JobMarketRecord]:
        """
        Retrieve all jobs.

        Optional limit can restrict the number returned.
        """

        query = """
            SELECT *
            FROM jobs
            ORDER BY id DESC
        """

        parameters = ()

        if limit is not None:
            query += " LIMIT ?"
            parameters = (limit,)

        with self._connect() as connection:

            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._row_to_job(row)
            for row in rows
        ]

    def get_jobs_by_family(
        self,
        job_family: str,
    ) -> List[JobMarketRecord]:
        """
        Retrieve jobs belonging to a particular job family.
        """

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM jobs
                WHERE LOWER(job_family) = LOWER(?)
                ORDER BY id DESC
                """,
                (job_family.strip(),),
            ).fetchall()

        return [
            self._row_to_job(row)
            for row in rows
        ]

    def get_jobs_by_country(
        self,
        country: str,
    ) -> List[JobMarketRecord]:
        """
        Retrieve jobs from a specific country.
        """

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM jobs
                WHERE LOWER(country) = LOWER(?)
                ORDER BY id DESC
                """,
                (country.strip(),),
            ).fetchall()

        return [
            self._row_to_job(row)
            for row in rows
        ]

    def count_jobs(self) -> int:
        """
        Return the total number of stored jobs.
        """

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM jobs
                """
            ).fetchone()

        return int(row["total"])

    def delete_all_jobs(self) -> None:
        """
        Delete every job.

        Mainly useful for tests or development resets.
        """

        with self._connect() as connection:

            connection.execute(
                "DELETE FROM jobs"
            )

            connection.commit()

    def _row_to_job(
        self,
        row: sqlite3.Row,
    ) -> JobMarketRecord:
        """
        Convert one SQLite row back into JobMarketRecord.
        """

        return JobMarketRecord(
            job_title=row["job_title"] or "",
            company=row["company"] or "",
            location=row["location"] or "",
            country=row["country"] or "",

            industry=row["industry"] or "",
            job_family=row["job_family"] or "",
            occupation=row["occupation"] or "",
            seniority=row["seniority"] or "",

            required_skills=self._deserialize_list(
                row["required_skills"]
            ),

            preferred_skills=self._deserialize_list(
                row["preferred_skills"]
            ),

            required_languages=self._deserialize_list(
                row["required_languages"]
            ),

            certifications=self._deserialize_list(
                row["certifications"]
            ),

            education_level=row["education_level"] or "",
            experience_years=row["experience_years"],

            employment_type=row["employment_type"] or "",
            work_mode=row["work_mode"] or "",

            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            salary_currency=row["salary_currency"] or "",
            salary_period=row["salary_period"] or "",

            description=row["description"] or "",

            source=row["source"] or "",
            source_url=row["source_url"] or "",

            posted_date=row["posted_date"],
            collected_at=row["collected_at"],

            parser_version=row["parser_version"] or "1.0",

            classification_confidence=(
                row["classification_confidence"]
            ),
        )
