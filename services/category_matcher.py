import re

from services.matcher import extract_skills


def normalize_text(text: str) -> str:
    """
    Normalize text for conservative text comparison.
    """

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    return text


def requirement_is_evidenced(
    requirement: str,
    cv_text: str,
) -> bool:
    """
    Determine whether a requirement has reasonable evidence in the CV.

    The function checks:
    1. Direct phrase matching.
    2. Recognised technical skills.
    3. Significant-word overlap.
    """

    cleaned_requirement = normalize_text(
        requirement
    )

    cleaned_cv_text = normalize_text(
        cv_text
    )

    if not cleaned_requirement:
        return False

    if cleaned_requirement in cleaned_cv_text:
        return True

    requirement_skills = extract_skills(
        requirement
    )

    if requirement_skills:
        matched_skills = [
            skill
            for skill in requirement_skills
            if normalize_text(skill) in cleaned_cv_text
        ]

        if len(matched_skills) == len(
            requirement_skills
        ):
            return True

    ignored_words = {
        "and",
        "the",
        "with",
        "for",
        "from",
        "that",
        "this",
        "your",
        "you",
        "our",
        "their",
        "using",
        "use",
        "knowledge",
        "experience",
        "skills",
        "skill",
        "ability",
        "good",
        "strong",
        "required",
        "preferred",
        "minimum",
    }

    requirement_words = {
        word
        for word in re.findall(
            r"[a-z0-9äöüß+#./-]+",
            cleaned_requirement,
        )
        if len(word) >= 3
        and word not in ignored_words
    }

    if not requirement_words:
        return False

    matched_words = {
        word
        for word in requirement_words
        if re.search(
            rf"(?<![a-z0-9])"
            rf"{re.escape(word)}"
            rf"(?![a-z0-9])",
            cleaned_cv_text,
        )
    }

    word_coverage = (
        len(matched_words)
        / len(requirement_words)
    )

    return word_coverage >= 0.6


def calculate_list_match(
    requirements: list[str],
    cv_text: str,
) -> dict:
    """
    Calculate the percentage of list-based requirements
    evidenced in the CV.
    """

    matched = []
    missing = []

    unique_requirements = []

    seen_requirements = set()

    for requirement in requirements:
        cleaned_requirement = requirement.strip()

        if not cleaned_requirement:
            continue

        normalized_requirement = normalize_text(
            cleaned_requirement
        )

        if normalized_requirement in seen_requirements:
            continue

        seen_requirements.add(
            normalized_requirement
        )

        unique_requirements.append(
            cleaned_requirement
        )

    for requirement in unique_requirements:
        if requirement_is_evidenced(
            requirement=requirement,
            cv_text=cv_text,
        ):
            matched.append(requirement)

        else:
            missing.append(requirement)

    total = len(unique_requirements)

    if total == 0:
        return {
            "score": 0.0,
            "matched": [],
            "missing": [],
            "total": 0,
            "status": "not_specified",
        }

    score = (
        len(matched)
        / total
    ) * 100

    return {
        "score": round(score, 1),
        "matched": matched,
        "missing": missing,
        "total": total,
        "status": "calculated",
    }


def calculate_text_requirement_match(
    requirement: str,
    cv_text: str,
) -> dict:
    """
    Compare one broad text requirement with the CV.
    """

    cleaned_requirement = normalize_text(
        requirement
    )

    cleaned_cv_text = normalize_text(
        cv_text
    )

    if not cleaned_requirement:
        return {
            "score": 0.0,
            "matched": [],
            "missing": [],
            "status": "not_specified",
        }

    if cleaned_requirement in cleaned_cv_text:
        return {
            "score": 100.0,
            "matched": [requirement],
            "missing": [],
            "status": "calculated",
        }

    ignored_words = {
        "and",
        "the",
        "with",
        "for",
        "from",
        "that",
        "this",
        "your",
        "you",
        "our",
        "their",
        "required",
        "preferred",
        "minimum",
        "degree",
        "years",
        "year",
    }

    requirement_words = {
        word
        for word in re.findall(
            r"[a-z0-9äöüß+#./-]+",
            cleaned_requirement,
        )
        if len(word) >= 3
        and word not in ignored_words
    }

    matched_words = {
        word
        for word in requirement_words
        if re.search(
            rf"(?<![a-z0-9])"
            rf"{re.escape(word)}"
            rf"(?![a-z0-9])",
            cleaned_cv_text,
        )
    }

    missing_words = (
        requirement_words
        - matched_words
    )

    if not requirement_words:
        score = 0.0

    else:
        score = (
            len(matched_words)
            / len(requirement_words)
        ) * 100

    return {
        "score": round(score, 1),
        "matched": sorted(matched_words),
        "missing": sorted(missing_words),
        "status": "calculated",
    }


def calculate_category_scores(
    cv_text: str,
    extracted_job_details: dict,
    ats_score: float,
) -> dict:
    """
    Calculate separate, explainable job-match categories.
    """

    required_skills = calculate_list_match(
        requirements=extracted_job_details.get(
            "required_skills",
            [],
        ),
        cv_text=cv_text,
    )

    preferred_skills = calculate_list_match(
        requirements=extracted_job_details.get(
            "preferred_skills",
            [],
        ),
        cv_text=cv_text,
    )

    experience = calculate_text_requirement_match(
        requirement=extracted_job_details.get(
            "experience_requirement",
            "",
        ),
        cv_text=cv_text,
    )

    education = calculate_text_requirement_match(
        requirement=extracted_job_details.get(
            "education_requirement",
            "",
        ),
        cv_text=cv_text,
    )

    languages = calculate_list_match(
        requirements=extracted_job_details.get(
            "required_languages",
            [],
        ),
        cv_text=cv_text,
    )

    responsibilities = calculate_list_match(
        requirements=extracted_job_details.get(
            "responsibilities",
            [],
        ),
        cv_text=cv_text,
    )

    categories = {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience": experience,
        "education": education,
        "languages": languages,
        "responsibilities": responsibilities,
        "ats_readability": {
            "score": round(
                float(ats_score),
                1,
            ),
            "matched": [],
            "missing": [],
            "total": 1,
            "status": "calculated",
        },
    }

    weights = {
        "required_skills": 0.35,
        "preferred_skills": 0.10,
        "experience": 0.15,
        "education": 0.10,
        "languages": 0.10,
        "responsibilities": 0.10,
        "ats_readability": 0.10,
    }

    weighted_total = 0.0
    active_weight = 0.0

    for category_name, weight in weights.items():
        category = categories[
            category_name
        ]

        if category["status"] == "not_specified":
            continue

        weighted_total += (
            category["score"]
            * weight
        )

        active_weight += weight

    if active_weight == 0:
        overall_score = 0.0

    else:
        overall_score = (
            weighted_total
            / active_weight
        )

    overall_score = round(
        overall_score,
        1,
    )

    if overall_score >= 80:
        rating = "Strong Match"

    elif overall_score >= 65:
        rating = "Good Match"

    elif overall_score >= 50:
        rating = "Moderate Match"

    else:
        rating = "Low Match"

    return {
        "overall_score": overall_score,
        "rating": rating,
        "categories": categories,
        "weights": weights,
        "active_weight": round(
            active_weight,
            2,
        ),
    }