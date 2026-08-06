from parsers.job_parser import extract_job_details
from services.ats_score import calculate_ats_score
from services.category_matcher import (
    calculate_category_scores,
)
from services.german_resume_expert import (
    generate_german_recruiter_report,
)
from services.local_ai_service import (
    extract_job_details_with_ai,
    generate_cv_recommendations,
)
from services.matcher import calculate_keyword_match
from services.resume_doctor import (
    generate_resume_doctor_report,
)


def merge_job_details(
    ai_details: dict,
    fallback_details: dict,
) -> dict:
    """
    Combine local-AI extraction with rule-based extraction.

    Non-empty AI values take priority. Rule-based values
    remain available when an AI field is empty.
    """

    merged_details = fallback_details.copy()

    for key, value in ai_details.items():
        if isinstance(value, list):
            if value:
                merged_details[key] = value

        elif value not in (
            None,
            "",
        ):
            merged_details[key] = value

    return merged_details


def empty_recommendations() -> dict:
    """
    Return the default recommendation structure.
    """

    return {
        "overall_summary": "",
        "strong_matches": [],
        "missing_requirements": [],
        "weakly_evidenced_skills": [],
        "improvement_suggestions": [],
        "suggested_bullets": [],
        "important_warnings": [],
    }


def analyse_application(
    cv_text: str,
    job_text: str,
) -> dict:
    """
    Run the complete CV and job-description analysis.
    """

    cleaned_cv_text = cv_text.strip()
    cleaned_job_text = job_text.strip()

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    if not cleaned_job_text:
        raise ValueError(
            "The job-description text is empty."
        )

    warnings = []

    if len(cleaned_cv_text) < 50:
        warnings.append(
            "Very little text was extracted from the CV. "
            "The document may be scanned or image-based."
        )

    if len(cleaned_job_text) < 30:
        warnings.append(
            "Very little text was extracted from the "
            "job description."
        )

    # --------------------------------------------------
    # BASIC KEYWORD AND ATS ANALYSIS
    # --------------------------------------------------
    keyword_match_result = calculate_keyword_match(
        cleaned_cv_text,
        cleaned_job_text,
    )

    ats_result = calculate_ats_score(
        cleaned_cv_text
    )

    # --------------------------------------------------
    # JOB INFORMATION EXTRACTION
    # --------------------------------------------------
    fallback_job_details = extract_job_details(
        cleaned_job_text
    )

    ai_extraction_used = False
    ai_extraction_error = ""

    try:
        ai_job_details = extract_job_details_with_ai(
            cleaned_job_text
        )

        extracted_job_details = merge_job_details(
            ai_details=ai_job_details,
            fallback_details=fallback_job_details,
        )

        ai_extraction_used = True

    except Exception as error:
        extracted_job_details = (
            fallback_job_details
        )

        ai_extraction_error = str(
            error
        )

        warnings.append(
            "Local AI job extraction was unavailable, "
            "so the rule-based parser was used."
        )

    # --------------------------------------------------
    # MULTI-CATEGORY JOB MATCH
    # --------------------------------------------------
    category_match_result = (
        calculate_category_scores(
            cv_text=cleaned_cv_text,
            extracted_job_details=(
                extracted_job_details
            ),
            ats_score=ats_result.get(
                "score",
                0.0,
            ),
        )
    )

    job_match_result = {
        "score": category_match_result.get(
            "overall_score",
            0.0,
        ),
        "rating": category_match_result.get(
            "rating",
            "Not calculated",
        ),
        "explanation": (
            "The overall score is calculated from "
            "required skills, preferred skills, "
            "experience, education, languages, "
            "responsibilities and ATS readability."
        ),
        "profile_completeness_score": (
            ats_result.get(
                "score",
                0.0,
            )
        ),
    }

    # --------------------------------------------------
    # GERMAN RECRUITER REPORT
    # --------------------------------------------------
    german_recruiter_report = (
        generate_german_recruiter_report(
            cv_text=cleaned_cv_text,
            ats_result=ats_result,
            job_match_result=job_match_result,
            match_result=(
                keyword_match_result
            ),
            category_match_result=(
                category_match_result
            ),
        )
    )

    # --------------------------------------------------
    # AI CV RECOMMENDATIONS
    # --------------------------------------------------
    cv_recommendations = (
        empty_recommendations()
    )

    ai_recommendations_used = False
    ai_recommendations_error = ""

    try:
        cv_recommendations = (
            generate_cv_recommendations(
                cv_text=cleaned_cv_text,
                job_text=cleaned_job_text,
            )
        )

        ai_recommendations_used = True

    except Exception as error:
        ai_recommendations_error = str(
            error
        )

        warnings.append(
            "Local AI CV recommendations could "
            "not be generated."
        )

    # --------------------------------------------------
    # RESUME DOCTOR REPORT
    # --------------------------------------------------
    resume_doctor_report = (
        generate_resume_doctor_report(
            ats_result=ats_result,
            match_result=keyword_match_result,
            cv_recommendations=cv_recommendations,
            german_recruiter_report=(
                german_recruiter_report
            ),
        )
    )

    return {
        "cv_text": cleaned_cv_text,
        "job_text": cleaned_job_text,
        "match_result": (
            keyword_match_result
        ),
        "ats_result": ats_result,
        "job_match_result": (
            job_match_result
        ),
        "category_match_result": (
            category_match_result
        ),
        "german_recruiter_report": (
            german_recruiter_report
        ),
        "resume_doctor_report": (
            resume_doctor_report
        ),
        "extracted_job_details": (
            extracted_job_details
        ),
        "cv_recommendations": (
            cv_recommendations
        ),
        "warnings": warnings,
        "ai_extraction_used": (
            ai_extraction_used
        ),
        "ai_extraction_error": (
            ai_extraction_error
        ),
        "ai_recommendations_used": (
            ai_recommendations_used
        ),
        "ai_recommendations_error": (
            ai_recommendations_error
        ),
    }
