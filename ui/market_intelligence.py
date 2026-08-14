import hashlib
from typing import List, Optional

import streamlit as st

from market_intelligence.cv_market_comparator import CVMarketComparator
from market_intelligence.cv_skill_bridge import CVSkillBridge
from market_intelligence.database import JobMarketDatabase
from market_intelligence.job_ranker import JobRanker
from market_intelligence.market_taxonomy import (
    classify_market_job,
    subcategories_for_family,
    supported_market_families,
)
from market_intelligence.skill_gap import SkillGapPrioritizer
from market_intelligence.statistics import MarketStatisticsEngine
from market_intelligence.technology_filter import (
    available_technologies,
    filter_jobs_by_technology,
)
from market_intelligence.trend_analysis import MarketTrendAnalyzer
from ui.market_refresh import render_market_refresh
from ui.snapshot_trends import render_snapshot_trends


# ==========================================================
# GENERAL HELPERS
# ==========================================================
def _parse_candidate_skills(
    raw_text: str,
) -> List[str]:
    """
    Convert comma/newline separated input into a clean,
    duplicate-free skill list.
    """

    if not raw_text:
        return []

    normalized = raw_text.replace(
        "\n",
        ",",
    )

    skills = []
    seen = set()

    for item in normalized.split(","):
        skill = item.strip()

        if not skill:
            continue

        key = skill.lower()

        if key not in seen:
            seen.add(key)
            skills.append(skill)

    return skills


def _format_percentage(
    value: float,
) -> str:
    return f"{value:.2f}%"


def _get_filter_options(
    jobs,
):
    countries = sorted(
        {
            job.country
            for job in jobs
            if job.country.strip()
        }
    )

    # Show the complete supported market taxonomy instead of
    # only families already present in the current local DB.
    job_families = supported_market_families()

    return countries, job_families


def _market_classification(
    job,
):
    return classify_market_job(
        job_title=job.job_title,
        description=job.description,
        legacy_job_family=job.job_family,
        legacy_occupation=job.occupation,
    )


def _filter_market_jobs(
    jobs,
    country: Optional[str] = None,
    market_family: Optional[str] = None,
    subcategory: Optional[str] = None,
):
    filtered = []

    for job in jobs:
        if (
            country
            and job.country.casefold()
            != country.casefold()
        ):
            continue

        classification = (
            _market_classification(
                job
            )
        )

        if (
            market_family
            and classification.job_family.casefold()
            != market_family.casefold()
        ):
            continue

        if (
            subcategory
            and classification.subcategory.casefold()
            != subcategory.casefold()
        ):
            continue

        filtered.append(
            job
        )

    return filtered


class _FilteredJobMarketDatabase:
    # Read-only analytics view over a filtered list of jobs.
    def __init__(
        self,
        source_database: JobMarketDatabase,
        jobs,
    ):
        self.source_database = (
            source_database
        )

        self.jobs = list(
            jobs
        )

    def get_all_jobs(
        self,
        limit: Optional[int] = None,
    ):
        if limit is None:
            return list(
                self.jobs
            )

        return list(
            self.jobs[:limit]
        )

    def __getattr__(
        self,
        name,
    ):
        return getattr(
            self.source_database,
            name,
        )


def _render_taxonomy_summary(
    jobs,
):
    classifications = [
        _market_classification(
            job
        )
        for job in jobs
    ]

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Jobs analysed",
        len(jobs),
    )

    col2.metric(
        "Companies",
        len(
            {
                job.company.strip().casefold()
                for job in jobs
                if job.company.strip()
            }
        ),
    )

    col3.metric(
        "Locations",
        len(
            {
                job.location.strip().casefold()
                for job in jobs
                if job.location.strip()
            }
        ),
    )

    col4.metric(
        "Roles",
        len(
            {
                item.subcategory.casefold()
                for item in classifications
                if item.subcategory.strip()
            }
        ),
    )


# ==========================================================
# CV → MARKET INTELLIGENCE BRIDGE
# ==========================================================
def _build_cv_hash(
    cv_text: str,
) -> str:
    """
    Create a stable identifier for the current analysed CV.

    This allows us to automatically refresh market skills when
    the user analyses a different CV without overwriting manual
    edits every Streamlit rerun.
    """

    cleaned = (
        cv_text or ""
    ).strip()

    if not cleaned:
        return ""

    return hashlib.sha256(
        cleaned.encode("utf-8")
    ).hexdigest()


