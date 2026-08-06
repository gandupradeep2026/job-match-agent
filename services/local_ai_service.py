import os
from dotenv import load_dotenv
import json
from ollama import chat
from pydantic import BaseModel, Field, ValidationError


def get_ollama_model() -> str:
    """
    Return the configured local Ollama model.
    """

    load_dotenv(
        override=True
    )

    return os.getenv(
        "OLLAMA_MODEL",
        "llama3.2",
    ).strip()


# ==================================================
# JOB-DESCRIPTION EXTRACTION MODELS
# ==================================================
class JobDetails(BaseModel):
    """
    Structured information extracted from a job description.
    """

    company: str = ""
    job_title: str = ""
    location: str = ""
    employment_type: str = ""
    work_mode: str = ""
    salary: str = ""
    application_deadline: str = ""

    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    job_url: str = ""

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    responsibilities: list[str] = Field(
        default_factory=list
    )

    required_languages: list[str] = Field(
        default_factory=list
    )

    education_requirement: str = ""
    experience_requirement: str = ""
    visa_sponsorship: str = ""
    summary: str = ""


# ==================================================
# CV-RECOMMENDATION MODELS
# ==================================================
class RecommendationItem(BaseModel):
    """
    One CV recommendation supported by evidence.
    """

    title: str
    explanation: str
    cv_evidence: str = ""
    job_evidence: str = ""
    importance: str = "medium"


class SuggestedBullet(BaseModel):
    """
    A rewritten CV bullet based on existing evidence.
    """

    original_evidence: str
    suggested_bullet: str
    related_requirement: str


class CVRecommendations(BaseModel):
    """
    Structured comparison between a CV and job description.
    """

    overall_summary: str = ""

    strong_matches: list[RecommendationItem] = Field(
        default_factory=list
    )

    missing_requirements: list[RecommendationItem] = Field(
        default_factory=list
    )

    weakly_evidenced_skills: list[
        RecommendationItem
    ] = Field(
        default_factory=list
    )

    improvement_suggestions: list[
        RecommendationItem
    ] = Field(
        default_factory=list
    )

    suggested_bullets: list[SuggestedBullet] = Field(
        default_factory=list
    )

    important_warnings: list[str] = Field(
        default_factory=list
    )


# ==================================================
# COVER-LETTER MODEL
# ==================================================
class CoverLetterResult(BaseModel):
    """
    A tailored cover letter generated from verified evidence.
    """

    subject: str = ""
    greeting: str = ""
    opening: str = ""
    motivation: str = ""
    qualification_match: str = ""
    closing: str = ""
    sign_off: str = ""

    warnings: list[str] = Field(
        default_factory=list
    )


# ==================================================
# TAILORED-CV MODEL
# ==================================================
class TailoredCVResult(BaseModel):
    """
    Structured CV content tailored to one job.
    """

    candidate_name: str = ""
    professional_title: str = ""

    contact_details: list[str] = Field(
        default_factory=list
    )

    professional_summary: str = ""

    technical_skills: list[str] = Field(
        default_factory=list
    )

    experience_sections: list[str] = Field(
        default_factory=list
    )

    project_sections: list[str] = Field(
        default_factory=list
    )

    education_sections: list[str] = Field(
        default_factory=list
    )

    certification_sections: list[str] = Field(
        default_factory=list
    )

    language_sections: list[str] = Field(
        default_factory=list
    )

    additional_sections: list[str] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )


