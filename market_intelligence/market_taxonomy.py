from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, List


@dataclass(frozen=True)
class MarketClassification:
    job_family: str
    subcategory: str
    matched_keyword: str = ""


# User-facing Job Market Intelligence taxonomy.
# This sits above the existing baseline classifier so the current
# database schema and earlier analytics remain backward-compatible.
MARKET_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Automotive & Mobility": {
        "Automotive Software Engineer": [
            "automotive software engineer",
            "automotive software developer",
            "vehicle software engineer",
            "automotive software",
        ],
        "ADAS / Autonomous Driving Engineer": [
            "adas engineer",
            "autonomous driving engineer",
            "autonomous vehicle engineer",
            "automated driving engineer",
            "adas",
            "autonomous driving",
        ],
        "Embedded Automotive Engineer": [
            "embedded automotive engineer",
            "automotive embedded engineer",
            "embedded software automotive",
            "autosar engineer",
            "autosar",
            "ecu software",
        ],
        "Vehicle Test & Validation Engineer": [
            "vehicle test engineer",
            "automotive test engineer",
            "validation engineer automotive",
            "vehicle validation",
            "hil engineer",
            "sil engineer",
            "canoe",
            "canalyzer",
        ],
        "Functional Safety Engineer": [
            "functional safety engineer",
            "functional safety",
            "iso 26262",
            "fusa engineer",
        ],
        "E/E Systems Engineer": [
            "e/e systems engineer",
            "vehicle electronics engineer",
            "automotive electronics engineer",
        ],
        "V2X / Connected Vehicle Engineer": [
            "v2x engineer",
            "connected vehicle engineer",
            "vehicle connectivity engineer",
            "automotive ethernet",
            "v2x",
        ],
        "Automotive Simulation Engineer": [
            "automotive simulation engineer",
            "vehicle simulation engineer",
            "simulation engineer automotive",
            "ipg carmaker",
            "carsim",
        ],
    },

    "AI Engineering": {
        "AI Engineer": [
            "ai engineer",
            "artificial intelligence engineer",
        ],
        "Applied AI Engineer": [
            "applied ai engineer",
            "applied artificial intelligence",
        ],
        "Generative AI Engineer": [
            "generative ai engineer",
            "genai engineer",
            "generative ai",
        ],
        "AI Platform Engineer": [
            "ai platform engineer",
            "ai infrastructure engineer",
            "ai systems engineer",
        ],
        "AI Solutions Engineer": [
            "ai solutions engineer",
            "ai solution architect",
            "ai solutions architect",
        ],
    },

    "Cloud Engineering & DevOps": {
        "Cloud Engineer": [
            "cloud engineer",
            "cloud infrastructure engineer",
        ],
        "Cloud Architect": [
            "cloud architect",
            "cloud solution architect",
            "cloud solutions architect",
        ],
        "DevOps Engineer": [
            "devops engineer",
            "devops specialist",
        ],
        "Platform Engineer": [
            "platform engineer",
            "platform engineering",
        ],
        "Site Reliability Engineer": [
            "site reliability engineer",
            "sre engineer",
            "site reliability",
        ],
        "Cloud Security Engineer": [
            "cloud security engineer",
            "cloud security specialist",
        ],
        "Cloud FinOps Engineer": [
            "finops engineer",
            "cloud finops",
            "cloud cost engineer",
        ],
    },

    "Machine Learning": {
        "Machine Learning Engineer": [
            "machine learning engineer",
            "ml engineer",
        ],
        "MLOps Engineer": [
            "mlops engineer",
            "ml ops engineer",
            "ml platform engineer",
        ],
        "Computer Vision Engineer": [
            "computer vision engineer",
            "computer vision scientist",
            "computer vision",
        ],
        "NLP Engineer": [
            "nlp engineer",
            "natural language processing engineer",
            "natural language processing",
        ],
        "Deep Learning Engineer": [
            "deep learning engineer",
            "deep learning scientist",
            "deep learning",
        ],
        "ML Research Engineer": [
            "machine learning research engineer",
            "ml research engineer",
            "research engineer machine learning",
        ],
        "Recommender Systems Engineer": [
            "recommender systems engineer",
            "recommendation systems engineer",
            "recommendation engineer",
        ],
    },

    "Data Science & Analytics": {
        "Data Scientist": [
            "data scientist",
            "applied data scientist",
        ],
        "Data Analyst": [
            "data analyst",
            "senior data analyst",
        ],
        "Business Intelligence Analyst": [
            "business intelligence analyst",
            "bi analyst",
            "business intelligence specialist",
        ],
        "Product Analyst": [
            "product analyst",
            "product analytics",
        ],
        "Marketing Analyst": [
            "marketing analyst",
            "marketing analytics",
        ],
        "Quantitative Analyst": [
            "quantitative analyst",
            "quant analyst",
        ],
        "Statistician": [
            "statistician",
            "statistical analyst",
        ],
    },

    "IT Support & Operations": {
        "IT Support Specialist": [
            "it support specialist",
            "it support engineer",
            "it support technician",
        ],
        "Help Desk Specialist": [
            "help desk",
            "helpdesk",
            "help desk specialist",
        ],
        "Service Desk Specialist": [
            "service desk",
            "service desk analyst",
            "service desk specialist",
        ],
        "Desktop Support Engineer": [
            "desktop support",
            "desktop support engineer",
            "workplace support",
        ],
        "Technical Support Engineer": [
            "technical support engineer",
            "technical support specialist",
        ],
        "NOC Engineer": [
            "noc engineer",
            "network operations center",
            "network operations centre",
        ],
    },

    "Software Development": {
        "Backend Developer": [
            "backend developer",
            "backend engineer",
            "back-end developer",
            "back-end engineer",
        ],
        "Frontend Developer": [
            "frontend developer",
            "frontend engineer",
            "front-end developer",
            "front-end engineer",
        ],
        "Full Stack Developer": [
            "full stack developer",
            "full-stack developer",
            "full stack engineer",
            "full-stack engineer",
        ],
        "Python Developer": [
            "python developer",
            "python software engineer",
        ],
        "Java Developer": [
            "java developer",
            "java software engineer",
        ],
        ".NET Developer": [
            ".net developer",
            "dotnet developer",
            ".net software engineer",
        ],
        "C / C++ Developer": [
            "c++ developer",
            "c++ software engineer",
            "c developer",
        ],
        "Mobile Developer": [
            "mobile developer",
            "android developer",
            "ios developer",
            "mobile engineer",
        ],
        "QA Automation Engineer": [
            "qa automation engineer",
            "test automation engineer",
            "software test automation",
        ],
        "Software Engineer": [
            "software engineer",
            "software developer",
            "application developer",
        ],
    },

    "Agentic AI & LLM": {
        "Agentic AI Engineer": [
            "agentic ai engineer",
            "agentic ai",
            "agentic systems engineer",
        ],
        "AI Agent Developer": [
            "ai agent developer",
            "ai agent engineer",
            "autonomous agent engineer",
            "multi-agent engineer",
            "multi agent engineer",
        ],
        "LLM Engineer": [
            "llm engineer",
            "large language model engineer",
            "language model engineer",
        ],
        "RAG Engineer": [
            "rag engineer",
            "retrieval augmented generation engineer",
            "retrieval-augmented generation",
            "retrieval augmented generation",
        ],
        "Conversational AI Engineer": [
            "conversational ai engineer",
            "conversation ai engineer",
            "chatbot engineer",
        ],
        "AI Workflow / Orchestration Engineer": [
            "ai workflow engineer",
            "llm orchestration engineer",
            "ai orchestration engineer",
            "langgraph",
            "crewai",
            "autogen",
        ],
    },

    "IT Administration & Infrastructure": {
        "System Administrator": [
            "system administrator",
            "systems administrator",
            "sysadmin",
        ],
        "Linux Administrator": [
            "linux administrator",
            "linux systems administrator",
        ],
        "Windows Administrator": [
            "windows administrator",
            "windows systems administrator",
        ],
        "Microsoft 365 Administrator": [
            "microsoft 365 administrator",
            "m365 administrator",
            "office 365 administrator",
        ],
        "Network Administrator": [
            "network administrator",
            "network admin",
        ],
        "IAM Administrator": [
            "iam administrator",
            "identity access administrator",
            "identity and access administrator",
        ],
        "Database Administrator": [
            "database administrator",
            "dba",
        ],
        "Endpoint Administrator": [
            "endpoint administrator",
            "intune administrator",
            "endpoint management administrator",
        ],
    },

    "Data Engineering": {
        "Databricks Consulting Engineer": [
            "databricks consulting engineer",
            "consulting engineer databricks",
        ],
        "Data Solutions Architect": [
            "databricks resident solutions architect",
            "resident solutions architect",
            "databricks solutions architect",
            "data solutions architect",
            "solutions architect databricks",
        ],
        "Data Engineer": [
            "data engineer",
        ],
        "Cloud Data Engineer": [
            "cloud data engineer",
            "gcp data engineer",
            "aws data engineer",
            "azure data engineer",
        ],
        "Data Platform Engineer": [
            "data platform engineer",
            "data infrastructure engineer",
        ],
        "Big Data Engineer": [
            "big data engineer",
            "big-data engineer",
        ],
        "ETL / ELT Engineer": [
            "etl engineer",
            "elt engineer",
            "data integration engineer",
        ],
        "Streaming Data Engineer": [
            "streaming data engineer",
            "real time data engineer",
            "real-time data engineer",
        ],
        "Data Warehouse Engineer": [
            "data warehouse engineer",
            "data warehousing engineer",
            "warehouse developer",
        ],
        "Analytics Engineer": [
            "analytics engineer",
        ],
    },

    "Cybersecurity": {
        "Security Engineer": [
            "security engineer",
            "cybersecurity engineer",
            "cyber security engineer",
        ],
        "SOC Analyst": [
            "soc analyst",
            "security operations center analyst",
            "security operations centre analyst",
        ],
        "Application Security Engineer": [
            "application security engineer",
            "appsec engineer",
            "application security",
        ],
        "Cloud Security Engineer": [
            "cloud security engineer",
        ],
        "IAM Engineer": [
            "iam engineer",
            "identity and access management engineer",
        ],
        "Penetration Tester": [
            "penetration tester",
            "pentester",
            "ethical hacker",
        ],
        "GRC Specialist": [
            "grc specialist",
            "governance risk compliance",
            "information security compliance",
        ],
        "Security Architect": [
            "security architect",
            "cybersecurity architect",
        ],
    },

    "Product & Project Management": {
        "Product Manager": [
            "product manager",
        ],
        "Technical Product Manager": [
            "technical product manager",
        ],
        "Product Owner": [
            "product owner",
        ],
        "Project Manager": [
            "project manager",
        ],
        "Technical Project Manager": [
            "technical project manager",
            "it project manager",
        ],
        "Program Manager": [
            "program manager",
            "programme manager",
        ],
        "Scrum Master": [
            "scrum master",
        ],
        "PMO Specialist": [
            "pmo specialist",
            "project management office",
        ],
    },

    "Finance & Accounting": {
        "Accountant": [
            "accountant",
        ],
        "Financial Analyst": [
            "financial analyst",
            "finance analyst",
        ],
        "FP&A Analyst": [
            "fp&a analyst",
            "financial planning and analysis",
        ],
        "Controller": [
            "controller",
            "financial controller",
        ],
        "Auditor": [
            "auditor",
            "internal audit",
        ],
        "Tax Specialist": [
            "tax specialist",
            "tax consultant",
            "tax accountant",
        ],
        "Treasury Specialist": [
            "treasury specialist",
            "treasury analyst",
        ],
        "Finance Manager": [
            "finance manager",
        ],
    },

    "Sales & Business Development": {
        "Sales Representative": [
            "sales representative",
            "sales specialist",
        ],
        "Account Executive": [
            "account executive",
        ],
        "Business Development Manager": [
            "business development manager",
            "business development executive",
        ],
        "Key Account Manager": [
            "key account manager",
        ],
        "Sales Manager": [
            "sales manager",
        ],
        "Sales Engineer": [
            "sales engineer",
            "solutions engineer sales",
        ],
        "Partnerships Manager": [
            "partnerships manager",
            "partner manager",
        ],
    },

    "Marketing & Communications": {
        "Digital Marketing Specialist": [
            "digital marketing specialist",
            "digital marketer",
        ],
        "SEO / SEM Specialist": [
            "seo specialist",
            "sem specialist",
            "search engine marketing",
        ],
        "Content Marketing Specialist": [
            "content marketing specialist",
            "content marketer",
        ],
        "Social Media Manager": [
            "social media manager",
        ],
        "Brand Manager": [
            "brand manager",
        ],
        "Product Marketing Manager": [
            "product marketing manager",
        ],
        "Marketing Analyst": [
            "marketing analyst",
        ],
        "Communications Specialist": [
            "communications specialist",
            "communications manager",
            "corporate communications",
        ],
    },

    "Human Resources": {
        "Recruiter": [
            "recruiter",
            "recruitment specialist",
        ],
        "Talent Acquisition Specialist": [
            "talent acquisition specialist",
            "talent acquisition manager",
        ],
        "HR Business Partner": [
            "hr business partner",
            "human resources business partner",
        ],
        "HR Generalist": [
            "hr generalist",
            "human resources generalist",
        ],
        "People Operations Specialist": [
            "people operations specialist",
            "people ops",
        ],
        "Learning & Development Specialist": [
            "learning and development specialist",
            "learning & development specialist",
            "l&d specialist",
        ],
        "Compensation & Benefits Specialist": [
            "compensation and benefits specialist",
            "compensation & benefits",
        ],
        "HR Administrator": [
            "hr administrator",
            "human resources administrator",
        ],
    },

    "Supply Chain & Logistics": {
        "Supply Chain Analyst": [
            "supply chain analyst",
        ],
        "Logistics Coordinator": [
            "logistics coordinator",
            "logistics specialist",
        ],
        "Procurement Specialist": [
            "procurement specialist",
            "procurement manager",
        ],
        "Buyer": [
            "strategic buyer",
            "technical buyer",
            "buyer",
        ],
        "Warehouse Operations": [
            "warehouse operations",
            "warehouse manager",
            "warehouse specialist",
        ],
        "Demand Planner": [
            "demand planner",
            "demand planning",
        ],
        "Transport Planner": [
            "transport planner",
            "transportation planner",
        ],
        "Inventory Specialist": [
            "inventory specialist",
            "inventory analyst",
        ],
    },

    "Manufacturing & Industrial Engineering": {
        "Manufacturing Engineer": [
            "manufacturing engineer",
        ],
        "Industrial Engineer": [
            "industrial engineer",
        ],
        "Process Engineer": [
            "process engineer",
        ],
        "Quality Engineer": [
            "quality engineer",
        ],
        "Production Engineer": [
            "production engineer",
        ],
        "Automation Engineer": [
            "automation engineer",
            "industrial automation engineer",
        ],
        "Mechanical Design Engineer": [
            "mechanical design engineer",
            "mechanical engineer",
        ],
        "Electrical Engineer": [
            "electrical engineer",
            "electronics engineer",
        ],
    },

    "Hospitality & Customer Service": {
        "Receptionist": [
            "receptionist",
            "hotel receptionist",
        ],
        "Front Office Employee": [
            "front office",
            "front desk",
        ],
        "Guest Service Specialist": [
            "guest service",
            "guest services",
        ],
        "Restaurant Service": [
            "waiter",
            "waitress",
            "restaurant server",
        ],
        "Chef / Cook": [
            "chef",
            "cook",
            "kitchen employee",
        ],
        "Housekeeping": [
            "housekeeping",
            "room attendant",
        ],
        "Customer Service Specialist": [
            "customer service specialist",
            "customer service representative",
        ],
        "Customer Success Specialist": [
            "customer success specialist",
            "customer success manager",
        ],
        "Call Center Specialist": [
            "call center",
            "contact center agent",
        ],
    },
}


