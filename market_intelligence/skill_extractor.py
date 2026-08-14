from dataclasses import dataclass, field
import re
from typing import Dict, List


@dataclass
class SkillExtractionResult:
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    matched_aliases: Dict[str, str] = field(default_factory=dict)

    def all_skills(self) -> List[str]:
        """
        Return required + preferred skills without duplicates.
        """

        result = []
        seen = set()

        for skill in self.required_skills + self.preferred_skills:
            key = skill.lower()

            if key not in seen:
                seen.add(key)
                result.append(skill)

        return result


class UniversalSkillExtractor:
    """
    Universal deterministic skill extractor.

    The extractor is intentionally not limited to Data Engineering.
    It supports skills from multiple industries and professions.

    A future AI/LLM fallback can handle skills that are not yet present
    in this deterministic taxonomy.
    """

    SKILL_ALIASES: Dict[str, List[str]] = {

        # --------------------------------------------------------------
        # Programming
        # --------------------------------------------------------------
        "Python": [
            "python",
        ],
        "SQL": [
            "sql",
        ],
        "Java": [
            "java",
        ],
        "C++": [
            "c++",
            "cpp",
        ],
        "JavaScript": [
            "javascript",
        ],
        "TypeScript": [
            "typescript",
        ],

        # --------------------------------------------------------------
        # Data Engineering
        # --------------------------------------------------------------
        "Apache Spark": [
            "apache spark",
            "spark",
        ],
        "PySpark": [
            "pyspark",
        ],
        "Apache Kafka": [
            "apache kafka",
            "kafka",
        ],
        "Apache Airflow": [
            "apache airflow",
            "airflow",
        ],
        "dbt": [
            "dbt",
            "data build tool",
        ],
        "BigQuery": [
            "bigquery",
            "google bigquery",
        ],
        "Snowflake": [
            "snowflake",
        ],
        "Databricks": [
            "databricks",
        ],
        "PostgreSQL": [
            "postgresql",
            "postgres",
        ],
        "MySQL": [
            "mysql",
        ],
        "MongoDB": [
            "mongodb",
        ],
        "ETL": [
            "etl",
        ],
        "ELT": [
            "elt",
        ],
        "Data Warehousing": [
            "data warehouse",
            "data warehousing",
        ],

        # --------------------------------------------------------------
        # Cloud / DevOps
        # --------------------------------------------------------------
        "Google Cloud Platform": [
            "google cloud platform",
            "google cloud",
            "gcp",
        ],
        "AWS": [
            "amazon web services",
            "aws",
        ],
        "Microsoft Azure": [
            "microsoft azure",
            "azure",
        ],
        "Docker": [
            "docker",
        ],
        "Kubernetes": [
            "kubernetes",
            "k8s",
        ],
        "Terraform": [
            "terraform",
        ],
        "Git": [
            "git",
        ],
        "CI/CD": [
            "ci/cd",
            "continuous integration",
            "continuous delivery",
            "continuous deployment",
        ],

        # --------------------------------------------------------------
        # AI / Machine Learning
        # --------------------------------------------------------------
        "Machine Learning": [
            "machine learning",
        ],
        "Deep Learning": [
            "deep learning",
        ],
        "PyTorch": [
            "pytorch",
        ],
        "TensorFlow": [
            "tensorflow",
        ],
        "Scikit-learn": [
            "scikit-learn",
            "sklearn",
        ],
        "Natural Language Processing": [
            "natural language processing",
            "nlp",
        ],
        "Computer Vision": [
            "computer vision",
        ],
        "Generative AI": [
            "generative ai",
            "genai",
            "gen ai",
        ],
        "Large Language Models": [
            "large language model",
            "large language models",
            "llm",
            "llms",
        ],
        "MLflow": [
            "mlflow",
        ],

        # --------------------------------------------------------------
        # Automotive
        # --------------------------------------------------------------
        "AUTOSAR": [
            "autosar",
        ],
        "CAN Bus": [
            "can bus",
            "can-bus",
            "controller area network",
        ],
        "CANoe": [
            "canoe",
        ],
        "ECU": [
            "ecu",
            "electronic control unit",
        ],
        "ADAS": [
            "adas",
            "advanced driver assistance systems",
        ],
        "ISO 26262": [
            "iso 26262",
        ],
        "MATLAB": [
            "matlab",
        ],
        "Simulink": [
            "simulink",
        ],
        "Embedded Systems": [
            "embedded systems",
            "embedded system",
        ],
        "Functional Safety": [
            "functional safety",
            "funktionale sicherheit",
        ],

        # --------------------------------------------------------------
        # Business Intelligence
        # --------------------------------------------------------------
        "Microsoft Excel": [
            "microsoft excel",
            "ms excel",
            "excel",
        ],
        "Power BI": [
            "power bi",
            "powerbi",
        ],
        "Tableau": [
            "tableau",
        ],
        "SAP": [
            "sap",
        ],
        "Salesforce": [
            "salesforce",
        ],

        # --------------------------------------------------------------
        # Hospitality
        # --------------------------------------------------------------
        "Customer Service": [
            "customer service",
            "customer support",
            "guest service",
            "guest services",
            "kundenservice",
            "kundenbetreuung",
            "gästebetreuung",
        ],
        "Reservation Management": [
            "reservation management",
            "reservation system",
            "reservation systems",
            "reservations",
            "reservierung",
            "reservierungen",
            "reservierungssystem",
            "reservierungssysteme",
            "reservierungssystemen",
            "reservierungsmanagement",
        ],
        "Front Office": [
            "front office",
            "rezeption",
            "empfang",
        ],
        "Guest Relations": [
            "guest relations",
            "guest experience",
            "gästekontakt",
        ],
        "Housekeeping": [
            "housekeeping",
        ],
        "Food Preparation": [
            "food preparation",
            "food prep",
            "speisenzubereitung",
        ],
        "POS Systems": [
            "pos system",
            "pos systems",
            "point of sale",
            "kassensystem",
            "kassensysteme",
        ],

        # --------------------------------------------------------------
        # Sales
        # --------------------------------------------------------------
        "Business Development": [
            "business development",
            "geschäftsentwicklung",
        ],
        "Account Management": [
            "account management",
            "key account management",
            "kundenmanagement",
        ],
        "CRM": [
            "customer relationship management",
            "crm",
        ],
        "Lead Generation": [
            "lead generation",
            "leadgenerierung",
        ],
        "Sales": [
            "sales",
            "vertrieb",
        ],

        # --------------------------------------------------------------
        # Marketing
        # --------------------------------------------------------------
        "SEO": [
            "search engine optimization",
            "search engine optimisation",
            "seo",
        ],
        "SEM": [
            "search engine marketing",
            "sem",
        ],
        "Content Marketing": [
            "content marketing",
        ],
        "Social Media Marketing": [
            "social media marketing",
        ],

        # --------------------------------------------------------------
        # Human Resources
        # --------------------------------------------------------------
        "Recruitment": [
            "recruitment",
            "recruiting",
            "personalbeschaffung",
        ],
        "Talent Acquisition": [
            "talent acquisition",
        ],
        "HRIS": [
            "hris",
            "human resources information system",
        ],
        "Payroll": [
            "payroll",
            "lohnabrechnung",
            "gehaltsabrechnung",
        ],

        # --------------------------------------------------------------
        # Finance / Accounting
        # --------------------------------------------------------------
        "Accounting": [
            "accounting",
            "buchhaltung",
        ],
        "Financial Reporting": [
            "financial reporting",
            "finanzberichterstattung",
        ],
        "Accounts Payable": [
            "accounts payable",
            "kreditorenbuchhaltung",
        ],
        "Accounts Receivable": [
            "accounts receivable",
            "debitorenbuchhaltung",
        ],
        "Controlling": [
            "controlling",
        ],

        # --------------------------------------------------------------
        # Logistics / Supply Chain
        # --------------------------------------------------------------
        "Supply Chain Management": [
            "supply chain management",
            "supply chain",
        ],
        "Warehouse Management": [
            "warehouse management",
            "lagerverwaltung",
        ],
        "Inventory Management": [
            "inventory management",
            "bestandsmanagement",
        ],
        "Procurement": [
            "procurement",
            "beschaffung",
            "einkauf",
        ],
        "Logistics": [
            "logistics",
            "logistik",
        ],

        # --------------------------------------------------------------
        # Engineering / General
        # --------------------------------------------------------------
        "CATIA": [
            "catia",
        ],
        "SolidWorks": [
            "solidworks",
        ],
        "CAD": [
            "computer aided design",
            "computer-aided design",
            "cad",
        ],

        # --------------------------------------------------------------
        # Professional / Soft Skills
        # --------------------------------------------------------------
        "Communication": [
            "communication skills",
            "strong communication",
            "communication",
            "kommunikationsfähigkeit",
            "kommunikation",
        ],
        "Teamwork": [
            "teamwork",
            "team player",
            "teamfähigkeit",
        ],
        "Problem Solving": [
            "problem solving",
            "problem-solving",
            "problemlösung",
            "problemlösungsfähigkeit",
        ],
        "Leadership": [
            "leadership",
            "führungserfahrung",
            "führungskompetenz",
        ],
        "Project Management": [
            "project management",
            "projektmanagement",
        ],
        "Agile": [
            "agile",
            "agile methodology",
            "agile methodologies",
        ],
        "Scrum": [
            "scrum",
        ],
    }

    PREFERRED_CUES = [
        "nice to have",
        "nice-to-have",
        "preferred",
        "preferably",
        "advantage",
        "advantageous",
        "would be a plus",
        "is a plus",
        "plus",
        "desirable",
        "optional",
        "not required",
        "bonus",
        "von vorteil",
        "wünschenswert",
        "wünschenswert sind",
        "idealerweise",
    ]

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join((text or "").lower().split())

    @staticmethod
    def _contains(text: str, phrase: str) -> bool:
        """
        Match complete skill names/aliases while avoiding accidental
        partial-word matches.
        """

        text = text.lower()
        phrase = phrase.lower()

        pattern = (
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)"
        )

        return re.search(pattern, text) is not None

    def _find_skill(
        self,
        text: str,
        canonical_skill: str,
        aliases: List[str],
    ) -> str | None:
        """
        Return the matching alias if a skill is present.
        """

        for alias in aliases:
            if self._contains(text, alias):
                return alias

        return None

    def _is_preferred_context(self, text: str) -> bool:
        normalized = self._normalize(text)

        return any(
            self._contains(normalized, cue)
            for cue in self.PREFERRED_CUES
        )

    @staticmethod
    def _split_into_segments(text: str) -> List[str]:
        """
        Split a job description into manageable requirement segments.
        """

        if not text:
            return []

        segments = re.split(
            r"(?<=[.!?;])\s+|\n+",
            text,
        )

        return [
            segment.strip()
            for segment in segments
            if segment.strip()
        ]

    def extract(
        self,
        text: str,
        job_title: str = "",
    ) -> SkillExtractionResult:
        """
        Extract required and preferred skills.

        Skills found in the job title are treated as required.

        Skills occurring in sentences containing cues such as
        'nice to have', 'preferred', 'von Vorteil', etc. are treated
        as preferred.

        If the same skill occurs as both required and preferred,
        required takes precedence.
        """

        required_skills: List[str] = []
        preferred_skills: List[str] = []
        matched_aliases: Dict[str, str] = {}

        # --------------------------------------------------------------
        # Step 1: Skills explicitly present in job title
        # --------------------------------------------------------------
        normalized_title = self._normalize(job_title)

        if normalized_title:
            for canonical_skill, aliases in self.SKILL_ALIASES.items():
                matched_alias = self._find_skill(
                    normalized_title,
                    canonical_skill,
                    aliases,
                )

                if matched_alias:
                    if canonical_skill not in required_skills:
                        required_skills.append(canonical_skill)

                    matched_aliases[canonical_skill] = matched_alias

        # --------------------------------------------------------------
        # Step 2: Process individual description segments
        # --------------------------------------------------------------
        for segment in self._split_into_segments(text):

            normalized_segment = self._normalize(segment)

            preferred_context = self._is_preferred_context(
                normalized_segment
            )

            for canonical_skill, aliases in self.SKILL_ALIASES.items():

                matched_alias = self._find_skill(
                    normalized_segment,
                    canonical_skill,
                    aliases,
                )

                if not matched_alias:
                    continue

                matched_aliases[canonical_skill] = matched_alias

                if preferred_context:

                    # Required always takes precedence.
                    if canonical_skill not in required_skills:
                        if canonical_skill not in preferred_skills:
                            preferred_skills.append(canonical_skill)

                else:

                    if canonical_skill not in required_skills:
                        required_skills.append(canonical_skill)

                    if canonical_skill in preferred_skills:
                        preferred_skills.remove(canonical_skill)

        return SkillExtractionResult(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            matched_aliases=matched_aliases,
        )
