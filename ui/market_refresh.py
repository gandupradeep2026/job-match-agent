from datetime import datetime
from typing import Optional

import streamlit as st

from ui.market_system_health import render_market_system_health

from market_intelligence.database import (
    JobMarketDatabase,
)
from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.market_refresh import (
    MarketRefreshResult,
    MarketRefreshService,
)


# ==========================================================
# HELPERS
# ==========================================================

def _format_datetime(
    value: str,
) -> str:

    if not value:
        return "Unknown"

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

        return parsed.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

    except ValueError:
        return value


def _store_refresh_result(
    result: MarketRefreshResult,
) -> None:

    st.session_state[
        "market_refresh_result"
    ] = result


def _get_refresh_result(
) -> Optional[MarketRefreshResult]:

    return st.session_state.get(
        "market_refresh_result"
    )


# ==========================================================
# CURRENT DATABASE
# ==========================================================

def _render_database_status(
    database: JobMarketDatabase,
) -> None:

    st.subheader(
        "Current Market Database"
    )

    st.metric(
        "Jobs currently stored",
        database.count_jobs(),
    )

    st.caption(
        "Only jobs accepted by the configured market "
        "filters are stored. Existing job URLs are "
        "protected against duplicate insertion."
    )


# ==========================================================
# REFRESH SUMMARY
# ==========================================================

def _render_refresh_summary(
    result: MarketRefreshResult,
) -> None:

    st.subheader(
        "Latest Refresh Result"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Sources checked",
        result.sources_attempted,
    )

    col2.metric(
        "Jobs fetched",
        result.fetched,
    )

    col3.metric(
        "New jobs",
        result.inserted,
    )

    col4.metric(
        "Database jobs",
        result.jobs_after,
    )

    col5, col6, col7, col8 = (
        st.columns(4)
    )

    col5.metric(
        "Filtered out",
        result.filtered_out,
    )

    col6.metric(
        "Duplicates",
        result.duplicates,
    )

    col7.metric(
        "Failed jobs",
        result.failed_jobs,
    )

    col8.metric(
        "Source errors",
        result.source_errors,
    )

    st.caption(
        "Started: "
        + _format_datetime(
            result.started_at
        )
        + " · Completed: "
        + _format_datetime(
            result.completed_at
        )
    )


# ==========================================================
# SOURCE HEALTH
# ==========================================================

def _render_source_results(
    result: MarketRefreshResult,
) -> None:

    st.subheader(
        "Source Health"
    )

    rows = []

    for source in (
        result.source_results
    ):

        if source.source_error:
            status = "❌ Error"

        elif source.failed:
            status = "⚠️ Partial"

        else:
            status = "✅ Healthy"

        rows.append(
            {
                "Company": source.company,
                "Provider": source.provider,
                "Status": status,
                "Fetched": source.fetched,
                "New": source.inserted,
                "Duplicates": (
                    source.duplicates
                ),
                "Filtered": (
                    source.filtered_out
                ),
                "Failed": source.failed,
                "Error": (
                    source.source_error
                    or ""
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ==========================================================
# PERSISTENT REFRESH HISTORY
# ==========================================================

def _render_history(
    history: MarketRefreshHistory,
) -> None:

    st.subheader(
        "📚 Refresh History"
    )

    runs = history.recent_refreshes(
        limit=15
    )

    if not runs:
        st.info(
            "No persistent refresh history exists yet. "
            "Run a market refresh to create the first snapshot."
        )

        return

    rows = []

    for run in runs:

        rows.append(
            {
                "Run": run["id"],
                "Completed": (
                    _format_datetime(
                        run[
                            "completed_at"
                        ]
                    )
                ),
                "Market Jobs": (
                    run[
                        "snapshot_jobs"
                    ]
                ),
                "Companies": (
                    run[
                        "companies_count"
                    ]
                ),
                "Fetched": (
                    run["fetched"]
                ),
                "New": (
                    run["inserted"]
                ),
                "Duplicates": (
                    run["duplicates"]
                ),
                "Failed": (
                    run["failed_jobs"]
                ),
                "Source Errors": (
                    run["source_errors"]
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    # ======================================================
    # HISTORICAL SKILL DEMAND
    # ======================================================

    skills = (
        history.available_skills()
    )

    if not skills:
        return

    st.markdown(
        "#### Historical Skill Demand"
    )

    selected_skill = st.selectbox(
        "Skill",
        options=skills,
        key="market_history_skill",
    )

    skill_rows = (
        history.skill_history(
            selected_skill
        )
    )

    if not skill_rows:
        return

    st.dataframe(
        [
            {
                "Refresh": (
                    row[
                        "refresh_run_id"
                    ]
                ),
                "Completed": (
                    _format_datetime(
                        row[
                            "completed_at"
                        ]
                    )
                ),
                "Jobs": (
                    row[
                        "snapshot_jobs"
                    ]
                ),
                "Companies": (
                    row[
                        "companies_count"
                    ]
                ),
                "Jobs requiring skill": (
                    row[
                        "job_count"
                    ]
                ),
                "Demand": (
                    f"{row['demand_percentage']:.2f}%"
                ),
            }
            for row in skill_rows
        ],
        use_container_width=True,
        hide_index=True,
    )


# ==========================================================
# MAIN COMPONENT
# ==========================================================

def render_market_refresh(
) -> None:

    render_market_system_health()

    st.divider()

    st.subheader(
        "🔄 Refresh Market Data"
    )

    st.write(
        "Check all configured Greenhouse and Lever "
        "career sources, add newly published jobs and "
        "save a historical snapshot of the market."
    )

    database = (
        JobMarketDatabase()
    )

    history = (
        MarketRefreshHistory()
    )

    _render_database_status(
        database
    )

    st.info(
        "Each successful refresh now creates a persistent "
        "market snapshot in `database/market_history.db`."
    )

    refresh_button = st.button(
        "🔄 Refresh Market Data",
        type="primary",
        key="refresh_market_data_button",
    )

    if refresh_button:

        try:

            service = (
                MarketRefreshService(
                    database=database
                )
            )

            with st.spinner(
                "Refreshing job-market data from "
                "all configured sources..."
            ):

                result = (
                    service.refresh()
                )

                collection_filter = (
                    service.registry
                    .load_collection_filter()
                )

                refresh_run_id = (
                    history.record_refresh(
                        result=result,
                        market_database=(
                            database
                        ),
                        collection_filter=(
                            collection_filter
                        ),
                    )
                )

            _store_refresh_result(
                result
            )

            st.session_state[
                "market_refresh_run_id"
            ] = refresh_run_id

            if result.inserted:

                st.success(
                    f"Refresh completed. "
                    f"{result.inserted} new job(s) added "
                    f"and snapshot #{refresh_run_id} saved."
                )

            else:

                st.success(
                    "Refresh completed. No new matching "
                    f"jobs were found. Snapshot "
                    f"#{refresh_run_id} was still saved."
                )

        except Exception as error:

            st.error(
                "Market data refresh failed."
            )

            st.code(
                f"{type(error).__name__}: "
                f"{error}"
            )

    result = _get_refresh_result()

    if result is not None:

        st.divider()

        _render_refresh_summary(
            result
        )

        st.divider()

        _render_source_results(
            result
        )

    st.divider()

    _render_history(
        history
    )