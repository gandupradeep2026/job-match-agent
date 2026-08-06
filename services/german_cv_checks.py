import re
from typing import Any


COMMON_CV_SECTIONS = {
    "summary": [
        "professional summary",
        "summary",
        "profile",
        "career objective",
        "about me",
        "profil",
        "kurzprofil",
        "berufliches profil",
    ],
    "experience": [
        "professional experience",
        "work experience",
        "experience",
        "employment history",
        "berufserfahrung",
        "praktische erfahrung",
        "praxiserfahrung",
    ],
    "education": [
        "education",
        "academic background",
        "qualifications",
        "ausbildung",
        "schulbildung",
        "studium",
        "bildungsweg",
    ],
    "skills": [
        "technical skills",
        "skills",
        "core competencies",
        "technische kenntnisse",
        "kenntnisse",
        "fähigkeiten",
        "kompetenzen",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "projekte",
        "praxisprojekte",
    ],
    "languages": [
        "languages",
        "language skills",
        "sprachkenntnisse",
        "sprachen",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "courses",
        "zertifikate",
        "weiterbildungen",
    ],
}


ACTION_VERBS = {
    "administered",
    "analysed",
    "analyzed",
    "automated",
    "built",
    "configured",
    "created",
    "deployed",
    "designed",
    "developed",
    "documented",
    "implemented",
    "improved",
    "installed",
    "integrated",
    "maintained",
    "managed",
    "monitored",
    "optimized",
    "resolved",
    "supported",
    "tested",
    "troubleshot",
    "updated",
    "verwaltet",
    "analysiert",
    "automatisiert",
    "erstellt",
    "entwickelt",
    "implementiert",
    "installiert",
    "integriert",
    "konfiguriert",
    "optimiert",
    "unterstützt",
    "dokumentiert",
    "überwacht",
}


GERMAN_LEVEL_PATTERN = re.compile(
    r"\b(?:german|deutsch)\s*[-:()]?\s*"
    r"(a1|a2|b1|b2|c1|c2)\b",
    re.IGNORECASE,
)