# ==================================================
# JOB-EXTRACTION PROMPT
# ==================================================
def build_job_extraction_prompt(
    job_text: str,
) -> str:
    """
    Create instructions for extracting job information.
    """

    schema_text = json.dumps(
        JobDetails.model_json_schema(),
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are a job-description information extractor.

Extract only information explicitly stated or clearly supported
by the supplied job description.

Rules:

1. Do not invent missing information.
2. Use an empty string when a text field is missing.
3. Use an empty list when a list field is missing.
4. Keep email addresses, phone numbers and URLs exactly as written.
5. Separate required skills from preferred skills.
6. Extract language requirements together with stated levels.
7. For visa sponsorship:
   - Return "Yes" only when explicitly offered.
   - Return "No" only when explicitly unavailable.
   - Return an empty string when it is not mentioned.
8. Return only data matching the JSON schema.
9. Do not return markdown or additional commentary.

JSON schema:

{schema_text}

--- START JOB DESCRIPTION ---

{job_text}

--- END JOB DESCRIPTION ---
""".strip()


# ==================================================
# CV-RECOMMENDATION PROMPT
# ==================================================
def build_cv_recommendation_prompt(
    cv_text: str,
    job_text: str,
) -> str:
    """
    Create instructions for comparing a CV with a job.
    """

    schema_text = json.dumps(
        CVRecommendations.model_json_schema(),
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are a careful CV and job-description comparison assistant.

Compare the CV with the job description and provide truthful,
evidence-based recommendations.

Critical rules:

1. Never invent qualifications, experience, projects, skills,
   achievements, certifications, language levels or dates.
2. A requirement absent from the CV must be described as
   "not evidenced in the CV", not as proof that the candidate
   does not possess it.
3. Do not recommend adding a skill unless the candidate can
   truthfully prove it.
4. Suggested CV bullet points must be based only on information
   already present in the CV.
5. Do not create fake numbers, percentages or achievements.
6. Separate:
   - strong matches,
   - missing requirements,
   - weakly evidenced skills,
   - improvement suggestions.
7. Use importance values only from:
   - high
   - medium
   - low
8. Keep recommendations practical and concise.
9. Return only JSON matching the supplied schema.
10. Do not include markdown outside the JSON.

JSON schema:

{schema_text}

--- START CV ---

{cv_text}

--- END CV ---

--- START JOB DESCRIPTION ---

{job_text}

--- END JOB DESCRIPTION ---
""".strip()


# ==================================================
# COVER-LETTER PROMPT
# ==================================================
def build_cover_letter_prompt(
    cv_text: str,
    job_text: str,
    job_details: dict,
    language: str,
    candidate_name: str,
) -> str:
    """
    Build the prompt used to generate a truthful cover letter.
    """

    schema_text = json.dumps(
        CoverLetterResult.model_json_schema(),
        indent=2,
        ensure_ascii=False,
    )

    company = job_details.get(
        "company",
        "",
    )

    job_title = job_details.get(
        "job_title",
        "",
    )

    contact_name = job_details.get(
        "contact_name",
        "",
    )

    location = job_details.get(
        "location",
        "",
    )

    return f"""
You are a professional job-application assistant.

Generate a tailored cover letter using only facts supported by the
candidate's CV and the supplied job description.

Required output language: {language}

Candidate name:
{candidate_name}

Extracted job information:
- Company: {company}
- Job title: {job_title}
- Contact person: {contact_name}
- Location: {location}

Critical rules:

1. Never invent experience, qualifications, projects, certificates,
   achievements, language levels, dates or technical skills.
2. Do not claim that the candidate possesses a missing requirement.
3. Use specific evidence from the CV whenever possible.
4. Avoid generic phrases and excessive praise.
5. Keep the letter professional and concise.
6. Do not include a postal address block.
7. If a contact person is available, address that person.
8. For German:
   - use formal professional German,
   - use "Sehr geehrte Frau" or "Sehr geehrter Herr" only when the
     person's gender is clear,
   - otherwise use "Guten Tag [full name]" or
     "Sehr geehrte Damen und Herren".
9. For English:
   - use "Dear [full name]" when available,
   - otherwise use "Dear Hiring Team".
10. Put uncertainty or unsupported information in the warnings list.
11. Return only JSON matching the supplied schema.
12. Do not include markdown.

JSON schema:

{schema_text}

--- START CV ---

{cv_text}

--- END CV ---

--- START JOB DESCRIPTION ---

{job_text}

--- END JOB DESCRIPTION ---
""".strip()


# ==================================================
# TAILORED-CV PROMPT
# ==================================================
def build_tailored_cv_prompt(
    cv_text: str,
    job_text: str,
    job_details: dict,
    language: str,
) -> str:
    """
    Create instructions for tailoring a CV without
    introducing unsupported information.
    """

    schema_text = json.dumps(
        TailoredCVResult.model_json_schema(),
        indent=2,
        ensure_ascii=False,
    )

    company = job_details.get(
        "company",
        "",
    )

    job_title = job_details.get(
        "job_title",
        "",
    )

    required_skills = job_details.get(
        "required_skills",
        [],
    )

    preferred_skills = job_details.get(
        "preferred_skills",
        [],
    )

    return f"""
You are a careful CV editor.

Create a tailored CV draft for the supplied job using only facts
already present in the candidate's original CV.

Output language: {language}

Target company:
{company}

Target role:
{job_title}

Required skills:
{required_skills}

Preferred skills:
{preferred_skills}

Critical rules:

1. Never invent skills, employment, responsibilities, dates,
   education, projects, certificates, language levels,
   achievements or numerical results.
2. You may reorganize, shorten and professionally rewrite
   existing CV information.
3. Include a technical skill only when it appears in the
   original CV.
4. Do not copy missing job requirements into the CV.
5. Preserve employers, education providers, dates and
   qualification names accurately.
6. Suggested experience and project entries must be based
   directly on the original CV.
7. Prefer job-relevant evidence over unrelated information.
8. Use concise ATS-readable wording.
9. Avoid tables, columns, icons and decorative formatting.
10. Keep warnings for anything uncertain or incomplete.
11. Return only JSON matching the supplied schema.
12. Do not include markdown outside the JSON.

JSON schema:

{schema_text}

--- START ORIGINAL CV ---

{cv_text}

--- END ORIGINAL CV ---

--- START JOB DESCRIPTION ---

{job_text}

--- END JOB DESCRIPTION ---
""".strip()


# ==================================================
# JOB EXTRACTION
# ==================================================
def extract_job_details_with_ai(
    job_text: str,
) -> dict:
    """
    Extract structured job details using Ollama.
    """

    cleaned_job_text = job_text.strip()

    if not cleaned_job_text:
        raise ValueError(
            "The job-description text is empty."
        )

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": build_job_extraction_prompt(
                    cleaned_job_text
                ),
            }
        ],
        format=JobDetails.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    response_text = (
        response.message.content.strip()
    )

    if not response_text:
        raise ValueError(
            "The local AI returned an empty response."
        )

    try:
        extracted_details = (
            JobDetails.model_validate_json(
                response_text
            )
        )

    except ValidationError as error:
        raise ValueError(
            "The local AI response did not match "
            "the required job-details structure."
        ) from error

    return extracted_details.model_dump()


