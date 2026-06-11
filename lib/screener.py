"""Stock screener logic for filtering IDX stocks by criteria."""

import streamlit as st
from lib.market_data import get_quote, get_history, get_stock_fundamentals, TOP_IDX_STOCKS
from lib.technicals import quick_screen_indicators


@st.cache_data(ttl=120, show_spinner=False)
def screen_stocks(tickers: list = None,
                  min_rsi: float = 0, max_rsi: float = 100,
                  above_sma20: bool | None = None,
                  above_sma50: bool | None = None,
                  above_sma200: bool | None = None,
                  min_pe: float = 0, max_pe: float = 9999,
                  min_roe: float = -999, max_roe: float = 999,
                  min_mcap: float = 0,
                  volume_surge: bool = False) -> list:
    """Screen stocks based on technical and fundamental criteria.

    Returns list of dicts with stock data + indicator values.
    """
    if tickers is None:
        tickers = TOP_IDX_STOCKS[:35]

    results = []
    for ticker in tickers:
        try:
            q = get_quote(ticker)
            if q.get("price", 0) <= 0:
                continue

            hist = get_history(ticker, "6mo")
            if hist.empty or len(hist) < 15:
                continue

            closes = hist["Close"].dropna().tolist()
            indicators = quick_screen_indicators(closes)

            # Fundamental data
            fund = get_stock_fundamentals(ticker)

            pe = fund.get("trailingPE") or 0
            roe = (fund.get("returnOnEquity") or 0) * 100
            mcap = q.get("marketCap", 0) or 0

            # Volume surge check
            vol_surge = False
            if "Volume" in hist.columns and len(hist) >= 20:
                avg_vol = hist["Volume"].tail(20).mean()
                last_vol = hist["Volume"].iloc[-1]
                if avg_vol > 0 and last_vol > 2 * avg_vol:
                    vol_surge = True

            # Apply filters
            rsi = indicators.get("rsi", 50)
            if rsi < min_rsi or rsi > max_rsi:
                continue
            if above_sma20 is not None and indicators.get("above_sma20") != above_sma20:
                continue
            if above_sma50 is not None and indicators.get("above_sma50") is not None:
                if indicators["above_sma50"] != above_sma50:
                    continue
            if above_sma200 is not None and indicators.get("above_sma200") is not None:
                if indicators["above_sma200"] != above_sma200:
                    continue
            if pe > 0 and (pe < min_pe or pe > max_pe):
                continue
            if roe < min_roe or roe > max_roe:
                continue
            if mcap < min_mcap:
                continue
            if volume_surge and not vol_surge:
                continue

            results.append({
                "ticker": ticker,
                "name": q.get("name", ticker),
                "price": q.get("price", 0),
                "pctChange": q.get("pctChange", 0),
                "volume": q.get("volume", 0),
                "marketCap": mcap,
                "sector": q.get("sector", "N/A"),
                "rsi": rsi,
                "above_sma20": indicators.get("above_sma20"),
                "above_sma50": indicators.get("above_sma50"),
                "above_sma200": indicators.get("above_sma200"),
                "pe": pe,
                "roe": roe,
                "vol_surge": vol_surge,
            })
        except Exception:
            continue

    return results


# Preset screener filters
PRESETS = {
    "Oversold (RSI < 30)": {"min_rsi": 0, "max_rsi": 30},
    "Overbought (RSI > 70)": {"min_rsi": 70, "max_rsi": 100},
    "Uptrend (Di atas SMA-200)": {"above_sma200": True},
    "Downtrend (Di bawah SMA-200)": {"above_sma200": False},
    "Value (P/E < 10)": {"min_pe": 0.1, "max_pe": 10},
    "High ROE (> 15%)": {"min_roe": 15},
    "Volume Surge (2x avg)": {"volume_surge": True},
}
