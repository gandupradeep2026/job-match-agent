from market_intelligence.market_taxonomy import (
    classify_market_job,
)


def test_databricks_consulting_engineer_is_not_plain_data_engineer():
    result = classify_market_job(
        job_title="Senior Databricks Consulting Engineer (m/f/*)",
        description="Work with Databricks, Spark, data engineering and cloud.",
        legacy_job_family="Data & Analytics",
        legacy_occupation="Data Engineer",
    )
    assert result.job_family == "Data Engineering"
    assert result.subcategory == "Databricks Consulting Engineer"


def test_databricks_resident_solutions_architect_is_architect_role():
    result = classify_market_job(
        job_title="Databricks Resident Solutions Architect (m/f/*)",
        description="Design enterprise data and Databricks solutions.",
        legacy_job_family="Data & Analytics",
        legacy_occupation="Data Engineer",
    )
    assert result.job_family == "Data Engineering"
    assert result.subcategory == "Data Solutions Architect"


def test_standard_data_engineer_remains_data_engineer():
    result = classify_market_job(
        job_title="Senior Data Engineer",
        description="Python SQL ETL cloud data pipelines.",
        legacy_job_family="Data & Analytics",
        legacy_occupation="Data Engineer",
    )
    assert result.job_family == "Data Engineering"
    assert result.subcategory == "Data Engineer"