def _sync_cv_skills_to_market(
    force: bool = False,
):
    """
    Read final_cv_text from the existing Job Agent session,
    extract normalized skills, and populate the Market
    Intelligence candidate-skill field.

    Automatic replacement happens when:
        - a new CV has been analysed, or
        - force=True.

    Manual edits remain intact during normal Streamlit reruns.
    """

    cv_text = (
        st.session_state.get(
            "final_cv_text",
            "",
        )
        or ""
    ).strip()

    if not cv_text:
        return None

    current_hash = _build_cv_hash(
        cv_text
    )

    previous_hash = (
        st.session_state.get(
            "market_cv_source_hash",
            "",
        )
        or ""
    )

    bridge = CVSkillBridge()

    profile = bridge.extract_skills(
        cv_text
    )

    if (
        force
        or current_hash != previous_hash
    ):
        st.session_state[
            "market_candidate_skills"
        ] = ", ".join(
            profile.skills
        )

        st.session_state[
            "market_cv_source_hash"
        ] = current_hash

        st.session_state[
            "market_cv_skill_count"
        ] = profile.skill_count

        st.session_state[
            "market_cv_matched_aliases"
        ] = profile.matched_aliases

    return profile


# ==========================================================
# MARKET SUMMARY
# ==========================================================
def _render_summary(
    statistics: MarketStatisticsEngine,
    job_family: Optional[str],
    country: Optional[str],
):
    summary = statistics.summary(
        job_family=job_family,
        country=country,
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Jobs analysed",
        summary["total_jobs"],
    )

    col2.metric(
        "Companies",
        summary["unique_companies"],
    )

    col3.metric(
        "Locations",
        summary["unique_locations"],
    )

    col4.metric(
        "Job families",
        summary["unique_job_families"],
    )


