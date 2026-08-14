from dataclasses import dataclass, field
import re
from typing import Dict, List, Tuple


@dataclass
class ClassificationResult:
    industry: str
    job_family: str
    occupation: str
    seniority: str
    confidence: float
    matched_keywords: List[str] = field(default_factory=list)


class UniversalJobClassifier:
    """
    Universal baseline classifier for job advertisements.

    It is not restricted to Data Engineering.
    """

    JOB_FAMILIES: Dict[str, Dict] = {
        "Data & Analytics": {
            "industry": "Information Technology",
            "keywords": [
                "data engineer",
                "data analyst",
                "analytics engineer",
                "business intelligence",
                "bi developer",
                "data warehouse",
                "etl",
                "elt",
                "sql",
                "bigquery",
                "snowflake",
                "databricks",
                "apache spark",
                "pyspark",
                "airflow",
                "dbt",
            ],
        },

        "AI & Machine Learning": {
            "industry": "Artificial Intelligence",
            "keywords": [
                "machine learning engineer",
                "ml engineer",
                "ai engineer",
                "artificial intelligence",
                "machine learning",
                "deep learning",
                "computer vision",
                "nlp engineer",
                "natural language processing",
                "llm engineer",
                "generative ai",
                "mlops",
                "pytorch",
                "tensorflow",
            ],
        },

        "Software Engineering": {
            "industry": "Information Technology",
            "keywords": [
                "software engineer",
                "software developer",
                "backend developer",
                "frontend developer",
                "full stack developer",
                "full-stack developer",
                "web developer",
                "java developer",
                "python developer",
                "c++ developer",
                "javascript developer",
                "typescript developer",
                "react developer",
                "developer",
                "software development",
            ],
        },

        "Cloud & DevOps": {
            "industry": "Information Technology",
            "keywords": [
                "cloud engineer",
                "devops engineer",
                "site reliability engineer",
                "sre",
                "platform engineer",
                "cloud architect",
                "kubernetes",
                "terraform",
                "docker",
                "aws",
                "azure",
                "google cloud",
                "gcp",
                "ci/cd",
            ],
        },

        "Automotive": {
            "industry": "Automotive",
            "keywords": [
                "automotive engineer",
                "automotive software",
                "vehicle",
                "autosar",
                "adas",
                "can bus",
                "canoe",
                "ecu",
                "embedded automotive",
                "iso 26262",
                "functional safety",
                "automotive ethernet",
                "simulink",
                "matlab",
            ],
        },

        "Hospitality": {
            "industry": "Hospitality",
            "keywords": [
                "receptionist",
                "front office",
                "hotel",
                "hospitality",
                "guest service",
                "guest services",
                "reservation",
                "restaurant",
                "waiter",
                "waitress",
                "chef",
                "cook",
                "kitchen",
                "housekeeping",
                "bartender",
            ],
        },

        "Sales": {
            "industry": "Sales",
            "keywords": [
                "sales representative",
                "sales manager",
                "account executive",
                "business development",
                "sales consultant",
                "inside sales",
                "field sales",
                "key account manager",
                "sales specialist",
                "sales associate",
            ],
        },

        "Marketing": {
            "industry": "Marketing",
            "keywords": [
                "marketing manager",
                "digital marketing",
                "content marketing",
                "seo specialist",
                "sem specialist",
                "social media manager",
                "brand manager",
                "marketing specialist",
                "marketing analyst",
                "campaign manager",
            ],
        },

        "Human Resources": {
            "industry": "Human Resources",
            "keywords": [
                "human resources",
                "hr manager",
                "hr specialist",
                "hr business partner",
                "recruiter",
                "talent acquisition",
                "people operations",
                "personnel manager",
                "recruitment specialist",
            ],
        },

        "Finance & Accounting": {
            "industry": "Finance",
            "keywords": [
                "accountant",
                "controller",
                "financial analyst",
                "finance manager",
                "bookkeeper",
                "auditor",
                "tax consultant",
                "accounting",
                "financial reporting",
                "accounts payable",
                "accounts receivable",
            ],
        },

        "Customer Support": {
            "industry": "Customer Service",
            "keywords": [
                "customer support",
                "customer service",
                "support specialist",
                "technical support",
                "service desk",
                "help desk",
                "call center",
                "customer success",
                "first level support",
                "1st level support",
            ],
        },

        "Logistics & Supply Chain": {
            "industry": "Logistics",
            "keywords": [
                "logistics",
                "supply chain",
                "warehouse",
                "inventory",
                "procurement",
                "transportation",
                "freight",
                "shipping",
                "warehouse manager",
                "supply chain analyst",
            ],
        },

        "Mechanical Engineering": {
            "industry": "Engineering",
            "keywords": [
                "mechanical engineer",
                "mechanical engineering",
                "cad engineer",
                "solidworks",
                "catia",
                "manufacturing engineer",
                "product design engineer",
                "thermodynamics",
            ],
        },

        "Electrical Engineering": {
            "industry": "Engineering",
            "keywords": [
                "electrical engineer",
                "electrical engineering",
                "electronics engineer",
                "embedded systems",
                "pcb",
                "circuit design",
                "power electronics",
                "control systems",
            ],
        },

        "Healthcare": {
            "industry": "Healthcare",
            "keywords": [
                "nurse",
                "doctor",
                "physician",
                "medical assistant",
                "healthcare",
                "pharmacist",
                "physiotherapist",
                "clinical",
                "patient care",
            ],
        },
    }

    OCCUPATION_PATTERNS: List[Tuple[str, str]] = [
        ("automotive software engineer", "Automotive Software Engineer"),

        ("data engineer", "Data Engineer"),
        ("data analyst", "Data Analyst"),
        ("analytics engineer", "Analytics Engineer"),
        ("business intelligence", "Business Intelligence Specialist"),

        ("machine learning engineer", "Machine Learning Engineer"),
        ("ml engineer", "Machine Learning Engineer"),
        ("ai engineer", "AI Engineer"),
        ("llm engineer", "LLM Engineer"),

        ("software engineer", "Software Engineer"),
        ("software developer", "Software Developer"),
        ("python developer", "Python Developer"),
        ("java developer", "Java Developer"),
        ("backend developer", "Backend Developer"),
        ("frontend developer", "Frontend Developer"),
        ("full stack developer", "Full Stack Developer"),
        ("full-stack developer", "Full Stack Developer"),

        ("cloud engineer", "Cloud Engineer"),
        ("devops engineer", "DevOps Engineer"),
        ("platform engineer", "Platform Engineer"),
        ("site reliability engineer", "Site Reliability Engineer"),

        ("automotive engineer", "Automotive Engineer"),

        ("receptionist", "Receptionist"),
        ("front office", "Front Office Employee"),
        ("chef", "Chef"),
        ("cook", "Cook"),
        ("waiter", "Waiter"),
        ("waitress", "Waitress"),

        ("sales manager", "Sales Manager"),
        ("sales representative", "Sales Representative"),
        ("account executive", "Account Executive"),
        ("key account manager", "Key Account Manager"),

        ("marketing manager", "Marketing Manager"),
        ("marketing specialist", "Marketing Specialist"),

        ("recruiter", "Recruiter"),
        ("hr manager", "HR Manager"),
        ("hr specialist", "HR Specialist"),

        ("accountant", "Accountant"),
        ("financial analyst", "Financial Analyst"),
        ("controller", "Controller"),

        ("customer support", "Customer Support Specialist"),
        ("customer service", "Customer Service Specialist"),
        ("technical support", "Technical Support Specialist"),

        ("mechanical engineer", "Mechanical Engineer"),
        ("electrical engineer", "Electrical Engineer"),

        ("nurse", "Nurse"),
        ("doctor", "Doctor"),
        ("physician", "Physician"),
    ]

    SENIORITY_PATTERNS = {
        "Internship": [
            "intern",
            "internship",
            "working student",
            "werkstudent",
        ],
        "Entry-level": [
            "entry level",
            "entry-level",
            "graduate",
            "trainee",
            "junior",
        ],
        "Senior": [
            "senior",
            "sr.",
            "sr ",
            "lead ",
            "principal",
            "staff engineer",
        ],
        "Management": [
            "head of",
            "director",
            "vice president",
            "vp ",
            "chief ",
        ],
    }

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join((text or "").lower().split())

    @staticmethod
    def _contains(text: str, keyword: str) -> bool:
        text = text.lower()
        keyword = keyword.lower()

        if any(char in keyword for char in ["+", "/", ".", "#"]):
            return keyword in text

        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
        return re.search(pattern, text) is not None

    def _score_job_families(
        self,
        job_title: str,
        description: str,
    ) -> Tuple[Dict[str, int], Dict[str, List[str]]]:

        normalized_title = self._normalize(job_title)
        normalized_description = self._normalize(description)

        scores = {}
        matches = {}

        for family, config in self.JOB_FAMILIES.items():
            family_score = 0
            family_matches = []

            for keyword in config["keywords"]:
                if self._contains(normalized_title, keyword):
                    family_score += 4

                    if keyword not in family_matches:
                        family_matches.append(keyword)

                elif self._contains(normalized_description, keyword):
                    family_score += 1

                    if keyword not in family_matches:
                        family_matches.append(keyword)

            scores[family] = family_score
            matches[family] = family_matches

        return scores, matches

    def _detect_occupation(
        self,
        job_title: str,
        description: str,
    ) -> str:

        normalized_title = self._normalize(job_title)
        normalized_description = self._normalize(description)

        for pattern, occupation in self.OCCUPATION_PATTERNS:
            if self._contains(normalized_title, pattern):
                return occupation

        for pattern, occupation in self.OCCUPATION_PATTERNS:
            if self._contains(normalized_description, pattern):
                return occupation

        if job_title.strip():
            return job_title.strip()

        return "Unknown"

    def _detect_seniority(
        self,
        job_title: str,
        description: str,
    ) -> str:

        combined = self._normalize(
            f"{job_title} {description}"
        )

        order = [
            "Management",
            "Internship",
            "Entry-level",
            "Senior",
        ]

        for level in order:
            for keyword in self.SENIORITY_PATTERNS[level]:
                if self._contains(combined, keyword):
                    return level

        return "Not specified"

    @staticmethod
    def _calculate_confidence(
        winner_score: int,
        second_score: int,
    ) -> float:

        if winner_score <= 0:
            return 0.20

        separation = winner_score - second_score

        confidence = (
            0.45
            + min(winner_score, 20) * 0.02
            + min(max(separation, 0), 10) * 0.02
        )

        return round(min(confidence, 0.95), 2)

    def classify(
        self,
        job_title: str,
        description: str = "",
    ) -> ClassificationResult:

        scores, matches = self._score_job_families(
            job_title=job_title,
            description=description,
        )

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        winning_family, winning_score = ranked[0]

        second_score = ranked[1][1] if len(ranked) > 1 else 0

        if winning_score == 0:
            return ClassificationResult(
                industry="Other",
                job_family="Other",
                occupation=self._detect_occupation(
                    job_title,
                    description,
                ),
                seniority=self._detect_seniority(
                    job_title,
                    description,
                ),
                confidence=0.20,
                matched_keywords=[],
            )

        industry = self.JOB_FAMILIES[
            winning_family
        ]["industry"]

        return ClassificationResult(
            industry=industry,
            job_family=winning_family,
            occupation=self._detect_occupation(
                job_title,
                description,
            ),
            seniority=self._detect_seniority(
                job_title,
                description,
            ),
            confidence=self._calculate_confidence(
                winning_score,
                second_score,
            ),
            matched_keywords=matches[winning_family],
        )
