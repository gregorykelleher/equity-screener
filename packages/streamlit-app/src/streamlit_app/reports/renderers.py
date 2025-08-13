# renderers.py

from datetime import date

import pandas as pd
import streamlit as st

from streamlit_app.reports.charts import (
    build_completeness_chart,
    build_market_cap_chart,
    build_sector_heatmap,
)
from streamlit_app.reports.models import (
    CompletenessDistribution,
    ConsistencyFinding,
    CoverageReport,
    FieldCoverage,
    MarketCapDistribution,
    SectorFieldCoverage,
)


def render_header(report: CoverageReport) -> None:
    """
    Render the page header with snapshot date.

    Args:
        report: The coverage report data.
    """
    st.header("Integrity Report")
    if report.snapshot_date:
        parsed = date.fromisoformat(report.snapshot_date)
        formatted = parsed.strftime("%d/%m/%Y")
        st.caption(f"_Latest Snapshot Date: {formatted}_")


def render_summary(report: CoverageReport) -> None:
    """
    Render summary metrics: total equities, identity and financial coverage.

    Args:
        report: The coverage report data.
    """
    identity_pct = _overall_coverage(report.identity_coverage)
    financials_pct = _overall_coverage(report.financial_coverage)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Identity Coverage", f"{identity_pct:.1f}%")
    col2.metric("Financial Coverage", f"{financials_pct:.1f}%")
    col3.metric("Total Equities", f"{report.total_equities:,}")
    col4.metric("Total Snapshots", f"{report.total_snapshots:,}")
    col5.metric("Distinct Sectors", f"{report.distinct_sectors:,}")
    col6.metric("Distinct Industries", f"{report.distinct_industries:,}")


def render_coverage_table(
    title: str,
    coverage: tuple[FieldCoverage, ...],
    *,
    height: int | None = None,
) -> None:
    """
    Render a coverage table with progress bars inside a bordered card.

    Args:
        title: Subheading displayed at the top of the card.
        coverage: Field coverage tuples to display.
        height: Optional fixed pixel height for the card container.
    """
    df = _build_coverage_dataframe(coverage)
    df = df.sort_values("Coverage", ascending=False).reset_index(drop=True)
    container_kwargs = {"border": True, "gap": "medium"}
    if height is not None:
        container_kwargs["height"] = height
    dataframe_height = "stretch" if height is not None else "content"
    with st.container(**container_kwargs):
        st.subheader(title)
        st.dataframe(
            df,
            column_config={
                "Coverage": st.column_config.ProgressColumn(
                    "Coverage",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
                ),
            },
            hide_index=True,
            use_container_width=True,
            height=dataframe_height,
        )


def render_market_cap_card(
    title: str,
    distribution: MarketCapDistribution,
    *,
    height: int | None = None,
) -> None:
    """
    Render a market cap distribution card with metrics and histogram.

    Args:
        title: Subheading displayed at the top of the card.
        distribution: Market cap distribution statistics.
        height: Optional fixed pixel height for the card container.
    """
    container_kwargs = {"border": True, "gap": "medium"}
    if height is not None:
        container_kwargs["height"] = height
    with st.container(**container_kwargs):
        st.subheader(title)
        _render_distribution_metrics(distribution)
        chart = build_market_cap_chart(distribution.values)
        st.plotly_chart(
            chart,
            width="stretch",
            height="stretch",
            config={"displayModeBar": False},
        )


def render_consistency_card(
    title: str,
    findings: tuple[ConsistencyFinding, ...],
    *,
    height: int | None = None,
) -> None:
    """
    Render cross-field consistency findings inside a bordered card.

    Args:
        title: Subheading displayed at the top of the card.
        findings: Consistency findings to display.
        height: Optional fixed pixel height for the card container.
    """
    df = _build_consistency_dataframe(findings)
    df = df.sort_values("Affected", ascending=False).reset_index(drop=True)
    container_kwargs = {"border": True, "gap": "medium"}
    if height is not None:
        container_kwargs["height"] = height
    with st.container(**container_kwargs):
        st.subheader(title)
        st.dataframe(
            df,
            column_config={
                "Affected": st.column_config.ProgressColumn(
                    "Affected",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
                ),
            },
            hide_index=True,
            use_container_width=True,
            height="content",
        )


