# formatters.py

from st_aggrid import JsCode

CURRENCY_FMT = JsCode("""
function(params) {
    if (params.value == null) return '';
    var opts = {minimumFractionDigits: 2, maximumFractionDigits: 2};
    return '$' + params.value.toLocaleString('en-US', opts);
}
""")
"""
Format a number as US-dollar currency with two decimal places.
"""

LARGE_CURRENCY_FMT = JsCode("""
function(params) {
    if (params.value == null) return '';
    var v = params.value;
    if (Math.abs(v) >= 1e12) return '$' + (v / 1e12).toFixed(1) + 'T';
    if (Math.abs(v) >= 1e9) return '$' + (v / 1e9).toFixed(1) + 'B';
    if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K';
    return '$' + v.toFixed(2);
}
""")
"""
Format a large currency value with T/B/M/K abbreviation.
"""

PERCENTAGE_FMT = JsCode("""
function(params) {
    if (params.value == null) return '';
    return (params.value * 100).toFixed(1) + '%';
}
""")
"""
Format a decimal ratio as a percentage (0.15 -> '15.0%').
"""

LARGE_NUMBER_FMT = JsCode("""
function(params) {
    if (params.value == null) return '';
    var v = params.value;
    if (Math.abs(v) >= 1e12) return (v / 1e12).toFixed(1) + 'T';
    if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(1) + 'B';
    if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(1) + 'K';
    return v.toLocaleString('en-US');
}
""")
"""
Format a large number with T/B/M/K abbreviation (no currency symbol).
"""

RATIO_FMT = JsCode("""
function(params) {
    if (params.value == null) return '';
    return params.value.toFixed(1) + 'x';
}
""")
"""
Format a ratio value with one decimal and trailing 'x' (e.g. '12.3x').
"""

PCT_STYLE = JsCode("""
function(params) {
    if (params.value > 0) return { color: '#16a34a' };
    if (params.value < 0) return { color: '#dc2626' };
    return null;
}
""")
"""
Colour positive values green and negative values red.
"""

ANALYST_STYLE = JsCode("""
function(params) {
    if (params.value == null) return null;
    var v = params.value.toLowerCase();
    if (v.indexOf('strong buy') !== -1) return { color: '#15803d' };
    if (v.indexOf('buy') !== -1) return { color: '#16a34a' };
    if (v.indexOf('hold') !== -1) return { color: '#d97706' };
    if (v.indexOf('sell') !== -1) return { color: '#dc2626' };
    return null;
}
""")
"""
Colour-coded analyst rating: strong-buy dark-green, buy green, hold amber, sell red.
"""

IDENTIFIER_TOOLTIP = JsCode("""
class IdentifierTooltip {
    init(params) {
        this.eGui = document.createElement('div');
        var s = this.eGui.style;
        s.backgroundColor = '#ffffff';
        s.color = '#31333F';
        s.padding = '10px 14px';
        s.borderRadius = '6px';
        s.fontSize = '13px';
        s.lineHeight = '1.8';
        s.userSelect = 'text';
        s.cursor = 'text';
        s.border = '1px solid #e6e9ef';
        s.boxShadow = '0 2px 6px rgba(0,0,0,0.08)';
        s.maxWidth = '400px';

        var data = params.data;
        var items = [
            ['FIGI', data['Share Class FIGI']],
            ['ISIN', data['ISIN']],
            ['CUSIP', data['CUSIP']],
            ['CIK', data['CIK']],
            ['LEI', data['LEI']],
            ['MICs', data['MICs']]
        ];
        var html = '';
        for (var i = 0; i < items.length; i++) {
            if (items[i][1]) {
                html += '<div style="white-space:nowrap">'
                    + '<span style="color:#808495">' + items[i][0] + ':</span> '
                    + items[i][1] + '</div>';
            }
        }
        this.eGui.innerHTML = html;
    }
    getGui() { return this.eGui; }
}
""")
"""
Tooltip showing FIGI/ISIN/CUSIP/CIK/LEI/MICs for the hovered row.
"""

TOOLTIP_VALUE_GETTER = JsCode("""
function(params) {
    var fields = ['ISIN', 'CUSIP', 'CIK', 'LEI', 'Share Class FIGI', 'MICs'];
    for (var i = 0; i < fields.length; i++) {
        if (params.data[fields[i]]) return true;
    }
    return null;
}
""")
"""
Return truthy when any identifier field is present, triggering the tooltip.
"""

QUICK_FILTER_TEXT = JsCode("""
function(params) {
    var d = params.data;
    var parts = [d['Name'] || ''];
    var fields = ['ISIN', 'CUSIP', 'CIK', 'LEI', 'Share Class FIGI'];
    for (var i = 0; i < fields.length; i++) {
        if (d[fields[i]]) parts.push(d[fields[i]]);
    }
    return parts.join(' ');
}
""")
"""
Concatenate name + identifier fields for quick-filter search.
"""