ENGLISH_LEVEL_PATTERN = re.compile(
    r"\b(?:english|englisch)\s*[-:()]?\s*"
    r"(a1|a2|b1|b2|c1|c2)\b",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    """
    Normalize CV text for case-insensitive checks.
    """

    normalized = text.lower()
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def contains_email(text: str) -> bool:
    """
    Check whether the CV contains an email address.
    """

    pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    return re.search(pattern, text) is not None


def contains_phone(text: str) -> bool:
    """
    Check whether the CV contains a likely phone number.
    """

    pattern = r"(?:\+?\d[\d\s()./-]{7,}\d)"

    return re.search(pattern, text) is not None


def contains_linkedin(text: str) -> bool:
    """
    Check whether the CV contains a LinkedIn profile.
    """

    return "linkedin.com" in text.lower()


def contains_github(text: str) -> bool:
    """
    Check whether the CV contains a GitHub profile.
    """

    return "github.com" in text.lower()


def contains_portfolio(text: str) -> bool:
    """
    Check whether the CV mentions a personal portfolio.
    """

    normalized = normalize_text(text)

    portfolio_terms = [
        "portfolio",
        "personal website",
        "personal site",
        "project website",
        "meine website",
        "persönliche website",
    ]

    return any(
        term in normalized
        for term in portfolio_terms
    )


def detect_sections(text: str) -> dict[str, bool]:
    """
    Detect common English and German CV sections.
    """

    normalized = normalize_text(text)

    results = {}

    for section, headings in COMMON_CV_SECTIONS.items():
        results[section] = any(
            heading in normalized
            for heading in headings
        )

    return results


def detect_language_level(
    text: str,
    language: str,
) -> str:
    """
    Detect the stated CEFR level for German or English.
    """

    if language.lower() == "german":
        pattern = GERMAN_LEVEL_PATTERN

    elif language.lower() == "english":
        pattern = ENGLISH_LEVEL_PATTERN

    else:
        raise ValueError(
            "Language must be 'german' or 'english'."
        )

    match = pattern.search(text)

    if not match:
        return ""

    return match.group(1).upper()


def count_action_verbs(text: str) -> int:
    """
    Count unique action verbs present in the CV.
    """

    normalized = normalize_text(text)

    found_verbs = {
        verb
        for verb in ACTION_VERBS
        if re.search(
            rf"(?<![a-zäöüß])"
            rf"{re.escape(verb)}"
            rf"(?![a-zäöüß])",
            normalized,
        )
    }

    return len(found_verbs)


def count_bullet_points(text: str) -> int:
    """
    Count likely bullet-point lines.
    """

    bullet_patterns = [
        r"^\s*[-•▪●]\s+",
        r"^\s*\*\s+",
    ]

    count = 0

    for line in text.splitlines():
        if any(
            re.search(pattern, line)
            for pattern in bullet_patterns
        ):
            count += 1

    return count


def count_numeric_achievements(text: str) -> int:
    """
    Count lines containing numbers or percentages.

    This is only a rough indicator that achievements
    may be quantified.
    """

    count = 0

    for line in text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        if re.search(
            r"\b\d+(?:[.,]\d+)?%?\b",
            cleaned_line,
        ):
            count += 1

    return count


def detect_work_authorization(text: str) -> bool:
    """
    Check whether the CV mentions work authorization,
    visa status or EU work eligibility.
    """

    normalized = normalize_text(text)

    phrases = [
        "work authorization",
        "authorized to work",
        "eligible to work",
        "work permit",
        "visa status",
        "eu citizen",
        "eu citizenship",
        "niederlassungserlaubnis",
        "arbeitserlaubnis",
        "arbeitsberechtigung",
        "aufenthaltstitel",
        "eu-bürger",
        "eu bürger",
    ]

    return any(
        phrase in normalized
        for phrase in phrases
    )


def detect_relocation_availability(text: str) -> bool:
    """
    Check whether the CV states relocation availability.
    """

    normalized = normalize_text(text)

    phrases = [
        "willing to relocate",
        "open to relocation",
        "available to relocate",
        "relocation to germany",
        "relocation within germany",
        "umzugsbereit",
        "bereit zum umzug",
        "bereit für einen umzug",
    ]

    return any(
        phrase in normalized
        for phrase in phrases
    )


def detect_driving_licence(text: str) -> bool:
    """
    Check whether a driving licence is mentioned.
    """

    normalized = normalize_text(text)

    phrases = [
        "driving licence",
        "driver's licence",
        "driver license",
        "führerschein",
        "fuehrerschein",
    ]

    return any(
        phrase in normalized
        for phrase in phrases
    )


def analyse_contact_details(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse basic contact and professional-branding details.
    """

    checks = {
        "email": contains_email(cv_text),
        "phone": contains_phone(cv_text),
        "linkedin": contains_linkedin(cv_text),
        "github": contains_github(cv_text),
        "portfolio": contains_portfolio(cv_text),
    }

    score_weights = {
        "email": 30,
        "phone": 25,
        "linkedin": 20,
        "github": 15,
        "portfolio": 10,
    }

    score = sum(
        score_weights[key]
        for key, passed in checks.items()
        if passed
    )

    strengths = []
    improvements = []

    if checks["email"]:
        strengths.append(
            "Email address detected."
        )
    else:
        improvements.append(
            "Add a professional email address."
        )

    if checks["phone"]:
        strengths.append(
            "Phone number detected."
        )
    else:
        improvements.append(
            "Add a reachable phone number with country code."
        )

    if checks["linkedin"]:
        strengths.append(
            "LinkedIn profile detected."
        )
    else:
        improvements.append(
            "Add a complete LinkedIn profile."
        )

    if checks["github"]:
        strengths.append(
            "GitHub profile detected."
        )
    else:
        improvements.append(
            "Add GitHub when applying for technical roles."
        )

    if checks["portfolio"]:
        strengths.append(
            "Portfolio or personal website detected."
        )

    return {
        "score": float(score),
        "checks": checks,
        "strengths": strengths,
        "improvements": improvements,
    }


def analyse_cv_structure(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse the presence of important CV sections.
    """

    sections = detect_sections(
        cv_text
    )

    important_sections = {
        "summary": 15,
        "experience": 25,
        "education": 20,
        "skills": 20,
        "projects": 10,
        "languages": 10,
    }

    score = sum(
        weight
        for section, weight in important_sections.items()
        if sections.get(section, False)
    )

    strengths = []
    improvements = []

    for section, detected in sections.items():
        readable_name = section.replace(
            "_",
            " ",
        ).title()

        if detected:
            strengths.append(
                f"{readable_name} section detected."
            )

    missing_messages = {
        "summary": (
            "Add a concise professional summary tailored "
            "to the target role."
        ),
        "experience": (
            "Add a clearly labelled professional experience section."
        ),
        "education": (
            "Add a clearly labelled education section."
        ),
        "skills": (
            "Add a dedicated technical skills section."
        ),
        "projects": (
            "Add relevant technical or academic projects."
        ),
        "languages": (
            "Add language skills using CEFR levels such as B1 or B2."
        ),
    }

    for section, message in missing_messages.items():
        if not sections.get(section, False):
            improvements.append(
                message
            )

    return {
        "score": float(score),
        "sections": sections,
        "strengths": strengths,
        "improvements": improvements,
    }


def analyse_language_profile(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse German and English language information.
    """

    german_level = detect_language_level(
        cv_text,
        "german",
    )

    english_level = detect_language_level(
        cv_text,
        "english",
    )

    score = 0.0
    strengths = []
    improvements = []

    if german_level:
        score += 60.0

        strengths.append(
            f"German level {german_level} detected."
        )
    else:
        improvements.append(
            "State your German level using the CEFR scale."
        )

    if english_level:
        score += 40.0

        strengths.append(
            f"English level {english_level} detected."
        )
    else:
        improvements.append(
            "State your English level using the CEFR scale."
        )

    return {
        "score": score,
        "german_level": german_level,
        "english_level": english_level,
        "strengths": strengths,
        "improvements": improvements,
    }


def analyse_achievement_quality(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse bullet points, action verbs and quantified evidence.
    """

    action_verb_count = count_action_verbs(
        cv_text
    )

    bullet_count = count_bullet_points(
        cv_text
    )

    numeric_achievement_count = (
        count_numeric_achievements(
            cv_text
        )
    )

    action_score = min(
        action_verb_count * 8,
        40,
    )

    bullet_score = min(
        bullet_count * 4,
        30,
    )

    numeric_score = min(
        numeric_achievement_count * 6,
        30,
    )

    score = float(
        action_score
        + bullet_score
        + numeric_score
    )

    strengths = []
    improvements = []

    if action_verb_count >= 5:
        strengths.append(
            "The CV uses several strong action verbs."
        )
    else:
        improvements.append(
            "Use stronger action verbs such as configured, "
            "implemented, automated and resolved."
        )

    if bullet_count >= 5:
        strengths.append(
            "The CV uses readable bullet points."
        )
    else:
        improvements.append(
            "Use bullet points for experience and project evidence."
        )

    if numeric_achievement_count >= 2:
        strengths.append(
            "The CV includes some quantified evidence."
        )
    else:
        improvements.append(
            "Quantify outcomes only where accurate, such as time saved, "
            "systems supported or users assisted."
        )

    return {
        "score": min(
            score,
            100.0,
        ),
        "action_verb_count": action_verb_count,
        "bullet_count": bullet_count,
        "numeric_achievement_count": (
            numeric_achievement_count
        ),
        "strengths": strengths,
        "improvements": improvements,
    }


def analyse_german_market_details(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse practical information relevant to applications in Germany.
    """

    checks = {
        "work_authorization": (
            detect_work_authorization(
                cv_text
            )
        ),
        "relocation": (
            detect_relocation_availability(
                cv_text
            )
        ),
        "driving_licence": (
            detect_driving_licence(
                cv_text
            )
        ),
    }

    score = 0.0
    strengths = []
    improvements = []

    if checks["work_authorization"]:
        score += 45.0

        strengths.append(
            "Work authorization or visa status is mentioned."
        )
    else:
        improvements.append(
            "Consider stating your work authorization or visa situation."
        )

    if checks["relocation"]:
        score += 35.0

        strengths.append(
            "Relocation availability is mentioned."
        )
    else:
        improvements.append(
            "Mention relocation availability when applying from abroad."
        )

    if checks["driving_licence"]:
        score += 20.0

        strengths.append(
            "Driving licence information is included."
        )

    return {
        "score": score,
        "checks": checks,
        "strengths": strengths,
        "improvements": improvements,
    }


def analyse_cv_length(
    cv_text: str,
) -> dict[str, Any]:
    """
    Analyse basic CV length using word count.
    """

    word_count = len(
        cv_text.split()
    )

    if 250 <= word_count <= 900:
        score = 100.0
        message = (
            "The CV length is within a practical range."
        )

    elif 150 <= word_count < 250:
        score = 70.0
        message = (
            "The CV may be too short to show enough evidence."
        )

    elif 900 < word_count <= 1300:
        score = 65.0
        message = (
            "The CV may be too long and should be condensed."
        )

    else:
        score = 35.0
        message = (
            "The CV length is outside the recommended range."
        )

    return {
        "score": score,
        "word_count": word_count,
        "message": message,
    }


def run_german_cv_checks(
    cv_text: str,
) -> dict[str, Any]:
    """
    Run all deterministic German-market CV checks.
    """

    cleaned_cv_text = cv_text.strip()

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    contact = analyse_contact_details(
        cleaned_cv_text
    )

    structure = analyse_cv_structure(
        cleaned_cv_text
    )

    language = analyse_language_profile(
        cleaned_cv_text
    )

    achievements = analyse_achievement_quality(
        cleaned_cv_text
    )

    german_market = analyse_german_market_details(
        cleaned_cv_text
    )

    length = analyse_cv_length(
        cleaned_cv_text
    )

    strengths = (
        contact["strengths"]
        + structure["strengths"]
        + language["strengths"]
        + achievements["strengths"]
        + german_market["strengths"]
    )

    improvements = (
        contact["improvements"]
        + structure["improvements"]
        + language["improvements"]
        + achievements["improvements"]
        + german_market["improvements"]
    )

    return {
        "contact": contact,
        "structure": structure,
        "language": language,
        "achievements": achievements,
        "german_market": german_market,
        "length": length,
        "strengths": strengths,
        "improvements": improvements,
    }