# ==========================================================
# TOP SKILLS
# ==========================================================
def _render_top_skills(
    statistics: MarketStatisticsEngine,
    job_family: Optional[str],
    country: Optional[str],
):
    st.subheader(
        "Top Market Skills"
    )

    required_only = st.checkbox(
        "Required skills only",
        value=False,
        key="market_required_only",
    )

    top_n = st.slider(
        "Number of skills",
        min_value=5,
        max_value=30,
        value=15,
        step=5,
        key="market_top_skill_count",
    )

    skills = statistics.top_skills(
        limit=top_n,
        required_only=required_only,
        job_family=job_family,
        country=country,
    )

    if not skills:
        st.info(
            "No skill statistics are available "
            "for the selected market."
        )
        return

    rows = []

    for index, item in enumerate(
        skills,
        start=1,
    ):
        rows.append(
            {
                "Rank": index,
                "Skill": item["name"],
                "Jobs": item["count"],
                "Demand": (
                    _format_percentage(
                        item["percentage"]
                    )
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ==========================================================
# MARKET BREAKDOWN
# ==========================================================
def _render_market_breakdown(
    statistics: MarketStatisticsEngine,
    job_family: Optional[str],
    country: Optional[str],
):
    st.subheader(
        "Market Breakdown"
    )

    col1, col2 = st.columns(2)

    # ------------------------------------------------------
    # WORK MODE
    # ------------------------------------------------------
    with col1:
        st.markdown(
            "#### Work Modes"
        )

        work_modes = statistics.work_modes(
            job_family=job_family,
            country=country,
        )

        if work_modes:
            st.dataframe(
                [
                    {
                        "Work mode": item[
                            "name"
                        ],
                        "Jobs": item[
                            "count"
                        ],
                        "Percentage": (
                            _format_percentage(
                                item[
                                    "percentage"
                                ]
                            )
                        ),
                    }
                    for item in work_modes
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.caption(
                "No work-mode information "
                "available."
            )

    # ------------------------------------------------------
    # LANGUAGES
    # ------------------------------------------------------
    with col2:
        st.markdown(
            "#### Languages"
        )

        languages = statistics.languages(
            job_family=job_family,
            country=country,
        )

        if languages:
            st.dataframe(
                [
                    {
                        "Language": item[
                            "name"
                        ],
                        "Jobs": item[
                            "count"
                        ],
                        "Percentage": (
                            _format_percentage(
                                item[
                                    "percentage"
                                ]
                            )
                        ),
                    }
                    for item in languages
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.caption(
                "No language information "
                "available."
            )

    col3, col4 = st.columns(2)

    # ------------------------------------------------------
    # LOCATIONS
    # ------------------------------------------------------
    with col3:
        st.markdown(
            "#### Top Locations"
        )

        locations = (
            statistics.top_locations(
                limit=10,
                job_family=job_family,
                country=country,
            )
        )

        if locations:
            st.dataframe(
                [
                    {
                        "Location": item[
                            "name"
                        ],
                        "Jobs": item[
                            "count"
                        ],
                        "Percentage": (
                            _format_percentage(
                                item[
                                    "percentage"
                                ]
                            )
                        ),
                    }
                    for item in locations
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.caption(
                "No location information "
                "available."
            )

    # ------------------------------------------------------
    # SENIORITY
    # ------------------------------------------------------
    with col4:
        st.markdown(
            "#### Seniority"
        )

        seniority = (
            statistics.seniority_levels(
                job_family=job_family,
                country=country,
            )
        )

        if seniority:
            st.dataframe(
                [
                    {
                        "Level": item[
                            "name"
                        ],
                        "Jobs": item[
                            "count"
                        ],
                        "Percentage": (
                            _format_percentage(
                                item[
                                    "percentage"
                                ]
                            )
                        ),
                    }
                    for item in seniority
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.caption(
                "No seniority information "
                "available."
            )


# ==========================================================
# PERSONAL MARKET FIT
# ==========================================================
def _render_personal_market_fit(
    database: JobMarketDatabase,
    candidate_skills: List[str],
    job_family: Optional[str],
    country: Optional[str],
):
    comparator = CVMarketComparator(
        database
    )

    result = comparator.compare(
        candidate_skills=(
            candidate_skills
        ),
        job_family=job_family,
        country=country,
        top_n=30,
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Jobs analysed",
        result.total_jobs_analyzed,
    )

    col2.metric(
        "Market coverage",
        _format_percentage(
            result.market_coverage_percentage
        ),
    )

    st.caption(
        "Market coverage measures how much "
        "of the analysed market skill demand "
        "is represented in your profile. "
        "It is not an ATS score."
    )

    col3, col4 = st.columns(2)

    # ------------------------------------------------------
    # MATCHED SKILLS
    # ------------------------------------------------------
    with col3:
        st.markdown(
            "#### Skills You Match"
        )

        if result.matched_market_skills:
            st.dataframe(
                [
                    {
                        "Skill": item.skill,
                        "Demand": (
                            _format_percentage(
                                item.market_percentage
                            )
                        ),
                        "Jobs": (
                            item.market_count
                        ),
                    }
                    for item
                    in result.matched_market_skills
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info(
                "No matching market skills "
                "were found."
            )

    # ------------------------------------------------------
    # MISSING SKILLS
    # ------------------------------------------------------
    with col4:
        st.markdown(
            "#### Missing Market Skills"
        )

        if result.missing_market_skills:
            st.dataframe(
                [
                    {
                        "Skill": item.skill,
                        "Demand": (
                            _format_percentage(
                                item.market_percentage
                            )
                        ),
                        "Jobs": (
                            item.market_count
                        ),
                    }
                    for item
                    in result.missing_market_skills
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.success(
                "No missing skills detected "
                "in the analysed market."
            )


# ==========================================================
# SKILL GAP
# ==========================================================
def _render_skill_gap(
    database: JobMarketDatabase,
    candidate_skills: List[str],
    job_family: Optional[str],
    country: Optional[str],
):
    prioritizer = SkillGapPrioritizer(
        database
    )

    result = prioritizer.analyze(
        candidate_skills=(
            candidate_skills
        ),
        job_family=job_family,
        country=country,
        top_n=30,
    )

    st.metric(
        "Market coverage",
        _format_percentage(
            result.market_coverage_percentage
        ),
    )

    if not result.recommendations:
        st.success(
            "No learning priorities were "
            "identified."
        )
        return

    rows = []

    for index, item in enumerate(
        result.recommendations,
        start=1,
    ):
        rows.append(
            {
                "Priority Rank": index,
                "Skill": item.skill,
                "Market Demand": (
                    _format_percentage(
                        item.market_percentage
                    )
                ),
                "Jobs": item.market_count,
                "Priority": item.priority,
                "Score": item.priority_score,
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ==========================================================
# JOB RANKING
# ==========================================================
def _render_job_ranking(
    database: JobMarketDatabase,
    candidate_skills: List[str],
    job_family: Optional[str],
    country: Optional[str],
):
    ranker = JobRanker(
        database
    )

    minimum_score = st.slider(
        "Minimum job-fit score",
        min_value=0,
        max_value=100,
        value=40,
        step=5,
        key="market_minimum_job_score",
    )

    result = ranker.rank_jobs(
        candidate_skills=(
            candidate_skills
        ),
        job_family=job_family,
        country=country,
        minimum_score=minimum_score,
        limit=25,
    )

    st.caption(
        f"{result.total_jobs_considered} "
        "jobs were considered."
    )

    if not result.ranked_jobs:
        st.info(
            "No jobs meet the selected "
            "minimum score."
        )
        return

    for job in result.ranked_jobs:

        with st.expander(
            (
                f"#{job.rank} · "
                f"{job.job_title} · "
                f"{job.fit_score:.2f}%"
            )
        ):
            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "Fit score",
                _format_percentage(
                    job.fit_score
                ),
            )

            col2.metric(
                "Required skill match",
                _format_percentage(
                    job.required_skill_score
                ),
            )

            col3.metric(
                "Preferred skill match",
                _format_percentage(
                    job.preferred_skill_score
                ),
            )

            st.write(
                f"**Company:** "
                f"{job.company or 'Not specified'}"
            )

            st.write(
                f"**Location:** "
                f"{job.location or 'Not specified'}"
            )

            if job.matched_required_skills:
                st.write(
                    "**Matched required skills:** "
                    + ", ".join(
                        job.matched_required_skills
                    )
                )

            if job.missing_required_skills:
                st.write(
                    "**Missing required skills:** "
                    + ", ".join(
                        job.missing_required_skills
                    )
                )

            if job.matched_preferred_skills:
                st.write(
                    "**Matched preferred skills:** "
                    + ", ".join(
                        job.matched_preferred_skills
                    )
                )

            if job.missing_preferred_skills:
                st.write(
                    "**Missing preferred skills:** "
                    + ", ".join(
                        job.missing_preferred_skills
                    )
                )

            if job.source:
                st.write(
                    f"**Source:** "
                    f"{job.source}"
                )

            if job.source_url:

                if job.source_url.startswith(
                    (
                        "http://",
                        "https://",
                    )
                ):
                    st.link_button(
                        "Open Job",
                        job.source_url,
                    )

                else:
                    st.caption(
                        "This is demo/local market data "
                        "and does not have a public job URL."
                    )


# ==========================================================
# TREND ANALYSIS
# ==========================================================
def _render_trends(
    database: JobMarketDatabase,
    job_family: Optional[str],
    country: Optional[str],
):
    analyzer = MarketTrendAnalyzer(
        database
    )

    periods = analyzer.available_periods(
        job_family=job_family,
        country=country,
    )

    if len(periods) < 2:
        st.info(
            "At least two months of jobs "
            "with posted dates are required "
            "for trend analysis."
        )
        return

    col1, col2 = st.columns(2)

    earlier_period = col1.selectbox(
        "Earlier period",
        options=periods[:-1],
        index=0,
        key="market_trend_earlier",
    )

    possible_later = [
        period
        for period in periods
        if period > earlier_period
    ]

    if not possible_later:
        st.info(
            "Select an earlier period that "
            "has a later comparison month."
        )
        return

    later_period = col2.selectbox(
        "Later period",
        options=possible_later,
        index=len(
            possible_later
        ) - 1,
        key="market_trend_later",
    )

    # ------------------------------------------------------
    # RISING
    # ------------------------------------------------------
    st.markdown(
        "#### Rising Skills"
    )

    rising = analyzer.top_changing_skills(
        earlier_period=earlier_period,
        later_period=later_period,
        job_family=job_family,
        country=country,
        direction="rising",
        limit=15,
    )

    if rising:
        st.dataframe(
            [
                {
                    "Skill": item.skill,
                    earlier_period: (
                        _format_percentage(
                            item.earlier_percentage
                        )
                    ),
                    later_period: (
                        _format_percentage(
                            item.later_percentage
                        )
                    ),
                    "Change": (
                        f"{item.percentage_point_change:+.2f} pp"
                    ),
                    "Trend": item.trend,
                }
                for item in rising
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.caption(
            "No rising skills detected."
        )

    # ------------------------------------------------------
    # FALLING
    # ------------------------------------------------------
    st.markdown(
        "#### Falling Skills"
    )

    falling = analyzer.top_changing_skills(
        earlier_period=earlier_period,
        later_period=later_period,
        job_family=job_family,
        country=country,
        direction="falling",
        limit=15,
    )

    if falling:
        st.dataframe(
            [
                {
                    "Skill": item.skill,
                    earlier_period: (
                        _format_percentage(
                            item.earlier_percentage
                        )
                    ),
                    later_period: (
                        _format_percentage(
                            item.later_percentage
                        )
                    ),
                    "Change": (
                        f"{item.percentage_point_change:+.2f} pp"
                    ),
                    "Trend": item.trend,
                }
                for item in falling
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.caption(
            "No falling skills detected."
        )


# ==========================================================
# MAIN PAGE
# ==========================================================
def render_market_intelligence_page():
    """
    Main Streamlit page for Job Market Intelligence.
    """

    st.header(
        "📊 Job Market Intelligence"
    )

    st.write(
        "Analyse job-market demand, compare "
        "your CV with the market, identify "
        "learning priorities, rank suitable "
        "jobs and inspect market trends."
    )

    database = JobMarketDatabase()

    all_jobs = database.get_all_jobs()

    if not all_jobs:
        st.warning(
            "The Job Market database is empty. "
            "Import or collect jobs before "
            "running market analysis."
        )
        return

    # ------------------------------------------------------
    # AUTOMATIC CV SYNCHRONIZATION
    # ------------------------------------------------------
    cv_profile = (
        _sync_cv_skills_to_market()
    )

    if (
        "market_candidate_skills"
        not in st.session_state
    ):
        st.session_state[
            "market_candidate_skills"
        ] = ""

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------
    countries, job_families = (
        _get_filter_options(
            all_jobs
        )
    )

    st.subheader(
        "Market Filters"
    )

    col1, col2, col3, col4 = st.columns(4)

    selected_country = col1.selectbox(
        "Country",
        options=[
            "All Countries",
            *countries,
        ],
        index=0,
        key="market_country_filter",
    )

    selected_family = col2.selectbox(
        "Job Family",
        options=[
            "All Job Families",
            *job_families,
        ],
        index=0,
        key="market_family_filter",
    )

    country = (
        None
        if selected_country
        == "All Countries"
        else selected_country
    )

    market_family = (
        None
        if selected_family
        == "All Job Families"
        else selected_family
    )

    role_options = (
        subcategories_for_family(
            market_family
        )
        if market_family
        else []
    )

    current_role = (
        st.session_state.get(
            "market_role_filter",
            "All Roles",
        )
    )

    if (
        current_role != "All Roles"
        and current_role
        not in role_options
    ):
        st.session_state[
            "market_role_filter"
        ] = "All Roles"

    selected_role = col3.selectbox(
        "Job Role / Subcategory",
        options=[
            "All Roles",
            *role_options,
        ],
        index=0,
        disabled=(
            market_family is None
        ),
        help=(
            "Select a Job Family first. "
            "The role list will then show "
            "its subcategories."
        ),
        key="market_role_filter",
    )

    subcategory = (
        None
        if selected_role == "All Roles"
        else selected_role
    )

    role_filtered_jobs = (
        _filter_market_jobs(
            jobs=all_jobs,
            country=country,
            market_family=market_family,
            subcategory=subcategory,
        )
    )

    technology_options = (
        available_technologies(
            role_filtered_jobs
        )
    )

    current_technology = (
        st.session_state.get(
            "market_technology_filter",
            "All Technologies / Skills",
        )
    )

    if (
        current_technology
        != "All Technologies / Skills"
        and current_technology
        not in technology_options
    ):
        st.session_state[
            "market_technology_filter"
        ] = "All Technologies / Skills"

    selected_technology = col4.selectbox(
        "Technology / Skill",
        options=[
            "All Technologies / Skills",
            *technology_options,
        ],
        index=0,
        disabled=(
            len(technology_options) == 0
        ),
        help=(
            "Filter the selected market by an "
            "extracted technology or skill, for example "
            "Google Cloud Platform, AWS, BigQuery, Spark "
            "or Terraform."
        ),
        key="market_technology_filter",
    )

    technology = (
        None
        if selected_technology
        == "All Technologies / Skills"
        else selected_technology
    )

    filtered_jobs = (
        filter_jobs_by_technology(
            role_filtered_jobs,
            technology,
        )
    )

    analysis_database = (
        _FilteredJobMarketDatabase(
            source_database=database,
            jobs=filtered_jobs,
        )
    )

    statistics = (
        MarketStatisticsEngine(
            analysis_database
        )
    )

    if market_family:
        selected_market_text = (
            market_family
        )

        if subcategory:
            selected_market_text += (
                f" -> {subcategory}"
            )

        if technology:
            selected_market_text += (
                f" -> {technology}"
            )

        st.caption(
            "Selected market: "
            f"{selected_market_text}"
        )

    if not filtered_jobs:
        st.warning(
            "No collected jobs currently match "
            "this exact combination of country, "
            "job family, role and technology/skill. "
            "Try 'All Roles' or 'All Technologies / Skills' "
            "to broaden the market."
        )

    _render_taxonomy_summary(
        filtered_jobs
    )

    st.divider()

    (
        overview_tab,
        personal_tab,
        gap_tab,
        ranking_tab,
        trends_tab,
        refresh_tab,
    ) = st.tabs(
        [
            "Market Overview",
            "My Market Fit",
            "Skill Gaps",
            "Job Ranking",
            "Trends",
            "Refresh Data",
        ]
    )

    # ======================================================
    # MARKET OVERVIEW
    # ======================================================
    with overview_tab:

        _render_top_skills(
            statistics=statistics,
            job_family=None,
            country=None,
        )

        st.divider()

        _render_market_breakdown(
            statistics=statistics,
            job_family=None,
            country=None,
        )

    # ======================================================
    # PERSONAL MARKET FIT
    # ======================================================
    with personal_tab:

        st.subheader(
            "Candidate Skills"
        )

        final_cv_text = (
            st.session_state.get(
                "final_cv_text",
                "",
            )
            or ""
        ).strip()

        if final_cv_text:

            if (
                cv_profile
                and cv_profile.skills
            ):
                st.success(
                    f"Automatically extracted "
                    f"{cv_profile.skill_count} skills "
                    f"from your most recently "
                    f"analysed CV."
                )

                with st.expander(
                    "Show automatically detected CV skills"
                ):
                    st.write(
                        ", ".join(
                            cv_profile.skills
                        )
                    )

            else:
                st.warning(
                    "An analysed CV is available, "
                    "but no known market skills "
                    "were detected."
                )

            if st.button(
                "Refresh skills from analysed CV",
                key="refresh_market_cv_skills",
            ):
                _sync_cv_skills_to_market(
                    force=True
                )

                st.rerun()

        else:
            st.info(
                "No analysed CV is available in "
                "this session. Analyse a CV in "
                "'Analyse Job' first, or enter "
                "your skills manually below."
            )

        st.text_area(
            "Skills used for market comparison",
            height=150,
            help=(
                "Skills are automatically populated "
                "from your analysed CV. You can also "
                "edit, add or remove skills manually. "
                "Separate them with commas or new lines."
            ),
            key="market_candidate_skills",
        )

        candidate_skills = (
            _parse_candidate_skills(
                st.session_state.get(
                    "market_candidate_skills",
                    "",
                )
            )
        )

        st.caption(
            f"{len(candidate_skills)} skills "
            "currently used for market analysis."
        )

        if candidate_skills:

            _render_personal_market_fit(
                database=analysis_database,
                candidate_skills=(
                    candidate_skills
                ),
                job_family=job_family,
                country=country,
            )

        else:
            st.info(
                "No candidate skills are "
                "currently available."
            )

    # ======================================================
    # SKILL GAPS
    # ======================================================
    with gap_tab:

        candidate_skills = (
            _parse_candidate_skills(
                st.session_state.get(
                    "market_candidate_skills",
                    "",
                )
            )
        )

        if candidate_skills:

            _render_skill_gap(
                database=analysis_database,
                candidate_skills=(
                    candidate_skills
                ),
                job_family=job_family,
                country=country,
            )

        else:
            st.info(
                "Analyse a CV or enter skills "
                "in the 'My Market Fit' tab first."
            )

    # ======================================================
    # JOB RANKING
    # ======================================================
    with ranking_tab:

        candidate_skills = (
            _parse_candidate_skills(
                st.session_state.get(
                    "market_candidate_skills",
                    "",
                )
            )
        )

        if candidate_skills:

            _render_job_ranking(
                database=analysis_database,
                candidate_skills=(
                    candidate_skills
                ),
                job_family=job_family,
                country=country,
            )

        else:
            st.info(
                "Analyse a CV or enter skills "
                "in the 'My Market Fit' tab first."
            )

    # ======================================================
    # TRENDS
    # ======================================================
    with trends_tab:

        render_snapshot_trends()

    # ======================================================
    # MARKET DATA REFRESH
    # ======================================================
    with refresh_tab:

        render_market_refresh()
