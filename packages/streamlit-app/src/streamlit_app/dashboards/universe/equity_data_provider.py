# data_provider.py

from decimal import Decimal

import pandas as pd
import streamlit as st
from equity_aggregator import retrieve_canonical_equities

from streamlit_app.dashboards.universe.columns import DISPLAY_COLUMNS, FIELD_MAPPING


@st.cache_resource(ttl=3600, show_spinner=False)
def load_equities() -> tuple[pd.DataFrame, str | None]:
    """
    Fetch all canonical equities and return them as a cached DataFrame.

    Returns:
        tuple[pd.DataFrame, str | None]: DataFrame with columns matching
            DISPLAY_COLUMNS and latest snapshot date as YYYY-MM-DD or None.
    """
    equities = retrieve_canonical_equities()
    data = [_equity_to_row(eq) for eq in equities]
    snapshot_date = equities[0].snapshot_date if equities else None
    return pd.DataFrame(data, columns=list(DISPLAY_COLUMNS)), snapshot_date


def _equity_to_row(equity: object) -> dict[str, object]:
    """
    Map a single CanonicalEquity to a flat dict keyed by display column names.

    Driven by FIELD_MAPPING as its single source of truth.

    Args:
        equity: A CanonicalEquity instance from equity-aggregator.

    Returns:
        dict[str, object]: Flat dict suitable for a single DataFrame row.
    """
    return {
        name: _format_field(name, _resolve_accessor(equity, path))
        for name, path in FIELD_MAPPING
    }


def _format_field(name: str, value: object) -> object:
    """
    Coerce a resolved field value into its display-ready form.

    Joins MICs lists into comma-separated strings and coerces Decimals to float.

    Args:
        name: The display column name.
        value: The raw resolved value from the equity object.

    Returns:
        object: The display-ready value.
    """
    if name == "MICs" and isinstance(value, list):
        return ", ".join(value) if value else None
    return _coerce_value(value)


def _resolve_accessor(obj: object, dot_path: str) -> object:
    """
    Resolve a dot-separated attribute path on an object via getattr chain.

    Args:
        obj: Root object to traverse.
        dot_path: Dot-delimited attribute path (e.g. `"identity.name"`).

    Returns:
        object: The resolved attribute value, or None if any segment is missing.
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
        object: A float if the input was Decimal, otherwise the original value.
    """
    if isinstance(value, Decimal):
        return float(value)
    return value
