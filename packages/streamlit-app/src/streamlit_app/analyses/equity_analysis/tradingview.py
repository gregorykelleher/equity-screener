# tradingview.py

import json

import httpx
import streamlit as st
import streamlit.components.v1 as components

_TV_GLOBAL_SCAN_URL = "https://scanner.tradingview.com/global/scan"
_TV_LOGO_BASE = "https://s3-symbol-logo.tradingview.com"
_TV_CHART_JS = (
    "https://s3.tradingview.com/external-embedding"
    "/embed-widget-advanced-chart.js"
)
_TV_PROFILE_JS = (
    "https://s3.tradingview.com/external-embedding"
    "/embed-widget-symbol-profile.js"
)

_CHART_HEIGHT = 660
_PROFILE_HEIGHT = 360
_CHART_BG = "#ffffff"
_GRID_COLOR = "rgba(46, 46, 46, 0.06)"

_MIC_TO_TV_MARKET: dict[str, str] = {
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


def _mics_to_tv_markets(mics: str | None) -> list[str]:
    """
    Map comma-separated MICs to a deduplicated list of TV markets.

    Uses dict.fromkeys() for O(n) deduplication with preserved order.

    Args:
        mics: Comma-separated MIC codes (e.g. "XNYS,XNAS").

    Returns:
        Deduplicated list of TradingView market identifiers.
    """
    if not mics:
        return []
    markets = (
        _MIC_TO_TV_MARKET.get(mic.strip())
        for mic in mics.split(",")
    )
    return list(dict.fromkeys(m for m in markets if m))


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
        Request body dict ready for httpx.post().
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
        The resolved TradingView symbol string.
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
        body = _build_scan_request(field, query, operation, markets)
        try:
            resp = httpx.post(
                _TV_GLOBAL_SCAN_URL, json=body, timeout=10,
            )
            resp.raise_for_status()
            rows = resp.json().get("data", [])
            if rows:
                return rows[0].get("s", symbol)
        except Exception:
            continue
    return symbol


@st.cache_data(ttl=3600, show_spinner="Fetching logo...")
def fetch_logo(tv_sym: str) -> str | None:
    """
    Fetch the logoid for a symbol from TradingView.

    Args:
        tv_sym: The TradingView EXCHANGE:SYMBOL string.

    Returns:
        The logoid string, or None if unavailable.
    """
    body = {
        "symbols": {"tickers": [tv_sym]},
        "columns": ["logoid"],
    }
    try:
        resp = httpx.post(
            _TV_GLOBAL_SCAN_URL, json=body, timeout=10,
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
        Full URL to the logo SVG image.
    """
    return f"{_TV_LOGO_BASE}/{logoid}--big.svg"


def _chart_config(tv_symbol: str) -> str:
    """
    Build the JSON config string for the TradingView chart widget.

    Args:
        tv_symbol: The resolved TradingView symbol.

    Returns:
        JSON-encoded config string.
    """
    return json.dumps({
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
        "backgroundColor": _CHART_BG,
        "gridColor": _GRID_COLOR,
        "watchlist": [],
        "compareSymbols": [],
        "studies": ["STD;SMA"],
        "width": "100%",
        "height": _CHART_HEIGHT,
    })


def render_chart(tv_symbol: str) -> None:
    """
    Render the TradingView advanced chart widget.

    Args:
        tv_symbol: The resolved TradingView symbol.
    """
    config = _chart_config(tv_symbol)
    html = (
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget"></div>'
        f'<script type="text/javascript" src="{_TV_CHART_JS}" async>'
        f"{config}</script></div>"
    )
    components.html(html, height=_CHART_HEIGHT + 40)


def render_profile(tv_symbol: str) -> None:
    """
    Render the TradingView company profile widget.

    Args:
        tv_symbol: The resolved TradingView symbol.
    """
    config = json.dumps({
        "symbol": tv_symbol,
        "width": "100%",
        "height": _PROFILE_HEIGHT,
        "isTransparent": True,
        "colorTheme": "light",
        "locale": "en",
    })
    html = (
        '<div class="tradingview-widget-container">'
        '<div class="tradingview-widget-container__widget"></div>'
        f'<script type="text/javascript" src="{_TV_PROFILE_JS}" async>'
        f"{config}</script></div>"
    )
    components.html(html, height=_PROFILE_HEIGHT)
