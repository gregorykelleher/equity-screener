# universe.py

import streamlit as st

from streamlit_app.dashboards.universe.equity_data_provider import load_equities
from streamlit_app.dashboards.universe.grid import display_grid, get_cached_grid_options

with st.spinner("Loading equities..."):
    df, snapshot_date = load_equities()

# Search bar
_, search_col = st.columns([3, 1])
with search_col:
    search_query = st.text_input(
        "Search",
        placeholder="Search...",
        label_visibility="collapsed",
    )

# AgGrid display
grid_options = get_cached_grid_options(df)
display_grid(df, grid_options, search_query)

# Data freshness indicator
if snapshot_date:
    day, month, year = (
        snapshot_date[8:10],
        snapshot_date[5:7],
        snapshot_date[:4],
    )
    with st.container(horizontal_alignment="right"):
        st.page_link(
            "reports/integrity_report.py",
            label=f"_Integrity Report &middot; Last updated: {day}/{month}/{year}_",
        )
