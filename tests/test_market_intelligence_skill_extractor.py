from market_intelligence.skill_extractor import UniversalSkillExtractor


extractor = UniversalSkillExtractor()


def test_extracts_data_engineering_skills():
    result = extractor.extract(
        text="""
        Strong Python and SQL skills are required.
        Experience with Apache Spark, BigQuery and Airflow is required.
        Docker would be a plus.
        """
    )

    assert "Python" in result.required_skills
    assert "SQL" in result.required_skills
    assert "Apache Spark" in result.required_skills
    assert "BigQuery" in result.required_skills
    assert "Apache Airflow" in result.required_skills

    assert "Docker" in result.preferred_skills


def test_extracts_hospitality_skills():
    result = extractor.extract(
        text="""
        Experience in customer service, front office
        and reservation management is required.
        SAP would be a plus.
        """
    )

    assert "Customer Service" in result.required_skills
    assert "Front Office" in result.required_skills
    assert "Reservation Management" in result.required_skills

    assert "SAP" in result.preferred_skills


def test_extracts_automotive_skills():
    result = extractor.extract(
        text="""
        Experience with AUTOSAR, CAN bus,
        ISO 26262, MATLAB and Simulink.
        """
    )

    assert "AUTOSAR" in result.required_skills
    assert "CAN Bus" in result.required_skills
    assert "ISO 26262" in result.required_skills
    assert "MATLAB" in result.required_skills
    assert "Simulink" in result.required_skills


def test_extracts_business_and_sales_skills():
    result = extractor.extract(
        text="""
        Experience in business development,
        account management, CRM and Salesforce is required.
        Power BI is nice to have.
        """
    )

    assert "Business Development" in result.required_skills
    assert "Account Management" in result.required_skills
    assert "CRM" in result.required_skills
    assert "Salesforce" in result.required_skills

    assert "Power BI" in result.preferred_skills


def test_required_skill_overrides_preferred():
    result = extractor.extract(
        text="""
        Docker is nice to have.
        Professional Docker experience is required.
        """
    )

    assert "Docker" in result.required_skills
    assert "Docker" not in result.preferred_skills


def test_extracts_german_hospitality_terms():
    result = extractor.extract(
        text="""
        Erfahrung im Kundenservice, an der Rezeption
        und mit Reservierungssystemen.
        SAP ist von Vorteil.
        """
    )

    assert "Customer Service" in result.required_skills
    assert "Front Office" in result.required_skills
    assert "Reservation Management" in result.required_skills

    assert "SAP" in result.preferred_skills
