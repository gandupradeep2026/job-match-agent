import re
from urllib.parse import urlparse


EMAIL_PATTERN = (
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = (
    r"(?:\+?\d{1,4}[\s./-]?)?"
    r"(?:\(?\d{2,5}\)?[\s./-]?)?"
    r"\d[\d\s./-]{6,}\d"
)

URL_PATTERN = r"https?://[^\s<>\"']+"


JOB_TITLE_LABELS = [
    "job title",
    "position",
    "role",
    "stellenbezeichnung",
    "position title",
    "berufsbezeichnung",
]

COMPANY_LABELS = [
    "company",
    "company name",
    "employer",
    "unternehmen",
    "arbeitgeber",
]

LOCATION_LABELS = [
    "location",
    "work location",
    "standort",
    "arbeitsort",
    "ort",
]

CONTACT_LABELS = [
    "contact",
    "contact person",
    "recruiter",
    "hiring manager",
    "ansprechpartner",
    "ansprechpartnerin",
    "kontaktperson",
]


def clean_value(value: str) -> str:
    """
    Remove extra spaces and unwanted punctuation.
    """

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    value = value.strip(" :-|,;")

    return value


def extract_labeled_value(
    text: str,
    labels: list[str],
) -> str:
    """
    Find a value written after a label.

    Examples:
    Company: Siemens
    Standort: Berlin
    Position - IT System Administrator
    """

    for label in labels:
        pattern = rf"(?im)^\s*{re.escape(label)}\s*[:\-|]\s*(.+)$"

        match = re.search(
            pattern,
            text,
        )

        if match:
            value = clean_value(
                match.group(1)
            )

            if value:
                return value

    return ""


def extract_email(text: str) -> str:
    """
    Return the first email address found.
    """

    match = re.search(
        EMAIL_PATTERN,
        text,
    )

    if match:
        return match.group(0)

    return ""


def extract_phone(text: str) -> str:
    """
    Return the first likely phone number found.
    """

    matches = re.findall(
        PHONE_PATTERN,
        text,
    )

    for match in matches:
        phone = clean_value(match)

        digit_count = len(
            re.sub(
                r"\D",
                "",
                phone,
            )
        )

        if digit_count >= 8:
            return phone

    return ""


def extract_url(text: str) -> str:
    """
    Return the first URL found in the job description.
    """

    match = re.search(
        URL_PATTERN,
        text,
    )

    if match:
        return match.group(0).rstrip(".,);")

    return ""


def extract_company_from_email(
    email: str,
) -> str:
    """
    Try to derive a company name from an email domain.

    Example:
    jobs@siemens.com -> Siemens
    """

    if not email or "@" not in email:
        return ""

    domain = email.split("@")[-1].lower()

    ignored_domains = {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "yahoo.com",
        "icloud.com",
        "gmx.de",
        "web.de",
    }

    if domain in ignored_domains:
        return ""

    domain_name = domain.split(".")[0]

    domain_name = domain_name.replace(
        "-",
        " ",
    )

    return domain_name.title()


def extract_company_from_url(
    url: str,
) -> str:
    """
    Try to derive a company name from a URL domain.
    """

    if not url:
        return ""

    try:
        domain = urlparse(url).netloc.lower()

    except ValueError:
        return ""

    domain = domain.replace(
        "www.",
        "",
    )

    ignored_domains = {
        "linkedin.com",
        "indeed.com",
        "stepstone.de",
        "xing.com",
        "glassdoor.com",
        "arbeitsagentur.de",
        "ausbildung.de",
    }

    if domain in ignored_domains:
        return ""

    domain_name = domain.split(".")[0]

    domain_name = domain_name.replace(
        "-",
        " ",
    )

    return domain_name.title()


def extract_job_title_from_lines(
    text: str,
) -> str:
    """
    Try to identify a job title from the beginning
    of the job description.
    """

    lines = [
        clean_value(line)
        for line in text.splitlines()
        if clean_value(line)
    ]

    title_keywords = [
        "developer",
        "engineer",
        "administrator",
        "analyst",
        "consultant",
        "specialist",
        "technician",
        "manager",
        "intern",
        "trainee",
        "working student",
        "werkstudent",
        "fachinformatiker",
        "systemadministrator",
        "softwareentwickler",
        "informatiker",
        "ausbildung",
        "administrator",
        "entwickler",
        "ingenieur",
        "it support",
        "system integration",
        "systemintegration",
    ]

    for line in lines[:15]:
        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in title_keywords
        ):
            if 2 <= len(line.split()) <= 15:
                return line

    return ""


def extract_contact_name(
    text: str,
) -> str:
    """
    Try to extract a recruiter or contact person's name.
    """

    labeled_contact = extract_labeled_value(
        text,
        CONTACT_LABELS,
    )

    if labeled_contact:
        labeled_contact = re.split(
            r"[,;|]",
            labeled_contact,
        )[0]

        return clean_value(
            labeled_contact
        )

    patterns = [
        (
            r"(?i)(?:contact person|recruiter|"
            r"ansprechpartner(?:in)?|kontaktperson)"
            r"\s*[:\-]\s*"
            r"([A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+"
            r"(?:\s+[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+){1,3})"
        ),
        (
            r"(?i)(?:contact|kontakt)\s+"
            r"([A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+"
            r"(?:\s+[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]+){1,3})"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
        )

        if match:
            return clean_value(
                match.group(1)
            )

    return ""


def extract_location(
    text: str,
) -> str:
    """
    Extract a location when it follows a clear label.
    """

    return extract_labeled_value(
        text,
        LOCATION_LABELS,
    )


def extract_job_details(
    job_text: str,
) -> dict:
    """
    Extract likely application details from a job description.

    Every extracted field remains editable by the user.
    """

    email = extract_email(job_text)
    phone = extract_phone(job_text)
    url = extract_url(job_text)

    company = extract_labeled_value(
        job_text,
        COMPANY_LABELS,
    )

    if not company:
        company = extract_company_from_email(
            email
        )

    if not company:
        company = extract_company_from_url(
            url
        )

    job_title = extract_labeled_value(
        job_text,
        JOB_TITLE_LABELS,
    )

    if not job_title:
        job_title = extract_job_title_from_lines(
            job_text
        )

    return {
        "company": company,
        "job_title": job_title,
        "location": extract_location(
            job_text
        ),
        "job_url": url,
        "contact_name": extract_contact_name(
            job_text
        ),
        "contact_email": email,
        "contact_phone": phone,
    }