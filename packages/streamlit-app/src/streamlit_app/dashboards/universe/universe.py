# universe.py

import streamlit as st

from streamlit_app.dashboards.universe.equity_data_provider import load_equities
from streamlit_app.dashboards.universe.grid import display_grid, get_cached_grid_options

df = load_equities()

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
