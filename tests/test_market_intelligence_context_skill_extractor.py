from market_intelligence.context_skill_extractor import (
    ContextAwareJobSkillExtractor,
)


extractor = (
    ContextAwareJobSkillExtractor()
)


def test_real_data_engineer_context():

    result = extractor.extract(
        text="""
        RESPONSIBILITIES

        Build scalable data pipelines using
        Python, SQL and dbt.

        Collaborate with Sales and Logistics
        teams to understand business requirements.

        REQUIREMENTS

        Strong experience with Python, SQL,
        Databricks, AWS, Terraform and Git.

        WHAT WE OFFER

        An agile international company culture
        with great benefits.
        """,
        job_family=(
            "Data & Analytics"
        ),
    )

    assert "Python" in (
        result.required_skills
    )

    assert "SQL" in (
        result.required_skills
    )

    assert "dbt" in (
        result.required_skills
    )

    assert "Databricks" in (
        result.required_skills
    )

    assert "AWS" in (
        result.required_skills
    )

    assert "Terraform" in (
        result.required_skills
    )

    assert "Git" in (
        result.required_skills
    )

    assert "Sales" not in (
        result.required_skills
    )

    assert "Logistics" not in (
        result.required_skills
    )


def test_organizational_skills_are_recorded_as_ignored():

    result = extractor.extract(
        text="""
        RESPONSIBILITIES

        Collaborate with Sales and Logistics
        teams on reporting requirements.
        """,
        job_family=(
            "Data & Analytics"
        ),
    )

    assert "Sales" in (
        result.ignored_context_skills
    )

    assert "Logistics" in (
        result.ignored_context_skills
    )


def test_required_sales_skill_is_kept():

    result = extractor.extract(
        text="""
        REQUIREMENTS

        Strong experience in Sales and
        Business Development is required.
        """,
        job_family="Sales",
    )

    assert "Sales" in (
        result.required_skills
    )

    assert (
        "Business Development"
        in result.required_skills
    )


def test_preferred_section():

    result = extractor.extract(
        text="""
        REQUIREMENTS

        Python and SQL are required.

        NICE TO HAVE

        Apache Airflow, Terraform and
        Kubernetes.
        """,
        job_family=(
            "Data & Analytics"
        ),
    )

    assert "Python" in (
        result.required_skills
    )

    assert "SQL" in (
        result.required_skills
    )

    assert "Apache Airflow" in (
        result.preferred_skills
    )

    assert "Terraform" in (
        result.preferred_skills
    )

    assert "Kubernetes" in (
        result.preferred_skills
    )


def test_boilerplate_skills_are_ignored():

    result = extractor.extract(
        text="""
        REQUIREMENTS

        Python and SQL.

        ABOUT US

        Our Sales and Logistics teams operate
        internationally.

        We have an Agile culture.
        """,
        job_family=(
            "Data & Analytics"
        ),
    )

    assert "Python" in (
        result.required_skills
    )

    assert "SQL" in (
        result.required_skills
    )

    assert "Sales" not in (
        result.all_skills()
    )

    assert "Logistics" not in (
        result.all_skills()
    )

    assert "Agile" not in (
        result.all_skills()
    )


def test_german_sections():

    result = extractor.extract(
        text="""
        DEIN PROFIL

        Sehr gute Kenntnisse in Python und SQL.
        Erfahrung mit Docker.

        WÜNSCHENSWERT

        Erfahrung mit Kubernetes und Terraform.

        WAS WIR BIETEN

        Agile Unternehmenskultur.
        """,
        job_family=(
            "Data & Analytics"
        ),
    )

    assert "Python" in (
        result.required_skills
    )

    assert "SQL" in (
        result.required_skills
    )

    assert "Docker" in (
        result.required_skills
    )

    assert "Kubernetes" in (
        result.preferred_skills
    )

    assert "Terraform" in (
        result.preferred_skills
    )
