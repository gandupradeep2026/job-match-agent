import streamlit as st

from market_intelligence.system_health import (
    MarketSystemHealthService,
)


def _status_icon(
    status: str,
) -> str:

    if status == "HEALTHY":
        return "✅"

    if status == "WARNING":
        return "⚠️"

    return "❌"


def render_market_system_health():

    service = (
        MarketSystemHealthService()
    )

    report = service.evaluate()

    st.subheader(
        "🩺 Market Intelligence Health"
    )

    icon = _status_icon(
        report.overall_status
    )

    if (
        report.overall_status
        == "HEALTHY"
    ):

        st.success(
            f"{icon} System status: "
            f"{report.overall_status}"
        )

    elif (
        report.overall_status
        == "WARNING"
    ):

        st.warning(
            f"{icon} System status: "
            f"{report.overall_status}"
        )

    else:

        st.error(
            f"{icon} System status: "
            f"{report.overall_status}"
        )

    # ======================================================
    # METRICS
    # ======================================================

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Production Jobs",
        report.production_jobs,
    )

    col2.metric(
        "Companies",
        report.companies,
    )

    col3.metric(
        "Enabled Sources",
        report.enabled_sources,
    )

    col4.metric(
        "Snapshots",
        report.snapshots,
    )

    # ======================================================
    # CHECKS
    # ======================================================

    rows = []

    for check in report.checks:

        rows.append(
            {
                "Status": (
                    _status_icon(
                        check.status
                    )
                ),
                "Check": (
                    check.name
                ),
                "Value": (
                    check.value
                ),
                "Result": (
                    check.status
                ),
                "Details": (
                    check.message
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "A WARNING does not necessarily mean the "
        "system is broken. For example, a provider "
        "may publish one vacancy without a usable "
        "job description while all other sources "
        "continue successfully."
    )