# ==================================================
# CV RECOMMENDATIONS
# ==================================================
def generate_cv_recommendations(
    cv_text: str,
    job_text: str,
) -> dict:
    """
    Generate evidence-based CV recommendations using Ollama.
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

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": build_cv_recommendation_prompt(
                    cv_text=cleaned_cv_text,
                    job_text=cleaned_job_text,
                ),
            }
        ],
        format=CVRecommendations.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    response_text = (
        response.message.content.strip()
    )

    if not response_text:
        raise ValueError(
            "The local AI returned no CV recommendations."
        )

    try:
        recommendations = (
            CVRecommendations.model_validate_json(
                response_text
            )
        )

    except ValidationError as error:
        raise ValueError(
            "The local AI recommendations did not match "
            "the required structure."
        ) from error

    return recommendations.model_dump()


# ==================================================
# COVER-LETTER GENERATION
# ==================================================
def generate_cover_letter(
    cv_text: str,
    job_text: str,
    job_details: dict,
    language: str,
    candidate_name: str,
) -> dict:
    """
    Generate a structured cover letter using Ollama.
    """

    cleaned_cv_text = cv_text.strip()
    cleaned_job_text = job_text.strip()
    cleaned_candidate_name = (
        candidate_name.strip()
    )

    if not cleaned_cv_text:
        raise ValueError(
            "The CV text is empty."
        )

    if not cleaned_job_text:
        raise ValueError(
            "The job-description text is empty."
        )

    if not cleaned_candidate_name:
        raise ValueError(
            "The candidate name is required."
        )

    if language not in {
        "English",
        "German",
    }:
        raise ValueError(
            "The cover-letter language must be "
            "English or German."
        )

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": build_cover_letter_prompt(
                    cv_text=cleaned_cv_text,
                    job_text=cleaned_job_text,
                    job_details=job_details,
                    language=language,
                    candidate_name=(
                        cleaned_candidate_name
                    ),
                ),
            }
        ],
        format=CoverLetterResult.model_json_schema(),
        options={
            "temperature": 0.2,
        },
    )

    response_text = (
        response.message.content.strip()
    )

    if not response_text:
        raise ValueError(
            "The local AI returned an empty cover letter."
        )

    try:
        cover_letter = (
            CoverLetterResult.model_validate_json(
                response_text
            )
        )

    except ValidationError as error:
        raise ValueError(
            "The local AI cover letter did not match "
            "the required structure."
        ) from error

    return cover_letter.model_dump()


# ==================================================
# TAILORED-CV GENERATION
# ==================================================
def generate_tailored_cv(
    cv_text: str,
    job_text: str,
    job_details: dict,
    language: str,
) -> dict:
    """
    Generate a structured, job-tailored CV using Ollama.
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

    if language not in {
        "English",
        "German",
    }:
        raise ValueError(
            "The CV language must be English or German."
        )

    response = chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": build_tailored_cv_prompt(
                    cv_text=cleaned_cv_text,
                    job_text=cleaned_job_text,
                    job_details=job_details,
                    language=language,
                ),
            }
        ],
        format=TailoredCVResult.model_json_schema(),
        options={
            "temperature": 0.1,
        },
    )

    response_text = (
        response.message.content.strip()
    )

    if not response_text:
        raise ValueError(
            "The local AI returned an empty tailored CV."
        )

    try:
        tailored_cv = (
            TailoredCVResult.model_validate_json(
                response_text
            )
        )

    except ValidationError as error:
        raise ValueError(
            "The local AI tailored CV did not match "
            "the required structure."
        ) from error

    return tailored_cv.model_dump()