# integrity_report.py

import streamlit as st

from streamlit_app.reports.data_provider import (
    load_completeness_distribution,
    load_coverage_report,
    load_cross_field_consistency,
    load_financial_ratio_consistency,
    load_market_cap_distribution,
    load_sector_field_coverage,
    load_value_plausibility,
)
from streamlit_app.reports.renderers import (
    render_completeness_card,
    render_consistency_card,
    render_coverage_table,
    render_header,
    render_market_cap_card,
    render_sector_heatmap_card,
    render_summary,
)

with st.spinner("Running integrity analysis..."):
    report = load_coverage_report()

render_header(report)
st.space("medium")
render_summary(report)
st.divider()

left, right = st.columns(2)
with left:
    render_coverage_table(
        "Identity Coverage",
        report.identity_coverage,
    )
    render_consistency_card(
        "Pricing Anomalies",
        load_cross_field_consistency(),
    )
    render_consistency_card(
        "Financial Ratio Anomalies",
        load_financial_ratio_consistency(),
    )
    render_consistency_card(
        "Value Plausibility",
        load_value_plausibility(),
    )
with right:
    render_coverage_table(
        "Financial Coverage",
        report.financial_coverage,
    )

st.write("")
left, right = st.columns(2)
with left:
    render_market_cap_card(
        "Market Cap Distribution",
        load_market_cap_distribution(),
    )
with right:
    render_completeness_card(
        "Financial Data Completeness",
        load_completeness_distribution(),
    )

st.write("")
render_sector_heatmap_card(
    "Sector Coverage",
    load_sector_field_coverage(),
)
