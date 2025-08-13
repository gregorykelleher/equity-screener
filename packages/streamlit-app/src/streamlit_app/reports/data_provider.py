# data_provider.py

import statistics

import streamlit as st
from equity_aggregator import CanonicalEquity, retrieve_canonical_equities

from streamlit_app.reports.checks import (
    run_cross_field_checks,
    run_plausibility_checks,
    run_ratio_checks,
)
from streamlit_app.reports.fields import (
    financial_fields,
    has_field,
    heatmap_fields,
    identity_fields,
)
from streamlit_app.reports.models import (
    CompletenessDistribution,
    CoverageReport,
    FieldCoverage,
    MarketCapDistribution,
    SectorFieldCoverage,
)


@st.cache_resource(ttl=3600, show_spinner=False)
def load_coverage_report() -> CoverageReport:
    """
    Fetch all canonical equities and compute field coverage.

    Returns:
        CoverageReport: Coverage statistics for identity and
            financial fields.
    """
    equities = _load_equities()
    snapshot_date = equities[0].snapshot_date if equities else None
    return CoverageReport(
        total_equities=len(equities),
        snapshot_date=snapshot_date,
        total_snapshots=_count_total_snapshots(equities),
        distinct_sectors=_count_distinct(equities, "sector"),
        distinct_industries=_count_distinct(equities, "industry"),
        identity_coverage=_compute_coverage(
            equities,
            "identity",
            identity_fields(),
        ),
        financial_coverage=_compute_coverage(
            equities,
            "financials",
            financial_fields(),
        ),
    )


@st.cache_data(ttl=3600)
def load_market_cap_distribution() -> MarketCapDistribution:
    """
    Compute market capitalisation distribution statistics.

    Returns:
        MarketCapDistribution: Count, median, mean, and raw values
            for equities with reported market cap.
    """
    values = _extract_market_caps(_load_equities())
    return MarketCapDistribution(
        count=len(values),
        median=statistics.median(values) if values else 0.0,
        mean=statistics.mean(values) if values else 0.0,
        values=values,
    )


@st.cache_data(ttl=3600)
def load_cross_field_consistency() -> tuple:
    """
    Detect cross-field logic inconsistencies across all equities.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each consistency
            check performed.
    """
    return run_cross_field_checks(_load_equities())


@st.cache_data(ttl=3600)
def load_completeness_distribution() -> CompletenessDistribution:
    """
    Compute per-equity field completeness distribution.

    Returns:
        CompletenessDistribution: Count, median, mean, and raw scores
            (0-31) for each equity.
    """
    scores = _compute_completeness_scores(_load_equities())
    return CompletenessDistribution(
        count=len(scores),
        median=statistics.median(scores) if scores else 0,
        mean=statistics.mean(scores) if scores else 0,
        values=scores,
    )


@st.cache_data(ttl=3600)
def load_sector_field_coverage() -> SectorFieldCoverage:
    """
    Compute per-field coverage percentages grouped by sector.

    Returns:
        SectorFieldCoverage: Sectors, field labels, and a 2D
            percentages matrix.
    """
    grouped = _group_by_sector(_load_equities())
    fields = heatmap_fields()
    sector_rows = {s: _sector_coverage_row(grouped[s], fields) for s in grouped}
    ranked = sorted(sector_rows.items(), key=lambda p: _mean(p[1]))
    col_order = _rank_columns_by_coverage(
        tuple(row for _, row in ranked),
    )
    return SectorFieldCoverage(
        sectors=tuple(s for s, _ in ranked),
        fields=tuple(fields[i][1] for i in col_order),
        percentages=tuple(tuple(row[i] for i in col_order) for _, row in ranked),
    )


@st.cache_data(ttl=3600)
def load_financial_ratio_consistency() -> tuple:
    """
    Detect logically inconsistent financial ratio relationships.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each ratio
            consistency check performed.
    """
    return run_ratio_checks(_load_equities())


@st.cache_data(ttl=3600)
def load_value_plausibility() -> tuple:
    """
    Detect individual field values outside plausible ranges.

    Returns:
        tuple[ConsistencyFinding, ...]: Findings for each value
            plausibility check performed.
    """
    return run_plausibility_checks(_load_equities())


@st.cache_resource(ttl=3600)
def _load_equities() -> list[CanonicalEquity]:
    """
    Shared cached loader for canonical equities.

    Returns:
        list[CanonicalEquity]: All canonical equities.
    """
    return retrieve_canonical_equities()


def _extract_market_caps(
    equities: list[CanonicalEquity],
) -> tuple[float, ...]:
    """
    Filter equities to those with a positive market cap.

    Args:
        equities: List of CanonicalEquity instances.

    Returns:
        tuple[float, ...]: Positive market cap values.
    """
    return tuple(
        float(eq.financials.market_cap)
        for eq in equities
        if eq.financials.market_cap is not None and eq.financials.market_cap > 0
    )


