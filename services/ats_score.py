import re


STANDARD_HEADINGS = {
    "summary": [
        "summary",
        "profile",
        "professional summary",
        "about me",
        "career objective",
        "profil",
        "kurzprofil",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "berufserfahrung",
        "praktische erfahrung",
    ],
    "education": [
        "education",
        "academic background",
        "qualifications",
        "ausbildung",
        "schulbildung",
        "studium",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "kenntnisse",
        "fähigkeiten",
        "kompetenzen",
    ],
    "languages": [
        "languages",
        "language skills",
        "sprachkenntnisse",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "courses",
        "zertifikate",
        "weiterbildungen",
    ],
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_email(text: str) -> bool:
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return re.search(pattern, text) is not None


def contains_phone(text: str) -> bool:
    pattern = r"(\+?\d[\d\s()./-]{7,}\d)"
    return re.search(pattern, text) is not None


def contains_linkedin(text: str) -> bool:
    return "linkedin.com" in text.lower()


def contains_dates(text: str) -> bool:
    patterns = [
        r"\b(19|20)\d{2}\b",
        r"\b\d{1,2}[./-]\d{4}\b",
        r"\b\d{1,2}[./-]\d{1,2}[./-](19|20)\d{2}\b",
        r"\b(january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\s+(19|20)\d{2}\b",
        r"\b(januar|februar|märz|april|mai|juni|juli|august|"
        r"september|oktober|november|dezember)\s+(19|20)\d{2}\b",
    ]

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def contains_bullet_points(text: str) -> bool:
    bullet_patterns = [
        r"^\s*[-•▪●]\s+",
        r"^\s*\*\s+",
    ]

    lines = text.splitlines()

    return any(
        re.search(pattern, line)
        for line in lines
        for pattern in bullet_patterns
    )


def detect_headings(text: str) -> dict[str, bool]:
    cleaned_text = clean_text(text)
    results = {}

    for category, headings in STANDARD_HEADINGS.items():
        results[category] = any(
            heading in cleaned_text
            for heading in headings
        )

    return results


def calculate_ats_score(cv_text: str) -> dict:
    score = 0
    checks = []

    text_length = len(cv_text.strip())
    word_count = len(cv_text.split())
    headings = detect_headings(cv_text)

    if text_length >= 500:
        score += 15
        checks.append({
            "name": "Readable text",
            "passed": True,
            "points": 15,
            "message": "The CV contains enough readable text.",
        })
    elif text_length >= 200:
        score += 8
        checks.append({
            "name": "Readable text",
            "passed": True,
            "points": 8,
            "message": "The CV is readable, but it may be too short.",
        })
    else:
        checks.append({
            "name": "Readable text",
            "passed": False,
            "points": 0,
            "message": "Very little text was detected.",
        })

    if contains_email(cv_text):
        score += 10
        checks.append({
            "name": "Email address",
            "passed": True,
            "points": 10,
            "message": "An email address was detected.",
        })
    else:
        checks.append({
            "name": "Email address",
            "passed": False,
            "points": 0,
            "message": "No email address was detected.",
        })

    if contains_phone(cv_text):
        score += 10
        checks.append({
            "name": "Phone number",
            "passed": True,
            "points": 10,
            "message": "A phone number was detected.",
        })
    else:
        checks.append({
            "name": "Phone number",
            "passed": False,
            "points": 0,
            "message": "No phone number was detected.",
        })

    if contains_linkedin(cv_text):
        score += 5
        checks.append({
            "name": "LinkedIn profile",
            "passed": True,
            "points": 5,
            "message": "A LinkedIn profile was detected.",
        })
    else:
        checks.append({
            "name": "LinkedIn profile",
            "passed": False,
            "points": 0,
            "message": "No LinkedIn profile was detected.",
        })

    if headings["experience"]:
        score += 15
        checks.append({
            "name": "Experience section",
            "passed": True,
            "points": 15,
            "message": "An experience section was detected.",
        })
    else:
        checks.append({
            "name": "Experience section",
            "passed": False,
            "points": 0,
            "message": "No clear experience section was detected.",
        })

    if headings["education"]:
        score += 15
        checks.append({
            "name": "Education section",
            "passed": True,
            "points": 15,
            "message": "An education section was detected.",
        })
    else:
        checks.append({
            "name": "Education section",
            "passed": False,
            "points": 0,
            "message": "No clear education section was detected.",
        })

    if headings["skills"]:
        score += 10
        checks.append({
            "name": "Skills section",
            "passed": True,
            "points": 10,
            "message": "A skills section was detected.",
        })
    else:
        checks.append({
            "name": "Skills section",
            "passed": False,
            "points": 0,
            "message": "No clear skills section was detected.",
        })

    if contains_dates(cv_text):
        score += 10
        checks.append({
            "name": "Dates",
            "passed": True,
            "points": 10,
            "message": "Dates were detected in the CV.",
        })
    else:
        checks.append({
            "name": "Dates",
            "passed": False,
            "points": 0,
            "message": "No clear dates were detected.",
        })

    if contains_bullet_points(cv_text):
        score += 5
        checks.append({
            "name": "Bullet points",
            "passed": True,
            "points": 5,
            "message": "Bullet points were detected.",
        })
    else:
        checks.append({
            "name": "Bullet points",
            "passed": False,
            "points": 0,
            "message": "No bullet points were detected.",
        })

    if 150 <= word_count <= 1200:
        score += 5
        checks.append({
            "name": "CV length",
            "passed": True,
            "points": 5,
            "message": "The CV length is within a reasonable range.",
        })
    else:
        checks.append({
            "name": "CV length",
            "passed": False,
            "points": 0,
            "message": (
                "The CV may be too short or too long. "
                f"Detected word count: {word_count}."
            ),
        })

    return {
        "score": min(score, 100),
        "checks": checks,
        "word_count": word_count,
        "text_length": text_length,
        "headings": headings,
    }