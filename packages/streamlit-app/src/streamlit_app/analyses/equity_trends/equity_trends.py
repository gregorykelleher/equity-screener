# equity_trends.py

from typing import Any

import streamlit as st

from streamlit_app.analyses.equity_trends.data_provider import load_history
from streamlit_app.analyses.equity_trends.renderers import (
    render_header,
    render_trends,
)

# Session state guard
data: dict[str, Any] | None = st.session_state.get("selected_equity_data")
name: str | None = st.session_state.get("selected_equity_name")

if not data or not name:
    st.info("Select an equity from the Universe table to view equity trends.")
    st.stop()

figi = data.get("Share Class FIGI", "")
if not figi:
    st.warning("No FIGI available for this equity.")
    st.stop()

df = load_history(figi)

render_header(name, df)

if df.empty:
    st.info("No snapshot data available.")
    st.stop()

render_trends(df)
