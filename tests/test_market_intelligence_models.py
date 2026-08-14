from market_intelligence.models import JobMarketRecord


def test_data_engineer_job_record():
    job = JobMarketRecord(
        job_title="Data Engineer",
        company="Example GmbH",
        location="Berlin",
        country="Germany",
        industry="Information Technology",
        job_family="Data",
        occupation="Data Engineer",
        seniority="Mid-level",
        required_skills=[
            "Python",
            "SQL",
            "Apache Spark",
            "BigQuery",
        ],
        preferred_skills=[
            "Airflow",
            "Docker",
            "Python",
        ],
        required_languages=[
            "English",
            "German",
        ],
        experience_years=2,
        employment_type="Full-time",
        work_mode="Hybrid",
    )

    assert job.job_title == "Data Engineer"
    assert job.experience_years == 2

    assert job.all_skills() == [
        "Python",
        "SQL",
        "Apache Spark",
        "BigQuery",
        "Airflow",
        "Docker",
    ]


def test_hotel_job_record():
    job = JobMarketRecord(
        job_title="Receptionist",
        company="Example Hotel",
        location="Chemnitz",
        country="Germany",
        industry="Hospitality",
        job_family="Hotel Operations",
        occupation="Receptionist",
        required_skills=[
            "Customer Service",
            "Communication",
            "Reservation Management",
        ],
        required_languages=[
            "German",
            "English",
        ],
        employment_type="Full-time",
    )

    assert job.job_title == "Receptionist"
    assert "Customer Service" in job.required_skills
    assert "German" in job.required_languages


def test_job_record_to_dict():
    job = JobMarketRecord(
        job_title="Automotive Software Engineer",
        company="Automotive GmbH",
        required_skills=[
            "C++",
            "AUTOSAR",
            "CAN",
        ],
    )

    data = job.to_dict()

    assert isinstance(data, dict)
    assert data["job_title"] == "Automotive Software Engineer"
    assert data["company"] == "Automotive GmbH"
    assert "AUTOSAR" in data["required_skills"]