def _count_total_snapshots(
    equities: list[CanonicalEquity],
) -> int:
    """
    Count distinct non-None snapshot dates across all equities.

    Args:
        equities: List of CanonicalEquity instances.

    Returns:
        int: Number of unique snapshot dates.
    """
    return len(
        {eq.snapshot_date for eq in equities if eq.snapshot_date is not None},
    )


def _count_distinct(
    equities: list[CanonicalEquity],
    attr: str,
) -> int:
    """
    Count distinct non-None values for a financials attribute.

    Args:
        equities: List of CanonicalEquity instances.
        attr: Attribute name on the financials group.

    Returns:
        int: Number of unique non-None values.
    """
    return len(
        {
            getattr(eq.financials, attr)
            for eq in equities
            if getattr(eq.financials, attr, None) is not None
        }
    )


def _compute_coverage(
    equities: list[object],
    group: str,
    fields: tuple[tuple[str, str], ...],
) -> tuple[FieldCoverage, ...]:
    """
    Count non-None values for each field across all equities.

    Args:
        equities: List of CanonicalEquity instances.
        group: Attribute group name ("identity" or "financials").
        fields: Tuples of (attribute_name, display_label).

    Returns:
        tuple[FieldCoverage, ...]: Coverage for each field.
    """
    total = len(equities)
    return tuple(
        FieldCoverage(
            label=label,
            count=_count_populated(equities, group, attr),
            total=total,
        )
        for attr, label in fields
    )


def _count_populated(
    equities: list[object],
    group: str,
    attr: str,
) -> int:
    """
    Count equities where the given nested attribute is not None.

    Args:
        equities: List of CanonicalEquity instances.
        group: Attribute group name (e.g. "identity").
        attr: Attribute name within the group.

    Returns:
        int: Number of equities with a non-None value.
    """
    return sum(
        1
        for eq in equities
        if getattr(getattr(eq, group, None), attr, None) is not None
    )


def _mean(values: tuple[float, ...]) -> float:
    """
    Compute the arithmetic mean of a tuple of floats.

    Args:
        values: Numeric values.

    Returns:
        float: The mean, or 0.0 if the tuple is empty.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def _rank_columns_by_coverage(
    rows: tuple[tuple[float, ...], ...],
) -> tuple[int, ...]:
    """
    Return column indices sorted by mean coverage descending.

    Args:
        rows: 2D percentages matrix (sectors x fields).

    Returns:
        tuple[int, ...]: Column indices ordered highest mean first.
    """
    if not rows:
        return ()
    num_cols = len(rows[0])
    col_means = tuple(sum(row[c] for row in rows) / len(rows) for c in range(num_cols))
    return tuple(
        i
        for i, _ in sorted(
            enumerate(col_means),
            key=lambda pair: pair[1],
            reverse=True,
        )
    )


def _compute_completeness_scores(
    equities: list[CanonicalEquity],
) -> tuple[int, ...]:
    """
    Count populated financial fields for each equity.

    Args:
        equities: All canonical equities.

    Returns:
        tuple[int, ...]: Per-equity scores (0-31).
    """
    fields = financial_fields()
    return tuple(_count_equity_fields(eq, fields) for eq in equities)


def _count_equity_fields(
    equity: CanonicalEquity,
    fields: tuple[tuple[str, str], ...],
) -> int:
    """
    Count how many financial fields are populated for one equity.

    Args:
        equity: A single canonical equity.
        fields: Financial field specifications.

    Returns:
        int: Number of non-None fields.
    """
    return sum(1 for attr, _ in fields if has_field(equity, attr))


def _group_by_sector(
    equities: list[CanonicalEquity],
) -> dict[str, list[CanonicalEquity]]:
    """
    Group equities by sector, excluding those without one.

    Args:
        equities: All canonical equities.

    Returns:
        dict[str, list[CanonicalEquity]]: Equities keyed by sector.
    """
    grouped: dict[str, list[CanonicalEquity]] = {}
    for eq in equities:
        if eq.financials.sector is not None:
            grouped.setdefault(eq.financials.sector, []).append(eq)
    return grouped


def _sector_coverage_row(
    equities: list[CanonicalEquity],
    fields: tuple[tuple[str, str], ...],
) -> tuple[float, ...]:
    """
    Compute per-field coverage percentages for a sector group.

    Args:
        equities: Equities within a single sector.
        fields: Financial field specifications.

    Returns:
        tuple[float, ...]: Coverage percentage for each field.
    """
    total = len(equities)
    return tuple(_field_coverage_pct(equities, attr, total) for attr, _ in fields)


def _field_coverage_pct(
    equities: list[CanonicalEquity],
    attr: str,
    total: int,
) -> float:
    """
    Compute coverage percentage for a single field.

    Args:
        equities: Equities to check.
        attr: Financial attribute name.
        total: Total number of equities in the group.

    Returns:
        float: Percentage of equities with the field populated.
    """
    if not total:
        return 0.0
    return sum(1 for eq in equities if has_field(eq, attr)) / total * 100
