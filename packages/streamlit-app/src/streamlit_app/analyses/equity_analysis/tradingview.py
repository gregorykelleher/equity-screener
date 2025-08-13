# tradingview.py

import json

import httpx
import streamlit as st
import streamlit.components.v1 as components


@st.cache_data(ttl=3600, show_spinner="Resolving symbol...")
def resolve_tv_symbol(
    symbol: str,
    equity_name: str,
    mics: str | None = None,
) -> str:
    """
    Resolve an equity into TradingView EXCHANGE:SYMBOL format.

    Queries the TradingView global scanner API with priority-ordered
    searches: exact symbol match first, then fuzzy fallbacks.

    Args:
        symbol: The equity ticker symbol.
        equity_name: The full equity name for fuzzy matching.
        mics: Optional comma-separated MIC codes.

    Returns:
        str: The resolved TradingView symbol string.
    """
    markets = _mics_to_tv_markets(mics)
    searches = (
        ("name", symbol, "equal"),
        ("description", equity_name, "match"),
        ("name", symbol, "match"),
    )
    for field, query, operation in searches:
        if not query:
            continue
        result = _try_scan(field, query, operation, markets)
        if result is not None:
            return result
    return symbol


@st.cache_data(ttl=3600, show_spinner="Fetching logo...")
def fetch_logo(tv_sym: str) -> str | None:
    """
    Fetch the logoid for a symbol from TradingView.

    Args:
        tv_sym: The TradingView EXCHANGE:SYMBOL string.

    Returns:
        str | None: The logoid string, or None if unavailable.
    """
    body = {
        "symbols": {"tickers": [tv_sym]},
        "columns": ["logoid"],
    }
    try:
        resp = httpx.post(
            "https://scanner.tradingview.com/global/scan",
            json=body,
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json().get("data", [])
        if rows:
            return rows[0].get("d", [None])[0]
    except Exception:
        pass
    return None


def logo_url(logoid: str) -> str:
    """
    Build the full SVG logo URL from a TradingView logoid.

    Args:
        logoid: The TradingView logo identifier.

    Returns:
        str: Full URL to the logo SVG image.
    """
    return f"https://s3-symbol-logo.tradingview.com/{logoid}--big.svg"


def render_chart(tv_symbol: str) -> None:
    """
    Render the TradingView advanced chart widget.

    Args:
        tv_symbol: The resolved TradingView symbol.
    """
    config = _chart_config(tv_symbol)
    chart_js = (
        "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js"
    )
    html = (
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget"></div>'
        f'<script type="text/javascript" src="{chart_js}" async>'
        f"{config}</script></div>"
    )
    components.html(html, height=700)


def render_profile(tv_symbol: str) -> None:
    """
    Render the TradingView company profile widget.

    Args:
        tv_symbol: The resolved TradingView symbol.
    """
    profile_js = (
        "https://s3.tradingview.com/external-embedding/embed-widget-symbol-profile.js"
    )
    config = json.dumps(
        {
            "symbol": tv_symbol,
            "width": "100%",
            "height": 360,
            "isTransparent": True,
            "colorTheme": "light",
            "locale": "en",
        }
    )
    html = (
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget"></div>'
        f'<script type="text/javascript" src="{profile_js}" async>'
        f"{config}</script></div>"
    )
    components.html(html, height=360)


def _try_scan(
    field: str,
    query: str,
    operation: str,
    markets: list[str],
) -> str | None:
    """
    Attempt a single TradingView scanner search and return the top result.

    Args:
        field: The field to filter on (e.g. "name", "description").
        query: The search query value.
        operation: The filter operation (e.g. "equal", "match").
        markets: List of TradingView market identifiers.

    Returns:
        str | None: The matched symbol, or None on failure.
    """
    body = _build_scan_request(field, query, operation, markets)
    try:
        resp = httpx.post(
            "https://scanner.tradingview.com/global/scan",
            json=body,
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json().get("data", [])
        if rows:
            return rows[0].get("s")
    except Exception:
        pass
    return None


def _build_scan_request(
    field: str,
    query: str,
    operation: str,
    markets: list[str],
) -> dict:
    """
    Build a TradingView scanner API request body.

    Args:
        field: The field to filter on (e.g. "name", "description").
        query: The search query value.
        operation: The filter operation (e.g. "equal", "match").
        markets: List of TradingView market identifiers.

    Returns:
        dict: Request body dict ready for httpx.post().
    """
    return {
        "markets": markets,
        "symbols": {
            "query": {"types": ["stock"]},
            "tickers": [],
        },
        "options": {"lang": "en"},
        "filter": [
            {"left": field, "operation": operation, "right": query},
        ],
        "columns": ["name", "description", "volume"],
        "sort": {"sortBy": "volume", "sortOrder": "desc"},
        "range": [0, 1],
    }


def _mics_to_tv_markets(mics: str | None) -> list[str]:
    """
    Map comma-separated MICs to a deduplicated list of TV market identifiers.

    Uses dict.fromkeys() for O(n) deduplication with preserved order.

    Args:
        mics: Comma-separated MIC codes (e.g. "XNYS,XNAS").

    Returns:
        list[str]: Deduplicated list of TradingView market identifiers.
    """
    if not mics:
        return []
    mic_map = _mic_to_tv_market_map()
    markets = (mic_map.get(mic.strip()) for mic in mics.split(","))
    return list(dict.fromkeys(m for m in markets if m))


def _mic_to_tv_market_map() -> dict[str, str]:
    """
    Return the MIC-to-TradingView market mapping table.

    Returns:
        dict[str, str]: Mapping from MIC codes to TradingView market names.
    """
    return {
        "XNYS": "america",
        "XNAS": "america",
        "XASE": "america",
        "ARCX": "america",
        "BATS": "america",
        "IEXG": "america",
        "XLON": "uk",
        "XETR": "germany",
        "XFRA": "germany",
        "XPAR": "france",
        "XAMS": "netherlands",
        "XBRU": "belgium",
        "XLIS": "portugal",
        "XMIL": "italy",
        "XMAD": "spain",
        "XSWX": "switzerland",
        "XSTO": "sweden",
        "XCSE": "denmark",
        "XOSL": "norway",
        "XHEL": "finland",
        "XWBO": "austria",
        "XTKS": "japan",
        "XHKG": "hongkong",
        "XSHG": "china",
        "XSHE": "china",
        "XKRX": "korea",
        "XTAI": "taiwan",
        "XASX": "australia",
        "XNZE": "newzealand",
        "XSES": "singapore",
        "XBOM": "india",
        "XNSE": "india",
        "XTSE": "canada",
        "BVMF": "brazil",
        "XMEX": "mexico",
        "XJSE": "rsa",
    }


def _chart_config(tv_symbol: str) -> str:
    """
    Build the JSON config string for the TradingView chart widget.

    Args:
        tv_symbol: The resolved TradingView symbol.

    Returns:
        str: JSON-encoded config string.
    """
    return json.dumps(
        {
            "symbol": tv_symbol,
            "theme": "light",
            "style": "1",
            "interval": "W",
            "timezone": "Etc/UTC",
            "locale": "en",
            "allow_symbol_change": False,
            "hide_side_toolbar": True,
            "hide_top_toolbar": False,
            "hide_legend": False,
            "hide_volume": False,
            "calendar": False,
            "details": False,
            "hotlist": False,
            "save_image": False,
            "withdateranges": False,
            "range": "12M",
            "backgroundColor": "#ffffff",
            "gridColor": "rgba(46, 46, 46, 0.06)",
            "watchlist": [],
            "compareSymbols": [],
            "studies": ["STD;SMA"],
            "width": "100%",
            "height": 660,
        }
    )