LEGACY_FAMILY_FALLBACKS = {
    "Automotive": "Automotive & Mobility",
    "AI & Machine Learning": "AI Engineering",
    "Software Engineering": "Software Development",
    "Cloud & DevOps": "Cloud Engineering & DevOps",
    "Hospitality": "Hospitality & Customer Service",
    "Sales": "Sales & Business Development",
    "Marketing": "Marketing & Communications",
    "Human Resources": "Human Resources",
    "Finance & Accounting": "Finance & Accounting",
    "Customer Support": "IT Support & Operations",
    "Logistics & Supply Chain": "Supply Chain & Logistics",
    "Mechanical Engineering": "Manufacturing & Industrial Engineering",
    "Electrical Engineering": "Manufacturing & Industrial Engineering",
}


def supported_market_families() -> List[str]:
    return list(MARKET_TAXONOMY.keys())


def subcategories_for_family(
    job_family: str | None,
) -> List[str]:
    if not job_family:
        return []

    return list(
        MARKET_TAXONOMY.get(
            job_family,
            {},
        ).keys()
    )


def _normalize(value: str) -> str:
    return " ".join(
        (value or "").casefold().strip().split()
    )


def _contains(
    text: str,
    keyword: str,
) -> bool:
    text = _normalize(text)
    keyword = _normalize(keyword)

    if not text or not keyword:
        return False

    if any(char in keyword for char in ["+", "/", ".", "#", "&"]):
        return keyword in text

    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, text) is not None


