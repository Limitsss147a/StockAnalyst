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
    "^TNX": "US 10Y Yield",
}

# Latest known Indonesian macro data (updated periodically)
# These would ideally come from BPS/BI API, but we use static + live rates
INDO_MACRO_DATA = {
    "BI Rate": {"value": "6.25%", "description": "Suku bunga acuan Bank Indonesia (BI-Rate)", "status": "Ditahan"},
    "Inflasi (YoY)": {"value": "2.51%", "description": "Inflasi Indeks Harga Konsumen (BPS)", "status": "Terkendali"},
    "Pertumbuhan Ekonomi": {"value": "5.11%", "description": "Pertumbuhan PDB Q1 2024 YoY", "status": "Solid"},
    "Cadangan Devisa": {"value": "$136.2B", "description": "Posisi akhir April 2024", "status": "Cukup"},
    "Neraca Perdagangan": {"value": "$2.93B", "description": "Surplus April 2024", "status": "Surplus"},
    "Tingkat Pengangguran": {"value": "4.82%", "description": "Tingkat Pengangguran Terbuka (BPS)", "status": "Turun"},
}

def get_historical_macro_data() -> pd.DataFrame:
    """Get historical macro data for BI Rate and Inflation (mock real data for visualization)."""
    dates = pd.date_range(start="2023-01-01", periods=18, freq="ME")
    bi_rate = [5.50, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 5.75, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.25, 6.25, 6.25]
    inflation = [5.28, 5.47, 4.97, 4.33, 4.00, 3.52, 3.08, 3.27, 2.28, 2.56, 2.86, 2.61, 2.57, 2.75, 3.05, 3.00, 2.84, 2.51]
    
    return pd.DataFrame({
        "Date": dates,
        "BI Rate (%)": bi_rate,
        "Inflasi YoY (%)": inflation
    }).set_index("Date")


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
    """Get live macro data from market tickers, including history for sparklines."""
    snapshot = {}
    for ticker, name in MACRO_TICKERS.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1mo")
            if not hist.empty:
                closes = hist["Close"].tolist()
                price = closes[-1]
                prev = closes[-2] if len(closes) > 1 else price
                pct = ((price - prev) / prev * 100) if prev else 0
                snapshot[name] = {"price": price, "change_pct": pct, "history": closes}
            else:
                snapshot[name] = {"price": 0, "change_pct": 0, "history": []}
        except Exception:
            snapshot[name] = {"price": 0, "change_pct": 0, "history": []}
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
