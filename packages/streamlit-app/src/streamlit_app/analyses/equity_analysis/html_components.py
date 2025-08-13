# html_components.py

from __future__ import annotations

from streamlit.delta_generator import DeltaGenerator

from streamlit_app.analyses.equity_analysis.formatters import fmt_pct


def render_colored_pct_metric(
    container: DeltaGenerator,
    label: str,
    value: float | None,
) -> None:
    """
    Render a percentage metric with green/red colouring.

    Matches st.metric styling but applies colour based on sign.

    Args:
        container: Streamlit column or container to render into.
        label: The metric label text.
        value: Decimal ratio value (e.g. 0.15 for 15%), or None.
    """
    if value is None:
        formatted = "N/A"
        color = "#31333F"
    else:
        formatted = fmt_pct(value)
        color = "#16a34a" if value >= 0 else "#dc2626"
    label_style = (
        "font-size:0.82rem;"
        "color:rgb(120,120,120);"
        "font-weight:400;"
        'font-family:"Source Sans Pro",sans-serif;'
        "line-height:1.6;"
    )
    value_style = (
        "font-size:2.25rem;"
        "font-weight:400;"
        'font-family:"Source Sans Pro",sans-serif;'
        "line-height:1.2;"
    )
    container.markdown(
        f"<div>"
        f'<label style="{label_style}">{label}</label>'
        f'<div style="{value_style}color:{color};">'
        f"{formatted}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