def classify_market_job(
    job_title: str,
    description: str = "",
    legacy_job_family: str = "",
    legacy_occupation: str = "",
) -> MarketClassification:
    title = _normalize(job_title)
    description_text = _normalize(description)
    legacy_occupation_text = _normalize(
        legacy_occupation
    )

    candidates = []

    for family_index, (family, subcategories) in enumerate(
        MARKET_TAXONOMY.items()
    ):
        for subcategory_index, (
            subcategory,
            keywords,
        ) in enumerate(
            subcategories.items()
        ):
            best_score = 0
            best_keyword = ""

            for keyword in sorted(
                keywords,
                key=len,
                reverse=True,
            ):
                score = 0

                if _contains(title, keyword):
                    score = 100 + len(keyword)
                elif (
                    legacy_occupation_text
                    and _contains(
                        legacy_occupation_text,
                        keyword,
                    )
                ):
                    score = 80 + len(keyword)
                elif _contains(
                    description_text,
                    keyword,
                ):
                    score = 10 + len(keyword)

                if score > best_score:
                    best_score = score
                    best_keyword = keyword

            if best_score > 0:
                candidates.append(
                    (
                        best_score,
                        -family_index,
                        -subcategory_index,
                        family,
                        subcategory,
                        best_keyword,
                    )
                )

    if candidates:
        candidates.sort(
            reverse=True
        )

        (
            _,
            _,
            _,
            family,
            subcategory,
            keyword,
        ) = candidates[0]

        return MarketClassification(
            job_family=family,
            subcategory=subcategory,
            matched_keyword=keyword,
        )

    legacy_family = (
        legacy_job_family or ""
    ).strip()

    # Data & Analytics needs a finer fallback based on title.
    if legacy_family.casefold() == "data & analytics":
        combined = f"{title} {legacy_occupation_text}"

        if any(
            token in combined
            for token in [
                "engineer",
                "etl",
                "warehouse",
                "platform",
                "analytics engineer",
            ]
        ):
            return MarketClassification(
                job_family="Data Engineering",
                subcategory=(
                    legacy_occupation.strip()
                    or job_title.strip()
                    or "Other Data Engineering Role"
                ),
            )

        return MarketClassification(
            job_family="Data Science & Analytics",
            subcategory=(
                legacy_occupation.strip()
                or job_title.strip()
                or "Other Data & Analytics Role"
            ),
        )

    fallback = LEGACY_FAMILY_FALLBACKS.get(
        legacy_family
    )

    if fallback:
        return MarketClassification(
            job_family=fallback,
            subcategory=(
                legacy_occupation.strip()
                or job_title.strip()
                or "Other"
            ),
        )

    return MarketClassification(
        job_family="Other",
        subcategory=(
            legacy_occupation.strip()
            or job_title.strip()
            or "Other"
        ),
    )
