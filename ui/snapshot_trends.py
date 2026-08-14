from datetime import datetime

import streamlit as st

from market_intelligence.market_history import (
    MarketRefreshHistory,
)
from market_intelligence.snapshot_trends import (
    SnapshotTrendAnalyzer,
)


def _format_time(
    value: str,
) -> str:

    try:

        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

        return parsed.strftime(
            "%Y-%m-%d %H:%M UTC"
        )

    except Exception:
        return value


def _snapshot_label(
    snapshot: dict,
) -> str:

    return (
        f"Snapshot #{snapshot['id']} · "
        f"{_format_time(snapshot['completed_at'])} · "
        f"{snapshot['snapshot_jobs']} jobs"
    )


def render_snapshot_trends():

    st.subheader(
        "📈 Historical Market Trends"
    )

    st.write(
        "Compare persistent market snapshots to see "
        "how skill demand and the size of the market "
        "change over time."
    )

    history = MarketRefreshHistory()

    analyzer = SnapshotTrendAnalyzer(
        history
    )

    snapshots = analyzer.snapshots()

    # ======================================================
    # NOT ENOUGH HISTORY
    # ======================================================

    if len(snapshots) < 2:

        st.info(
            "At least two market snapshots are required "
            "for historical trend comparison."
        )

        if snapshots:

            latest = snapshots[-1]

            st.write(
                f"Current history contains Snapshot "
                f"#{latest['id']} with "
                f"{latest['snapshot_jobs']} jobs from "
                f"{latest['companies_count']} companies."
            )

        st.caption(
            "Run 'Refresh Market Data' again later to "
            "create the next snapshot."
        )

        return

    # ======================================================
    # SELECT SNAPSHOTS
    # ======================================================

    snapshot_map = {
        snapshot["id"]: snapshot
        for snapshot in snapshots
    }

    snapshot_ids = [
        snapshot["id"]
        for snapshot in snapshots
    ]

    col1, col2 = st.columns(2)

    earlier_id = col1.selectbox(
        "Earlier snapshot",
        options=snapshot_ids[:-1],
        index=0,
        format_func=lambda value: (
            _snapshot_label(
                snapshot_map[
                    value
                ]
            )
        ),
        key="snapshot_trend_earlier",
    )

    possible_later = [
        snapshot_id
        for snapshot_id
        in snapshot_ids
        if snapshot_id > earlier_id
    ]

    later_id = col2.selectbox(
        "Later snapshot",
        options=possible_later,
        index=(
            len(
                possible_later
            )
            - 1
        ),
        format_func=lambda value: (
            _snapshot_label(
                snapshot_map[
                    value
                ]
            )
        ),
        key="snapshot_trend_later",
    )

    # ======================================================
    # MARKET GROWTH
    # ======================================================

    market_change = (
        analyzer.market_change(
            earlier_run_id=(
                earlier_id
            ),
            later_run_id=(
                later_id
            ),
        )
    )

    st.markdown(
        "### Market Change"
    )

    metric1, metric2, metric3 = (
        st.columns(3)
    )

    metric1.metric(
        "Market jobs",
        market_change.later_jobs,
        delta=(
            market_change.job_change
        ),
    )

    metric2.metric(
        "Companies",
        market_change.later_companies,
        delta=(
            market_change.company_change
        ),
    )

    if (
        market_change
        .job_change_percentage
        is not None
    ):

        growth_display = (
            f"{market_change.job_change_percentage:+.2f}%"
        )

    else:

        growth_display = "N/A"

    metric3.metric(
        "Market growth",
        growth_display,
    )

    # ======================================================
    # RISING SKILLS
    # ======================================================

    st.markdown(
        "### 🚀 Rising Skills"
    )

    rising = analyzer.changing_skills(
        earlier_run_id=earlier_id,
        later_run_id=later_id,
        direction="rising",
        limit=20,
    )

    if rising:

        st.dataframe(
            [
                {
                    "Skill": item.skill,
                    "Earlier Demand": (
                        f"{item.earlier_percentage:.2f}%"
                    ),
                    "Later Demand": (
                        f"{item.later_percentage:.2f}%"
                    ),
                    "Change": (
                        f"{item.percentage_point_change:+.2f} pp"
                    ),
                    "Jobs Now": (
                        item.later_job_count
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
            "No skills increased between "
            "these snapshots."
        )

    # ======================================================
    # FALLING SKILLS
    # ======================================================

    st.markdown(
        "### 📉 Falling Skills"
    )

    falling = analyzer.changing_skills(
        earlier_run_id=earlier_id,
        later_run_id=later_id,
        direction="falling",
        limit=20,
    )

    if falling:

        st.dataframe(
            [
                {
                    "Skill": item.skill,
                    "Earlier Demand": (
                        f"{item.earlier_percentage:.2f}%"
                    ),
                    "Later Demand": (
                        f"{item.later_percentage:.2f}%"
                    ),
                    "Change": (
                        f"{item.percentage_point_change:+.2f} pp"
                    ),
                    "Jobs Now": (
                        item.later_job_count
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
            "No skills decreased between "
            "these snapshots."
        )

    # ======================================================
    # ONE SKILL THROUGH TIME
    # ======================================================

    st.markdown(
        "### Skill Demand Through Time"
    )

    skills = (
        history.available_skills()
    )

    if not skills:
        return

    selected_skill = st.selectbox(
        "Select skill",
        options=skills,
        key="snapshot_skill_history",
    )

    points = analyzer.skill_trend(
        selected_skill
    )

    if not points:
        return

    chart_data = {
        point.completed_at: (
            point.demand_percentage
        )
        for point in points
    }

    st.line_chart(
        chart_data,
        y_label="Demand %",
    )

    st.dataframe(
        [
            {
                "Snapshot": (
                    point.refresh_run_id
                ),
                "Date": (
                    _format_time(
                        point.completed_at
                    )
                ),
                "Jobs": (
                    point.snapshot_jobs
                ),
                "Companies": (
                    point.companies_count
                ),
                "Jobs requiring skill": (
                    point.job_count
                ),
                "Demand": (
                    f"{point.demand_percentage:.2f}%"
                ),
            }
            for point in points
        ],
        use_container_width=True,
        hide_index=True,
    )
