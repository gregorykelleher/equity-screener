# grid.py

from typing import Any

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from streamlit_app.dashboards.universe.columns import COLUMN_GROUPS
from streamlit_app.dashboards.universe.grid_configurators import configure_columns


def get_cached_grid_options(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return grid options, building and caching them in session state on
    first call.

    Note:
        The options are built once per session since the column structure
        is static.

    Args:
        df: Source DataFrame whose columns seed the GridOptionsBuilder.

    Returns:
        dict[str, Any]: Complete grid options dict ready for AgGrid rendering.
    """
    if "grid_options" not in st.session_state:
        st.session_state["grid_options"] = _build_grid_options(df)
    return st.session_state["grid_options"]


@st.fragment
def display_grid(
    df: pd.DataFrame,
    grid_options: dict[str, Any],
    search_query: str = "",
) -> None:
    """
    Render the AgGrid inside a fragment so selection changes only rerun this
    fragment, not the full page.

    On row selection, stores the equity in session state and navigates to the
    equity analysis page.

    Args:
        df: Source DataFrame to display.
        grid_options: Pre-built grid options from get_cached_grid_options.
        search_query: Text to apply as the AgGrid quick filter.
    """
    grid_options["quickFilterText"] = search_query

    response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        key="universe_grid",
        fit_columns_on_grid_load=False,
        theme="streamlit",
        height=600,
        allow_unsafe_jscode=True,
    )

    if response.selected_rows is not None and len(response.selected_rows) > 0:
        row = response.selected_rows.iloc[0]
        st.session_state["selected_equity_name"] = row["Name"]
        st.session_state["selected_equity_data"] = row.to_dict()
        st.switch_page("analyses/equity_analysis/equity_analysis.py")


def _build_grid_options(df: pd.DataFrame) -> dict[str, Any]:
    """
    Create fully-configured AgGrid options for the given DataFrame.

    Runs the column configuration, sets tooltip config, and applies
    grouped column definitions.

    Args:
        df: Source DataFrame whose columns seed the GridOptionsBuilder.

    Returns:
        dict[str, Any]: Complete grid options dict ready for AgGrid rendering.
    """
    gb = GridOptionsBuilder.from_dataframe(df)
    configure_columns(gb)

    grid_options = gb.build()
    grid_options["tooltipShowDelay"] = 300
    grid_options["tooltipInteraction"] = True
    grid_options["columnDefs"] = _build_grouped_column_defs(grid_options["columnDefs"])

    return grid_options


def _build_grouped_column_defs(flat_col_defs: list[dict]) -> list[dict]:
    """
    Transform flat columnDefs into the grouped hierarchy defined by COLUMN_GROUPS.

    Columns not belonging to any group are appended ungrouped at the end.

    Args:
        flat_col_defs: Flat list of AgGrid column definition dicts.

    Returns:
        list[dict]: Grouped column definition list with headerName/children
            structure.
    """
    col_def_map = {cd["field"]: cd for cd in flat_col_defs if "field" in cd}

    grouped: list[dict] = []
    for group in COLUMN_GROUPS:
        children = [col_def_map[f] for f in group.columns if f in col_def_map]
        if children:
            grouped.append({"headerName": group.header, "children": children})

    grouped_fields = {f for group in COLUMN_GROUPS for f in group.columns}
    for cd in flat_col_defs:
        field = cd.get("field", "")
        if field and field not in grouped_fields and not field.startswith("::"):
            grouped.append(cd)

    return grouped
