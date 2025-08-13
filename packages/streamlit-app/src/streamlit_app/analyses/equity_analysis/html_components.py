# html_components.py

from __future__ import annotations

from streamlit.delta_generator import DeltaGenerator

from streamlit_app.analyses.equity_analysis.formatters import fmt_pct

_POS_COLOR = "#16a34a"
_NEG_COLOR = "#dc2626"
_TEXT_COLOR = "#31333F"

_METRIC_LABEL_STYLE = (
    "font-size:0.82rem;"
    "color:rgb(120,120,120);"
    "font-weight:400;"
    'font-family:"Source Sans Pro",sans-serif;'
    "line-height:1.6;"
)

_METRIC_VALUE_STYLE = (
    "font-size:2.25rem;"
    "font-weight:400;"
    'font-family:"Source Sans Pro",sans-serif;'
    "line-height:1.2;"
)


def render_colored_pct_metric(
    container: DeltaGenerator,
    label: str,
    value: float | None,
) -> None:
    """
    Render a percentage metric with green/red coloring.

    Matches st.metric styling but applies color based on sign.

    Args:
        container: Streamlit column or container to render into.
        label: The metric label text.
        value: Decimal ratio value (e.g. 0.15 for 15%).
    """
    if value is None:
        formatted = "N/A"
        color = _TEXT_COLOR
    else:
        formatted = fmt_pct(value)
        color = _POS_COLOR if value >= 0 else _NEG_COLOR
    container.markdown(
        f"<div>"
        f'<label style="{_METRIC_LABEL_STYLE}">{label}</label>'
        f'<div style="{_METRIC_VALUE_STYLE}color:{color};">'
        f"{formatted}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
