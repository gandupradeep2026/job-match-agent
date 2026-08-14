from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_parser import UniversalJobParser
from market_intelligence.job_ranker import JobRanker


parser = UniversalJobParser()


def build_ranking_database(tmp_path):

    db = JobMarketDatabase(
        tmp_path / "ranking.db"
    )

    jobs = [
        parser.parse(
            job_title="Junior Data Engineer",
            company="Company A",
            country="Germany",
            description="""
            Python, SQL and BigQuery are required.
            Docker is preferred.
            """,
        ),

        parser.parse(
            job_title="Cloud Data Engineer",
            company="Company B",
            country="Germany",
            description="""
            Python, SQL, BigQuery,
            Google Cloud Platform and Terraform
            are required.

            Kubernetes is preferred.
            """,
        ),

        parser.parse(
            job_title="Streaming Data Engineer",
            company="Company C",
            country="Germany",
            description="""
            Python, SQL, Apache Spark,
            Apache Kafka and Apache Airflow
            are required.
            """,
        ),
    ]

    db.add_jobs(
        jobs,
        prevent_duplicates=False,
    )

    return db


def test_jobs_are_ranked(tmp_path):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
            "Docker",
        ],
        country="Germany",
    )

    assert result.total_jobs_considered == 3
    assert len(result.ranked_jobs) == 3

    assert (
        result.ranked_jobs[0].job_title
        == "Junior Data Engineer"
    )


def test_best_job_has_high_score(tmp_path):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
            "Docker",
        ],
        country="Germany",
    )

    best = result.ranked_jobs[0]

    assert best.fit_score == 100.0

    assert (
        best.required_skill_score
        == 100.0
    )


def test_missing_required_skills_detected(
    tmp_path,
):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        country="Germany",
    )

    cloud_job = next(
        job
        for job in result.ranked_jobs
        if job.job_title
        == "Cloud Data Engineer"
    )

    assert (
        "BigQuery"
        in cloud_job.missing_required_skills
    )

    assert (
        "Google Cloud Platform"
        in cloud_job.missing_required_skills
    )

    assert (
        "Terraform"
        in cloud_job.missing_required_skills
    )


def test_skill_aliases_are_supported(
    tmp_path,
):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
            "GCP",
            "Terraform",
        ],
        country="Germany",
    )

    cloud_job = next(
        job
        for job in result.ranked_jobs
        if job.job_title
        == "Cloud Data Engineer"
    )

    assert (
        "Google Cloud Platform"
        in cloud_job.matched_required_skills
    )


def test_minimum_score_filter(
    tmp_path,
):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
            "BigQuery",
            "Docker",
        ],
        country="Germany",
        minimum_score=80,
    )

    assert all(
        job.fit_score >= 80
        for job in result.ranked_jobs
    )


def test_limit_is_applied(tmp_path):

    db = build_ranking_database(tmp_path)

    ranker = JobRanker(db)

    result = ranker.rank_jobs(
        candidate_skills=[
            "Python",
            "SQL",
        ],
        limit=2,
    )

    assert len(result.ranked_jobs) == 2

    assert result.ranked_jobs[0].rank == 1
    assert result.ranked_jobs[1].rank == 2
