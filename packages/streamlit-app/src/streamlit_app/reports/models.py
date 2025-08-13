# models.py

from typing import NamedTuple


class FieldCoverage(NamedTuple):
    """
    Coverage statistics for a single field.
    """

    label: str
    count: int
    total: int


class CoverageReport(NamedTuple):
    """
    Aggregated field coverage for identity and financial fields.
    """

    total_equities: int
    snapshot_date: str | None
    total_snapshots: int
    distinct_sectors: int
    distinct_industries: int
    identity_coverage: tuple[FieldCoverage, ...]
    financial_coverage: tuple[FieldCoverage, ...]


class ConsistencyFinding(NamedTuple):
    """
    A single cross-field logic consistency observation.
    """

    description: str
    count: int
    total: int


class MarketCapDistribution(NamedTuple):
    """
    Summary statistics for market capitalisation distribution.
    """

    count: int
    median: float
    mean: float
    values: tuple[float, ...]


class CompletenessDistribution(NamedTuple):
    """
    Summary statistics for per-equity field completeness.
    """

    count: int
    median: float
    mean: float
    values: tuple[int, ...]


class SectorFieldCoverage(NamedTuple):
    """
    Coverage percentages for each sector/field pair.
    """

    sectors: tuple[str, ...]
    fields: tuple[str, ...]
    percentages: tuple[tuple[float, ...], ...]