def render_completeness_card(
    title: str,
    distribution: CompletenessDistribution,
    *,
    height: int | None = None,
) -> None:
    """
    Render a completeness distribution card with metrics and histogram.

    Args:
        title: Subheading displayed at the top of the card.
        distribution: Completeness distribution statistics.
        height: Optional fixed pixel height for the card container.
    """
    container_kwargs: dict[str, object] = {
        "border": True,
        "gap": "medium",
    }
    if height is not None:
        container_kwargs["height"] = height
    with st.container(**container_kwargs):
        st.subheader(title)
        _render_completeness_metrics(distribution)
        chart = build_completeness_chart(distribution.values)
        st.plotly_chart(
            chart,
            width="stretch",
            height="stretch",
            config={"displayModeBar": False},
        )


def render_sector_heatmap_card(
    title: str,
    coverage: SectorFieldCoverage,
) -> None:
    """
    Render a sector coverage heatmap inside a bordered card.

    Args:
        title: Subheading displayed at the top of the card.
        coverage: Sector field coverage data.
    """
    with st.container(border=True, gap="medium"):
        st.subheader(title)
        chart = build_sector_heatmap(coverage)
        st.plotly_chart(
            chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )


def _render_distribution_metrics(
    distribution: MarketCapDistribution,
) -> None:
    """
    Render a row of summary metrics for market cap distribution.

    Args:
        distribution: Market cap distribution statistics.
    """
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Equities", f"{distribution.count:,}")
    col2.metric(
        "Median Market Cap",
        _format_large_number(distribution.median),
    )
    col3.metric(
        "Mean Market Cap",
        _format_large_number(distribution.mean),
    )


def _format_large_number(value: float) -> str:
    """
    Format a number with T/B/M abbreviations.

    Args:
        value: The numeric value to format.

    Returns:
        str: Abbreviated string (e.g. "$1.2T", "$340.5B").
    """
    suffixes = ((1e12, "T"), (1e9, "B"), (1e6, "M"))
    for threshold, suffix in suffixes:
        if abs(value) >= threshold:
            return f"${value / threshold:.1f}{suffix}"
    return f"${value:,.0f}"


def _build_coverage_dataframe(
    coverage: tuple[FieldCoverage, ...],
) -> pd.DataFrame:
    """
    Convert field coverage tuples to a DataFrame for display.

    Combines populated and total counts into a single ratio column.

    Args:
        coverage: Field coverage tuples.

    Returns:
        pd.DataFrame: DataFrame with Field and Coverage columns.
    """
    return pd.DataFrame(
        [
            {
                "Field": fc.label,
                "Coverage": (fc.count / fc.total * 100) if fc.total else 0,
            }
            for fc in coverage
        ]
    )


def _overall_coverage(
    coverage: tuple[FieldCoverage, ...],
) -> float:
    """
    Compute the overall coverage percentage across all fields.

    Args:
        coverage: Field coverage tuples.

    Returns:
        float: Weighted average coverage as a percentage.
    """
    total_count = sum(fc.count for fc in coverage)
    total_possible = sum(fc.total for fc in coverage)
    if not total_possible:
        return 0.0
    return total_count / total_possible * 100


def _build_consistency_dataframe(
    findings: tuple[ConsistencyFinding, ...],
) -> pd.DataFrame:
    """
    Convert consistency findings to a DataFrame for display.

    Args:
        findings: Cross-field consistency findings.

    Returns:
        pd.DataFrame: DataFrame with Check and Affected columns.
    """
    return pd.DataFrame(
        [
            {
                "Check": f.description,
                "Affected": (f.count / f.total * 100) if f.total else 0,
            }
            for f in findings
        ]
    )


def _render_completeness_metrics(
    distribution: CompletenessDistribution,
) -> None:
    """
    Render summary metrics for completeness distribution.

    Args:
        distribution: Completeness distribution statistics.
    """
    col1, col2 = st.columns(2)
    col1.metric("Total Equities", f"{distribution.count:,}")
    col2.metric(
        "Median Fields Populated",
        f"{distribution.median:.0f} / 31",
    )
