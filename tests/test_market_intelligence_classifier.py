from market_intelligence.classifier import UniversalJobClassifier


classifier = UniversalJobClassifier()


def test_classifies_data_engineer():
    result = classifier.classify(
        job_title="Junior Data Engineer",
        description="""
        We are looking for a Data Engineer with Python,
        SQL, Apache Spark, BigQuery and Airflow experience.
        """,
    )

    assert result.job_family == "Data & Analytics"
    assert result.occupation == "Data Engineer"
    assert result.seniority == "Entry-level"
    assert result.confidence > 0.5


def test_classifies_hotel_receptionist():
    result = classifier.classify(
        job_title="Hotel Receptionist",
        description="""
        You will work at the front office,
        manage reservations and support hotel guests.
        German and English are required.
        """,
    )

    assert result.job_family == "Hospitality"
    assert result.occupation == "Receptionist"


def test_classifies_automotive_job():
    result = classifier.classify(
        job_title="Automotive Software Engineer",
        description="""
        Development of automotive embedded software.
        Experience with AUTOSAR, CAN bus,
        ISO 26262 and ECU development is required.
        """,
    )

    assert result.job_family == "Automotive"
    assert result.occupation == "Automotive Software Engineer"


def test_classifies_sales_job():
    result = classifier.classify(
        job_title="Senior Sales Manager",
        description="""
        Responsible for business development,
        customer acquisition and key accounts.
        """,
    )

    assert result.job_family == "Sales"
    assert result.occupation == "Sales Manager"
    assert result.seniority == "Senior"


def test_classifies_hr_job():
    result = classifier.classify(
        job_title="Recruiter",
        description="""
        Responsible for recruitment,
        talent acquisition and candidate management.
        """,
    )

    assert result.job_family == "Human Resources"
    assert result.occupation == "Recruiter"


def test_unknown_job_is_not_forced_into_wrong_category():
    result = classifier.classify(
        job_title="Specialist",
        description="General organisational responsibilities.",
    )

    assert result.job_family == "Other"
    assert result.industry == "Other"
    assert result.confidence == 0.20
