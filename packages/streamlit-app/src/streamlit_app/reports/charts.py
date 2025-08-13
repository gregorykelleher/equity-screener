# charts.py

import plotly.graph_objects as go

from streamlit_app.reports.models import SectorFieldCoverage


def build_market_cap_chart(
    values: tuple[float, ...],
) -> go.Figure:
    """
    Build a Plotly bar chart of market cap tier distribution.

    Args:
        values: Raw positive market cap values.

    Returns:
        go.Figure: Bar chart with 6 market cap tier buckets.
    """
    labels, counts = _count_per_tier(values)
    fig = go.Figure(
        data=go.Bar(
            x=labels,
            y=counts,
            marker_color="#FF4B4B",
        ),
    )
    fig.update_layout(
        margin={"l": 40, "r": 20, "t": 30, "b": 40},
        template="plotly_white",
        xaxis_title="Market Cap Tier",
        yaxis_title="No. of Equities",
    )
    return fig


def build_completeness_chart(
    values: tuple[int, ...],
) -> go.Figure:
    """
    Build a Plotly bar chart of per-equity completeness scores.

    Args:
        values: Per-equity field counts (0-31).

    Returns:
        go.Figure: Bar chart with one bar per score (0-31).
    """
    labels, counts = _count_per_score(values)
    total = len(values)
    pcts = _score_percentages(counts, total)
    fig = go.Figure(
        data=go.Bar(
            x=labels,
            y=counts,
            marker_color="#FF4B4B",
            customdata=pcts,
            hovertemplate=(
                "%{y:,} equities (%{customdata:.1f}%) with %{x} fields<extra></extra>"
            ),
        ),
    )
    fig.update_layout(
        bargap=0.15,
        margin={"l": 40, "r": 20, "t": 30, "b": 40},
        template="plotly_white",
        xaxis_title="Fields Populated (out of 31)",
        xaxis={"dtick": 5},
        yaxis_title="No. of Equities",
    )
    return fig


def build_sector_heatmap(
    coverage: SectorFieldCoverage,
) -> go.Figure:
    """
    Build a Plotly heatmap of sector vs field coverage.

    Args:
        coverage: Sector field coverage data.

    Returns:
        go.Figure: Heatmap with red-to-white-to-green colour scale.
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=coverage.percentages,
            x=coverage.fields,
            y=coverage.sectors,
            colorscale=_heatmap_colour_scale(),
            zmin=0,
            zmax=100,
            hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>",
        ),
    )
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 30, "b": 40},
        template="plotly_white",
        height=_heatmap_height(len(coverage.sectors)),
        xaxis={"tickangle": -45},
    )
    return fig


def _count_per_tier(
    values: tuple[float, ...],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """
    Bucket market cap values into standard financial tiers.

    Args:
        values: Raw positive market cap values.

    Returns:
        tuple[tuple[str, ...], tuple[int, ...]]: Parallel tuples
            of tier labels and counts.
    """
    thresholds = (
        ("Nano (<$50M)", 0, 50e6),
        ("Micro ($50M-$300M)", 50e6, 300e6),
        ("Small ($300M-$2B)", 300e6, 2e9),
        ("Mid ($2B-$10B)", 2e9, 10e9),
        ("Large ($10B-$200B)", 10e9, 200e9),
        ("Mega (>$200B)", 200e9, float("inf")),
    )
    labels = tuple(t[0] for t in thresholds)
    counts = tuple(sum(1 for v in values if lo <= v < hi) for _, lo, hi in thresholds)
    return labels, counts


def _count_per_score(
    values: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """
    Count equities at each completeness score from 0 to 31.

    Args:
        values: Per-equity field counts (0-31).

    Returns:
        tuple[tuple[int, ...], tuple[int, ...]]: Parallel tuples
            of score labels and equity counts.
    """
    scores = range(32)
    counts = tuple(values.count(s) for s in scores)
    return tuple(scores), counts


def _score_percentages(
    counts: tuple[int, ...],
    total: int,
) -> tuple[float, ...]:
    """
    Convert raw counts to percentages of a total.

    Args:
        counts: Raw counts per score bin.
        total: Total number of equities.

    Returns:
        tuple[float, ...]: Percentage for each bin.
    """
    if not total:
        return tuple(0.0 for _ in counts)
    return tuple(c / total * 100 for c in counts)


def _heatmap_colour_scale() -> list[list[float | str]]:
    """
    Return the red-to-white-to-green colour scale for the heatmap.

    Returns:
        list[list[float | str]]: Plotly-compatible colour scale.
    """
    return [[0, "#FF4B4B"], [0.5, "#FAFAFA"], [1.0, "#4BB543"]]


def _heatmap_height(num_sectors: int) -> int:
    """
    Compute dynamic chart height based on number of sectors.

    Args:
        num_sectors: Number of sector rows in the heatmap.

    Returns:
        int: Pixel height for the chart.
    """
    return max(400, num_sectors * 35 + 150)
