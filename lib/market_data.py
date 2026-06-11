"""Market data wrappers using yfinance for Indonesian stocks (IDX)."""

import yfinance as yf
import pandas as pd
import streamlit as st

# ── Index / Asset tickers shown on Market Pulse ──
INDEX_TICKERS = {
    "^JKSE":      {"name": "IHSG",          "emoji": "🇮🇩"},
    "USDIDR=X":   {"name": "USD/IDR",       "emoji": "💱"},
    "GC=F":       {"name": "Emas",          "emoji": "🥇"},
    "CL=F":       {"name": "Minyak Mentah", "emoji": "🛢️"},
    "BTC-USD":    {"name": "Bitcoin",       "emoji": "₿"},
    "^GSPC":      {"name": "S&P 500",       "emoji": "🇺🇸"},
    "^HSI":       {"name": "Hang Seng",     "emoji": "🇭🇰"},
    "^N225":      {"name": "Nikkei 225",    "emoji": "🇯🇵"},
    "^STI":       {"name": "STI",           "emoji": "🇸🇬"},
    "DX-Y.NYB":   {"name": "DXY",           "emoji": "💵"},
}

# ── Sector representatives (proxy for IDX sectors) ──
SECTOR_STOCKS = {
    "BBCA.JK": "Perbankan",
    "TLKM.JK": "Telekomunikasi",
    "ASII.JK": "Otomotif",
    "UNVR.JK": "Konsumer",
    "ADRO.JK": "Pertambangan",
    "BSDE.JK": "Properti",
    "TOWR.JK": "Infrastruktur",
    "KLBF.JK": "Kesehatan",
    "PGAS.JK": "Energi",
    "GOTO.JK": "Teknologi",
    "SMGR.JK": "Material Dasar",
}

# ── Period map for yfinance ──
PERIOD_MAP = {
    "1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo",
    "6M": "6mo", "YTD": "ytd", "1Y": "1y", "3Y": "3y",
    "5Y": "5y", "10Y": "10y", "Max": "max",
}

# ── Blue-chip IDX stocks ──
TOP_IDX_STOCKS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK",
    "ASII.JK", "UNVR.JK", "HMSP.JK", "ICBP.JK", "KLBF.JK",
    "SMGR.JK", "INDF.JK", "GGRM.JK", "ADRO.JK", "PTBA.JK",
    "ANTM.JK", "INCO.JK", "MDKA.JK", "EXCL.JK", "ISAT.JK",
    "TOWR.JK", "TBIG.JK", "ACES.JK", "ERAA.JK", "MAPI.JK",
    "PGAS.JK", "AKRA.JK", "BSDE.JK", "CTRA.JK", "SMRA.JK",
    "GOTO.JK", "EMTK.JK", "SIDO.JK", "AUTO.JK", "JSMR.JK",
    "BRPT.JK", "TPIA.JK", "ITMG.JK", "MEDC.JK", "BUKA.JK",
]


def _interval_for_period(period: str) -> str:
    """Choose chart interval based on period."""
    if period in ("1d",):
        return "5m"
    if period in ("5d",):
        return "15m"
    if period in ("1mo",):
        return "1h"
    return "1d"


@st.cache_data(ttl=60)
def get_quote(ticker: str) -> dict:
    """Get current quote for a single ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        fi = t.fast_info

        price = fi.get("last_price") or info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev = fi.get("previous_close") or info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        change = (price - prev) if price and prev else 0
        pct = (change / prev * 100) if prev else 0

        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName", ticker.replace(".JK", "")),
            "price": price or 0,
            "previousClose": prev or 0,
            "change": change,
            "pctChange": pct,
            "volume": info.get("volume") or fi.get("last_volume", 0),
            "marketCap": info.get("marketCap", 0),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        }
    except Exception as e:
        return {
            "ticker": ticker, "name": ticker.replace(".JK", ""),
            "price": 0, "previousClose": 0, "change": 0, "pctChange": 0,
            "volume": 0, "marketCap": 0, "sector": "N/A", "industry": "N/A",
            "error": str(e),
        }


@st.cache_data(ttl=300)
def get_history(ticker: str, period: str = "1y", interval: str | None = None) -> pd.DataFrame:
    """Get OHLCV history for a ticker."""
    try:
        t = yf.Ticker(ticker)
        iv = interval or _interval_for_period(period)
        df = t.history(period=period, interval=iv)
        if df.empty:
            return pd.DataFrame()
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_quotes_bulk(tickers: list) -> dict:
    """Get quotes for a list of tickers."""
    return {t: get_quote(t) for t in tickers}


@st.cache_data(ttl=300)
def get_history_bulk(tickers: list, period: str = "1y") -> dict:
    """Get history for a list of tickers."""
    return {t: get_history(t, period) for t in tickers}


@st.cache_data(ttl=300)
def get_stock_fundamentals(ticker: str) -> dict:
    """Get fundamental data for a stock."""
    try:
        info = yf.Ticker(ticker).info
        keys = [
            "trailingPE", "forwardPE", "priceToBook", "dividendYield", "beta",
            "marketCap", "enterpriseValue", "profitMargins", "grossMargins",
            "operatingMargins", "returnOnEquity", "returnOnAssets", "debtToEquity",
            "currentRatio", "quickRatio", "revenueGrowth", "earningsGrowth",
            "totalRevenue", "totalDebt", "totalCash", "freeCashflow",
            "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage",
            "twoHundredDayAverage", "averageVolume", "shortName", "longName",
            "sector", "industry", "longBusinessSummary", "website", "country",
            "currency", "targetMeanPrice", "recommendationKey",
            "numberOfAnalystOpinions",
        ]
        return {k: info.get(k) for k in keys}
    except Exception:
        return {}


@st.cache_data(ttl=300)
def get_previous_close(ticker: str) -> float:
    """Get yesterday's closing price (for 1D baseline)."""
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        return fi.get("previous_close", 0) or 0
    except Exception:
        return 0


# ── Formatting helpers ──

def format_idr(value, compact=True):
    """Format number as Indonesian Rupiah."""
    if value is None or value == 0:
        return "N/A"
    if compact:
        if abs(value) >= 1e12:
            return f"Rp{value / 1e12:,.1f}T"
        if abs(value) >= 1e9:
            return f"Rp{value / 1e9:,.1f}M"
        if abs(value) >= 1e6:
            return f"Rp{value / 1e6:,.1f}Jt"
        return f"Rp{value:,.0f}"
    return f"Rp{value:,.0f}"


def format_number(value, suffix="", prefix="", decimals=2):
    """Format a number with optional prefix/suffix."""
    if value is None:
        return "N/A"
    return f"{prefix}{value:,.{decimals}f}{suffix}"


def format_pct(value, decimals=2):
    """Format as percentage."""
    if value is None:
        return "N/A"
    return f"{value:+.{decimals}f}%"


def color_for_change(value):
    """Return CSS color for positive/negative."""
    if value is None:
        return "#888"
    return "#00d4aa" if value >= 0 else "#ff4757"
