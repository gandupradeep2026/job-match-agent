import re
from collections import Counter


# Different names that refer to the same skill
SKILL_ALIASES = {
    "ad": "active directory",
    "azure ad": "microsoft entra id",
    "entra id": "microsoft entra id",
    "ms azure": "microsoft azure",
    "azure": "microsoft azure",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "k8s": "kubernetes",
    "win server": "windows server",
    "windows server administration": "windows server",
    "ms office": "microsoft office",
    "office 365": "microsoft 365",
    "o365": "microsoft 365",
    "powershell scripting": "powershell",
    "python programming": "python",
    "js": "javascript",
    "ts": "typescript",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "postgres": "postgresql",
    "mysql database": "mysql",
    "ci cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "gitlab ci": "ci/cd",
    "github actions": "ci/cd",
    "lan wan": "networking",
    "tcp ip": "tcp/ip",
    "information security": "cybersecurity",
    "cyber security": "cybersecurity",
    "it security": "cybersecurity",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
}


# Skills that our application currently understands
KNOWN_SKILLS = {
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "php",
    "ruby",
    "go",
    "rust",
    "sql",
    "bash",
    "powershell",

    # Web development
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "django",
    "flask",
    "fastapi",
    "spring boot",
    "rest api",
    "graphql",

    # Operating systems and administration
    "linux",
    "ubuntu",
    "debian",
    "windows",
    "windows server",
    "macos",
    "active directory",
    "microsoft entra id",
    "group policy",
    "system administration",
    "user management",

    # Networking
    "networking",
    "tcp/ip",
    "dns",
    "dhcp",
    "vpn",
    "vlan",
    "lan",
    "wan",
    "routing",
    "switching",
    "firewall",
    "wireshark",
    "cisco",
    "ccna",

    # Cloud
    "amazon web services",
    "microsoft azure",
    "google cloud platform",
    "cloud computing",
    "cloud security",
    "microsoft 365",

    # DevOps
    "git",
    "github",
    "gitlab",
    "docker",
    "kubernetes",
    "terraform",
    "ansible",
    "jenkins",
    "ci/cd",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "oracle",
    "redis",

    # Security
    "cybersecurity",
    "network security",
    "information security",
    "penetration testing",
    "vulnerability assessment",
    "incident response",
    "siem",
    "soc",
    "splunk",
    "identity and access management",
    "zero trust",
    "encryption",

    # Data and AI
    "data analysis",
    "data engineering",
    "pandas",
    "numpy",
    "machine learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "power bi",
    "tableau",

    # IT support
    "technical support",
    "help desk",
    "service desk",
    "ticketing system",
    "troubleshooting",
    "hardware",
    "software installation",
    "remote support",
    "it support",

    # Project and business tools
    "jira",
    "confluence",
    "agile",
    "scrum",
    "itil",
    "sap",
    "microsoft office",

    # German Ausbildung-related terms
    "fachinformatiker",
    "systemintegration",
    "anwendungsentwicklung",
}


def clean_text(text: str) -> str:
    """
    Convert text to lowercase and remove unnecessary characters.
    """

    text = text.lower()

    # Keep characters commonly found in technical skills
    text = re.sub(
        r"[^a-z0-9äöüß+#./\- ]",
        " ",
        text,
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_skill(text: str, skill: str) -> bool:
    """
    Check whether a skill appears as a complete word or phrase.

    Example:
    'java' should match 'Java developer'
    but should not match 'javascript'.
    """

    pattern = rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])"

    return re.search(pattern, text, re.IGNORECASE) is not None


def normalize_skill(skill: str) -> str:
    """
    Convert aliases to one standard skill name.
    """

    cleaned_skill = clean_text(skill)

    return SKILL_ALIASES.get(cleaned_skill, cleaned_skill)


def extract_skills(text: str) -> list[str]:
    """
    Find known technical skills inside a document.
    """

    cleaned_text = clean_text(text)
    found_skills = set()

    # Search for standard skill names
    for skill in KNOWN_SKILLS:
        if contains_skill(cleaned_text, skill):
            found_skills.add(normalize_skill(skill))

    # Search for aliases such as GCP, AWS and AD
    for alias, standard_skill in SKILL_ALIASES.items():
        if contains_skill(cleaned_text, alias):
            found_skills.add(standard_skill)

    return sorted(found_skills)


def count_skill_frequency(
    text: str,
    skills: list[str],
) -> dict[str, int]:
    """
    Count how many times each skill is mentioned.
    """

    cleaned_text = clean_text(text)
    frequency = Counter()

    for skill in skills:
        standard_count = len(
            re.findall(
                rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])",
                cleaned_text,
                re.IGNORECASE,
            )
        )

        frequency[skill] += standard_count

        # Also count aliases belonging to this skill
        for alias, standard_skill in SKILL_ALIASES.items():
            if standard_skill == skill:
                alias_count = len(
                    re.findall(
                        rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])",
                        cleaned_text,
                        re.IGNORECASE,
                    )
                )

                frequency[skill] += alias_count

    return dict(frequency)


def calculate_keyword_match(
    cv_text: str,
    job_text: str,
) -> dict:
    """
    Compare the CV skills with the job-description skills.
    """

    cv_skills = set(extract_skills(cv_text))
    job_skills = set(extract_skills(job_text))

    matched_skills = cv_skills.intersection(job_skills)
    missing_skills = job_skills.difference(cv_skills)
    additional_cv_skills = cv_skills.difference(job_skills)

    job_skill_frequency = count_skill_frequency(
        job_text,
        sorted(job_skills),
    )

    # Give more importance to skills repeated in the job description.
    total_weight = 0
    matched_weight = 0

    for skill in job_skills:
        frequency = job_skill_frequency.get(skill, 1)

        # Maximum weight is 3 so repeated words do not dominate the score.
        weight = min(max(frequency, 1), 3)

        total_weight += weight

        if skill in cv_skills:
            matched_weight += weight

    if total_weight == 0:
        score = 0.0
    else:
        score = (matched_weight / total_weight) * 100

    return {
        "score": round(score, 1),
        "matched_keywords": sorted(matched_skills),
        "missing_keywords": sorted(missing_skills),
        "additional_cv_skills": sorted(additional_cv_skills),
        "cv_keywords": sorted(cv_skills),
        "job_keywords": sorted(job_skills),
        "cv_keyword_count": len(cv_skills),
        "job_keyword_count": len(job_skills),
        "matched_keyword_count": len(matched_skills),
        "job_skill_frequency": job_skill_frequency,
    }