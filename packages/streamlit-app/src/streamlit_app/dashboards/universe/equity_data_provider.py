# data_provider.py

from decimal import Decimal

import pandas as pd
import streamlit as st

from streamlit_app.dashboards.universe.columns import DISPLAY_COLUMNS, FIELD_MAPPING


@st.cache_data(ttl=900)
def load_equities() -> pd.DataFrame:
    """
    Fetch all canonical equities and return them as a cached DataFrame.

    Lazy-imports equity_aggregator so the module stays importable without
    the dependency installed.

    Returns:
        DataFrame with columns matching DISPLAY_COLUMNS, cached for 15 minutes.
    """
    from equity_aggregator import retrieve_canonical_equities

    equities = retrieve_canonical_equities()
    data = [_equity_to_row(eq) for eq in equities]
    return pd.DataFrame(data, columns=list(DISPLAY_COLUMNS))


def _equity_to_row(equity: object) -> dict[str, object]:
    """
    Map a single CanonicalEquity to a flat dict keyed by display column names.

    Driven by FIELD_MAPPING as its single source of truth.  Coerces Decimal
    values to float and joins MICs lists into comma-separated strings.

    Args:
        equity: A CanonicalEquity instance from equity-aggregator.

    Returns:
        Flat dict suitable for a single DataFrame row.
    """
    row: dict[str, object] = {}
    for display_name, dot_path in FIELD_MAPPING:
        value = _resolve_accessor(equity, dot_path)
        if display_name == "MICs" and isinstance(value, list):
            value = ", ".join(value) if value else None
        else:
            value = _coerce_value(value)
        row[display_name] = value
    return row


def _resolve_accessor(obj: object, dot_path: str) -> object:
    """
    Resolve a dot-separated attribute path on an object via getattr chain.

    Args:
        obj: Root object to traverse.
        dot_path: Dot-delimited attribute path (e.g. `"identity.name"`).

    Returns:
        The resolved attribute value, or None if any segment is missing.
    """
    for attr in dot_path.split("."):
        obj = getattr(obj, attr, None)
        if obj is None:
            return None
    return obj


def _coerce_value(value: object) -> object:
    """
    Coerce a Decimal to float for pandas numeric dtype efficiency.

    Args:
        value: The value to potentially coerce.

    Returns:
        A float if the input was Decimal, otherwise the original value.
    """
    if isinstance(value, Decimal):
        return float(value)
    return value
