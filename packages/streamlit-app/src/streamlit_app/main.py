# streamlit_app/main.py

import streamlit as st


def main() -> None:
    """
    The main function that sets up and runs the Streamlit app.
    """

    # Set the page configuration
    st.set_page_config(
        page_title="Screener App",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    pages = st.navigation(
        {
            "Dashboards": [
                st.Page(
                    "dashboards/universe/universe.py",
                    title="Universe",
                    icon="🌍",
                    default=True,
                ),
                st.Page(
                    "reports/integrity_report.py",
                    title="Integrity Report",
                    url_path="integrity-report",
                ),
            ],
            "Analyses": [
                st.Page(
                    "analyses/equity_analysis/equity_analysis.py",
                    title="Equity Analysis",
                    icon="📝",
                ),
                st.Page(
                    "analyses/equity_trends/equity_trends.py",
                    title="Equity Trends",
                    icon="📈",
                ),
            ],
        }
    )

    # Hide the "Integrity Report" page from the sidebar navigation
    st.sidebar.markdown(
        "<style>"
        "[data-testid='stSidebarNav']"
        ' a[href*="integrity-report"]{display:none;}'
        "</style>",
        unsafe_allow_html=True,
    )

    pages.run()


if __name__ == "__main__":
    main()
