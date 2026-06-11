"""News fetching using yfinance."""

import yfinance as yf
import streamlit as st
from datetime import datetime


@st.cache_data(ttl=300)
def get_ticker_news(ticker: str, max_items: int = 10) -> list:
    """Get news for a specific ticker."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        results = []
        for item in news[:max_items]:
            content = item.get("content", {}) if isinstance(item.get("content"), dict) else {}
            published = content.get("pubDate") or item.get("providerPublishTime", "")
            
            # Handle timestamp
            time_ago = ""
            if isinstance(published, (int, float)):
                dt = datetime.fromtimestamp(published)
                delta = datetime.now() - dt
                if delta.days > 0:
                    time_ago = f"{delta.days} hari lalu"
                elif delta.seconds > 3600:
                    time_ago = f"{delta.seconds // 3600} jam lalu"
                else:
                    time_ago = f"{delta.seconds // 60} menit lalu"
            elif isinstance(published, str) and published:
                time_ago = published[:19]

            results.append({
                "title": content.get("title") or item.get("title", "No title"),
                "publisher": content.get("provider", {}).get("displayName", "") if isinstance(content.get("provider"), dict) else item.get("publisher", ""),
                "link": content.get("canonicalUrl", {}).get("url", "") if isinstance(content.get("canonicalUrl"), dict) else item.get("link", ""),
                "time_ago": time_ago,
                "summary": content.get("summary", "") or "",
            })
        return results
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_market_news(max_items: int = 15) -> list:
    """Get aggregated market news from major IDX tickers."""
    tickers = ["^JKSE", "BBCA.JK", "BBRI.JK", "TLKM.JK"]
    all_news = []
    seen_titles = set()

    for ticker in tickers:
        news = get_ticker_news(ticker, max_items=5)
        for item in news:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_news.append(item)

    return all_news[:max_items]
