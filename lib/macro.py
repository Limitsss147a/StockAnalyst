"""Indonesian macro economic data helpers."""

import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# Key macro indicators for Indonesia (fetched via yfinance proxies)
MACRO_TICKERS = {
    "USDIDR=X": "Kurs USD/IDR",
    "^JKSE": "IHSG",
    "GC=F": "Emas (USD/oz)",
    "CL=F": "Minyak Mentah (USD/bbl)",
}

# Latest known Indonesian macro data (updated periodically)
# These would ideally come from BPS/BI API, but we use static + live rates
INDO_MACRO_DATA = {
    "BI Rate": {"value": "6.25%", "description": "Suku bunga acuan Bank Indonesia"},
    "Inflasi (YoY)": {"value": "~2.5%", "description": "Inflasi tahunan (BPS)"},
    "GDP Growth": {"value": "~5.0%", "description": "Pertumbuhan ekonomi tahunan"},
    "Cadangan Devisa": {"value": "~$140B", "description": "Cadangan devisa BI"},
    "Neraca Perdagangan": {"value": "Surplus", "description": "Neraca perdagangan Indonesia"},
    "Pengangguran": {"value": "~5.3%", "description": "Tingkat pengangguran terbuka (BPS)"},
}


@st.cache_data(ttl=600)
def get_exchange_rate_history(period="1y") -> pd.DataFrame:
    """Get USD/IDR exchange rate history."""
    try:
        t = yf.Ticker("USDIDR=X")
        return t.history(period=period)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_ihsg_history(period="1y") -> pd.DataFrame:
    """Get IHSG index history."""
    try:
        t = yf.Ticker("^JKSE")
        return t.history(period=period)
    except Exception:
        return pd.DataFrame()


def get_live_macro_snapshot() -> dict:
    """Get live macro data from market tickers."""
    snapshot = {}
    for ticker, name in MACRO_TICKERS.items():
        try:
            t = yf.Ticker(ticker)
            fi = t.fast_info
            price = fi.get("last_price", 0)
            prev = fi.get("previous_close", 0)
            pct = ((price - prev) / prev * 100) if prev else 0
            snapshot[name] = {"price": price, "change_pct": pct}
        except Exception:
            snapshot[name] = {"price": 0, "change_pct": 0}
    return snapshot


def render_exchange_rate_chart(df: pd.DataFrame) -> go.Figure:
    """Render USD/IDR exchange rate chart."""
    if df.empty:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines", line=dict(color="#00d4aa", width=2),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
        hovertemplate="Rp%{y:,.0f}<extra>USD/IDR</extra>",
    ))
    fig.update_layout(
        template="plotly_dark",
        title="Kurs USD/IDR",
        height=350,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Rupiah per USD",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        font=dict(family="Inter"),
    )
    return fig
