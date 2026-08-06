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


def build_check(
    *,
    name: str,
    passed: bool,
    points: int,
    max_points: int,
    message: str,
    recommendation: str,
    priority: str,
) -> dict:
    """
    Build one ATS diagnostic check with earned and lost points.
    """

    earned_points = min(max(points, 0), max_points)

    return {
        "name": name,
        "passed": passed,
        "points": earned_points,
        "max_points": max_points,
        "lost_points": max_points - earned_points,
        "message": message,
        "recommendation": recommendation,
        "priority": priority,
    }


def calculate_ats_score(cv_text: str) -> dict:
    score = 0
    checks = []

    text_length = len(cv_text.strip())
    word_count = len(cv_text.split())
    headings = detect_headings(cv_text)

    if text_length >= 500:
        score += 15
        checks.append(
            build_check(
                name="Readable text",
                passed=True,
                points=15,
                max_points=15,
                message="The CV contains enough readable text.",
                recommendation=(
                    "Keep the CV text selectable and avoid image-only pages."
                ),
                priority="low",
            )
        )
    elif text_length >= 200:
        score += 8
        checks.append(
            build_check(
                name="Readable text",
                passed=True,
                points=8,
                max_points=15,
                message="The CV is readable, but it may be too short.",
                recommendation=(
                    "Add relevant, truthful detail to experience, projects, "
                    "education, or technical skills."
                ),
                priority="medium",
            )
        )
    else:
        checks.append(
            build_check(
                name="Readable text",
                passed=False,
                points=0,
                max_points=15,
                message="Very little text was detected.",
                recommendation=(
                    "Use a text-based PDF or DOCX and include enough relevant "
                    "content for ATS systems to parse."
                ),
                priority="high",
            )
        )

    if contains_email(cv_text):
        score += 10
        checks.append(
            build_check(
                name="Email address",
                passed=True,
                points=10,
                max_points=10,
                message="An email address was detected.",
                recommendation="Keep the email professional and easy to read.",
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Email address",
                passed=False,
                points=0,
                max_points=10,
                message="No email address was detected.",
                recommendation=(
                    "Add a professional email address near the top of the CV."
                ),
                priority="high",
            )
        )

    if contains_phone(cv_text):
        score += 10
        checks.append(
            build_check(
                name="Phone number",
                passed=True,
                points=10,
                max_points=10,
                message="A phone number was detected.",
                recommendation=(
                    "Use an international format such as +49 when applying "
                    "in Germany."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Phone number",
                passed=False,
                points=0,
                max_points=10,
                message="No phone number was detected.",
                recommendation=(
                    "Add a reachable phone number near the top of the CV."
                ),
                priority="high",
            )
        )

    if contains_linkedin(cv_text):
        score += 5
        checks.append(
            build_check(
                name="LinkedIn profile",
                passed=True,
                points=5,
                max_points=5,
                message="A LinkedIn profile was detected.",
                recommendation=(
                    "Ensure the LinkedIn profile matches the CV."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="LinkedIn profile",
                passed=False,
                points=0,
                max_points=5,
                message="No LinkedIn profile was detected.",
                recommendation=(
                    "Add LinkedIn only if the profile is complete, current, "
                    "and professional."
                ),
                priority="low",
            )
        )

    if headings["experience"]:
        score += 15
        checks.append(
            build_check(
                name="Experience section",
                passed=True,
                points=15,
                max_points=15,
                message="An experience section was detected.",
                recommendation=(
                    "Keep role titles, employers, dates, and achievements clear."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Experience section",
                passed=False,
                points=0,
                max_points=15,
                message="No clear experience section was detected.",
                recommendation=(
                    "Add a clearly named Experience or Berufserfahrung section. "
                    "Students may include internships, projects, student jobs, "
                    "or practical experience."
                ),
                priority="high",
            )
        )

    if headings["education"]:
        score += 15
        checks.append(
            build_check(
                name="Education section",
                passed=True,
                points=15,
                max_points=15,
                message="An education section was detected.",
                recommendation=(
                    "Keep qualification names, institutions, and dates clear."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Education section",
                passed=False,
                points=0,
                max_points=15,
                message="No clear education section was detected.",
                recommendation=(
                    "Add an Education, Ausbildung, or Studium section using a "
                    "standard heading."
                ),
                priority="high",
            )
        )

    if headings["skills"]:
        score += 10
        checks.append(
            build_check(
                name="Skills section",
                passed=True,
                points=10,
                max_points=10,
                message="A skills section was detected.",
                recommendation=(
                    "Keep skills grouped and supported by your real experience."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Skills section",
                passed=False,
                points=0,
                max_points=10,
                message="No clear skills section was detected.",
                recommendation=(
                    "Add a Skills, Kenntnisse, Fähigkeiten, or Kompetenzen "
                    "section with truthful job-relevant skills."
                ),
                priority="high",
            )
        )

    if contains_dates(cv_text):
        score += 10
        checks.append(
            build_check(
                name="Dates",
                passed=True,
                points=10,
                max_points=10,
                message="Dates were detected in the CV.",
                recommendation=(
                    "Use one consistent date format throughout the CV."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Dates",
                passed=False,
                points=0,
                max_points=10,
                message="No clear dates were detected.",
                recommendation=(
                    "Add dates to education, experience, internships, and "
                    "projects using a consistent month/year format."
                ),
                priority="medium",
            )
        )

    if contains_bullet_points(cv_text):
        score += 5
        checks.append(
            build_check(
                name="Bullet points",
                passed=True,
                points=5,
                max_points=5,
                message="Bullet points were detected.",
                recommendation=(
                    "Keep bullets concise, action-focused, and evidence-based."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="Bullet points",
                passed=False,
                points=0,
                max_points=5,
                message="No bullet points were detected.",
                recommendation=(
                    "Use simple bullet points for responsibilities, projects, "
                    "and achievements."
                ),
                priority="medium",
            )
        )

    if 150 <= word_count <= 1200:
        score += 5
        checks.append(
            build_check(
                name="CV length",
                passed=True,
                points=5,
                max_points=5,
                message="The CV length is within a reasonable range.",
                recommendation=(
                    "Keep the CV concise and remove unrelated information."
                ),
                priority="low",
            )
        )
    else:
        checks.append(
            build_check(
                name="CV length",
                passed=False,
                points=0,
                max_points=5,
                message=(
                    "The CV may be too short or too long. "
                    f"Detected word count: {word_count}."
                ),
                recommendation=(
                    "Aim for a focused CV with enough evidence for the role. "
                    "Junior applicants usually benefit from one to two pages."
                ),
                priority="medium",
            )
        )

    final_score = min(score, 100)
    points_lost = sum(
        check["lost_points"]
        for check in checks
    )

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    failed_checks = sorted(
        [
            check
            for check in checks
            if check["lost_points"] > 0
        ],
        key=lambda check: (
            priority_order.get(
                check["priority"],
                3,
            ),
            -check["lost_points"],
        ),
    )

    return {
        "score": final_score,
        "max_score": 100,
        "points_lost": points_lost,
        "checks": checks,
        "failed_checks": failed_checks,
        "word_count": word_count,
        "text_length": text_length,
        "headings": headings,
    }
