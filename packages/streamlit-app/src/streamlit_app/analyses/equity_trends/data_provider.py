# data_provider.py

from decimal import Decimal

import pandas as pd
import streamlit as st
from equity_aggregator import retrieve_canonical_equity_history


@st.cache_data(ttl=900)
def load_history(figi: str) -> pd.DataFrame:
    """
    Fetch canonical equity history snapshots and return them as a DataFrame.

    Args:
        figi: Share class FIGI identifier for the equity.

    Returns:
        pd.DataFrame: Historical snapshot data with parsed dates, or empty
            on error.
    """
    try:
        snapshots = retrieve_canonical_equity_history(figi)
    except LookupError:
        return pd.DataFrame()

    rows = [_snapshot_to_row(s) for s in snapshots]
    df = pd.DataFrame(rows)
    if "snapshot_date" in df.columns:
        df["snapshot_date"] = pd.to_datetime(df["snapshot_date"]).dt.date
    return df


def _snapshot_to_row(snapshot: object) -> dict[str, object]:
    """
    Map a single equity snapshot to a flat dict keyed by column names.

    Args:
        snapshot: A CanonicalEquity instance from equity-aggregator.

    Returns:
        dict[str, object]: Flat dict suitable for a single DataFrame row.
    """
    fields = (
        ("snapshot_date", "snapshot_date"),
        ("last_price", "financials.last_price"),
        ("trailing_pe", "financials.trailing_pe"),
        ("price_to_book", "financials.price_to_book"),
        ("trailing_eps", "financials.trailing_eps"),
        ("revenue_per_share", "financials.revenue_per_share"),
        ("profit_margin", "financials.profit_margin"),
        ("gross_margin", "financials.gross_margin"),
        ("operating_margin", "financials.operating_margin"),
        ("operating_cash_flow", "financials.operating_cash_flow"),
        ("free_cash_flow", "financials.free_cash_flow"),
        ("total_debt", "financials.total_debt"),
        ("shares_outstanding", "financials.shares_outstanding"),
        ("held_insiders", "financials.held_insiders"),
        ("held_institutions", "financials.held_institutions"),
        ("revenue", "financials.revenue"),
        ("ebitda", "financials.ebitda"),
    )
    return {col: _coerce_decimal(_resolve(snapshot, path)) for col, path in fields}


def _coerce_decimal(value: object) -> object:
    """
    Coerce a Decimal to float for pandas numeric dtype efficiency.

    Args:
        value: The value to potentially coerce.

    Returns:
        object: A float if the input was Decimal, otherwise the original value.
    """
    return float(value) if isinstance(value, Decimal) else value


def _resolve(obj: object, dot_path: str) -> object:
    """
    Resolve a dot-separated attribute path on an object via getattr chain.

    Args:
        obj: Root object to traverse.
        dot_path: Dot-delimited attribute path (e.g. "financials.last_price").

    Returns:
        object: The resolved attribute value, or None if any segment is missing.
    """
    for attr in dot_path.split("."):
        obj = getattr(obj, attr, None)
        if obj is None:
            return None
    return obj
