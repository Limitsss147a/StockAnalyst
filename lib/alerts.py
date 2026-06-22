"""Alert detection engine for watchlist monitoring."""

import pandas as pd
import numpy as np
import streamlit as st
from lib.market_data import get_history
from lib.technicals import (
    calc_rsi, calc_macd, calc_sma, calc_stochastic,
    calc_bollinger_bands, calc_atr,
)


def check_stock_alerts(ticker: str):
    """
    Comprehensive alert scan for a single stock.
    Returns list of dicts: {"emoji", "title", "detail", "severity"}
    severity: "critical" | "warning" | "info"
    """
    alerts = []

    # Use 1 year of data to ensure SMA-200 has enough history
    hist = get_history(ticker, "1y")
    if hist.empty or len(hist) < 50:
        return alerts

    close = hist["Close"]
    high = hist["High"]
    low = hist["Low"]
    current_price = close.iloc[-1]

    # Compute indicators
    rsi = calc_rsi(close, 14)
    macd_line, macd_signal, macd_hist = calc_macd(close)
    sma_20 = calc_sma(close, 20)
    sma_50 = calc_sma(close, 50)
    sma_200 = calc_sma(close, 200)
    stoch_k, stoch_d = calc_stochastic(high, low, close)
    bb_upper, bb_mid, bb_lower = calc_bollinger_bands(close, 20, 2)
    atr = calc_atr(high, low, close)
    atr_val = atr.iloc[-1]

    curr_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2] if len(rsi) >= 2 else curr_rsi

    curr_macd = macd_hist.iloc[-1]
    prev_macd = macd_hist.iloc[-2] if len(macd_hist) >= 2 else curr_macd

    curr_k = stoch_k.iloc[-1]
    curr_d = stoch_d.iloc[-1]
    prev_k = stoch_k.iloc[-2] if len(stoch_k) >= 2 else curr_k

    curr_sma50 = sma_50.iloc[-1]
    prev_sma50 = sma_50.iloc[-2] if len(sma_50) >= 2 else curr_sma50
    curr_sma200 = sma_200.iloc[-1]
    prev_sma200 = sma_200.iloc[-2] if len(sma_200) >= 2 else curr_sma200

    # ── 1. RSI Alerts ──
    if curr_rsi < 30:
        alerts.append({
            "emoji": "📉", "title": "RSI Oversold",
            "detail": f"RSI(14) = {curr_rsi:.1f} — Saham sudah dalam zona jenuh jual, potensi rebound.",
            "severity": "critical"
        })
    elif curr_rsi > 70:
        alerts.append({
            "emoji": "📈", "title": "RSI Overbought",
            "detail": f"RSI(14) = {curr_rsi:.1f} — Saham sudah dalam zona jenuh beli, waspada koreksi.",
            "severity": "warning"
        })

    # RSI divergence (price makes new low but RSI makes higher low — bullish divergence)
    if len(close) >= 20:
        price_recent_low = close.iloc[-10:].min()
        price_prev_low = close.iloc[-20:-10].min()
        rsi_recent_low = rsi.iloc[-10:].min()
        rsi_prev_low = rsi.iloc[-20:-10].min()
        if price_recent_low < price_prev_low and rsi_recent_low > rsi_prev_low and curr_rsi < 40:
            alerts.append({
                "emoji": "🔀", "title": "Bullish RSI Divergence",
                "detail": "Harga membuat lower low tetapi RSI membuat higher low — sinyal pembalikan arah naik.",
                "severity": "critical"
            })

    # ── 2. MACD Alerts ──
    if prev_macd < 0 and curr_macd >= 0:
        alerts.append({
            "emoji": "✨", "title": "MACD Golden Cross",
            "detail": "Histogram MACD baru berubah positif — momentum bullish dimulai.",
            "severity": "critical"
        })
    elif prev_macd >= 0 and curr_macd < 0:
        alerts.append({
            "emoji": "💀", "title": "MACD Death Cross",
            "detail": "Histogram MACD baru berubah negatif — momentum bearish dimulai.",
            "severity": "critical"
        })

    # ── 3. SMA Support/Resistance ──
    if pd.notna(curr_sma200):
        dist_to_sma200 = (current_price - curr_sma200) / curr_sma200 * 100
        if 0 <= dist_to_sma200 <= 2:
            alerts.append({
                "emoji": "🛡️", "title": "Mendekati Support SMA-200",
                "detail": f"Harga Rp{current_price:,.0f} hanya {dist_to_sma200:.1f}% di atas SMA-200 (Rp{curr_sma200:,.0f}).",
                "severity": "warning"
            })
        elif -2 <= dist_to_sma200 < 0:
            alerts.append({
                "emoji": "🚨", "title": "Breakdown di Bawah SMA-200",
                "detail": f"Harga Rp{current_price:,.0f} jatuh di bawah SMA-200 (Rp{curr_sma200:,.0f}) — sinyal bearish kuat.",
                "severity": "critical"
            })

    # ── 4. Golden Cross / Death Cross (SMA-50 vs SMA-200) ──
    if pd.notna(prev_sma50) and pd.notna(prev_sma200):
        if prev_sma50 < prev_sma200 and curr_sma50 >= curr_sma200:
            alerts.append({
                "emoji": "🌟", "title": "Golden Cross (SMA-50 × SMA-200)",
                "detail": "SMA-50 baru saja menembus ke atas SMA-200 — sinyal tren naik jangka panjang.",
                "severity": "critical"
            })
        elif prev_sma50 >= prev_sma200 and curr_sma50 < curr_sma200:
            alerts.append({
                "emoji": "☠️", "title": "Death Cross (SMA-50 × SMA-200)",
                "detail": "SMA-50 baru saja menembus ke bawah SMA-200 — sinyal tren turun jangka panjang.",
                "severity": "critical"
            })

    # ── 5. Stochastic Alerts ──
    if prev_k < 20 and curr_k >= 20 and curr_k > curr_d:
        alerts.append({
            "emoji": "⚡", "title": "Stochastic Golden Cross (Oversold)",
            "detail": f"%K({curr_k:.0f}) naik menembus %D({curr_d:.0f}) dari zona oversold.",
            "severity": "warning"
        })

    # ── 6. Bollinger Band Alerts ──
    if pd.notna(bb_lower.iloc[-1]):
        if low.iloc[-1] <= bb_lower.iloc[-1] and close.iloc[-1] > bb_lower.iloc[-1]:
            alerts.append({
                "emoji": "📊", "title": "Pantulan dari Lower Bollinger Band",
                "detail": f"Harga menyentuh lower band (Rp{bb_lower.iloc[-1]:,.0f}) dan memantul — potensi rebound.",
                "severity": "warning"
            })
    if pd.notna(bb_upper.iloc[-1]):
        if high.iloc[-1] >= bb_upper.iloc[-1] and close.iloc[-1] < bb_upper.iloc[-1]:
            alerts.append({
                "emoji": "⚠️", "title": "Ditolak dari Upper Bollinger Band",
                "detail": f"Harga mencapai upper band (Rp{bb_upper.iloc[-1]:,.0f}) dan tertolak — potensi koreksi.",
                "severity": "info"
            })

    # ── 7. Volume Surge ──
    if "Volume" in hist.columns:
        vol = hist["Volume"]
        avg_vol = vol.tail(20).mean()
        last_vol = vol.iloc[-1]
        if avg_vol > 0:
            vol_ratio = last_vol / avg_vol
            if vol_ratio >= 3:
                alerts.append({
                    "emoji": "🔥", "title": "Volume Surge Besar",
                    "detail": f"Volume {vol_ratio:.1f}x lipat di atas rata-rata 20 hari — pergerakan signifikan.",
                    "severity": "critical"
                })
            elif vol_ratio >= 2:
                alerts.append({
                    "emoji": "📢", "title": "Volume Di Atas Rata-rata",
                    "detail": f"Volume {vol_ratio:.1f}x lipat di atas rata-rata — ada ketertarikan pasar.",
                    "severity": "info"
                })

    # ── 8. 52-Week High/Low Proximity ──
    high_52w = high.max()
    low_52w = low.min()
    if current_price >= high_52w * 0.98:
        alerts.append({
            "emoji": "🏔️", "title": "Mendekati Harga Tertinggi 52 Minggu",
            "detail": f"Harga Rp{current_price:,.0f} mendekati 52W High (Rp{high_52w:,.0f}) — All-Time High breakout?",
            "severity": "info"
        })
    elif current_price <= low_52w * 1.05:
        alerts.append({
            "emoji": "🕳️", "title": "Mendekati Harga Terendah 52 Minggu",
            "detail": f"Harga Rp{current_price:,.0f} mendekati 52W Low (Rp{low_52w:,.0f}) — Sangat murah atau ada masalah?",
            "severity": "warning"
        })

    return alerts


def format_alerts_html(alerts: list) -> str:
    """Format alerts into styled HTML for Streamlit display."""
    if not alerts:
        return ""
    
    severity_styles = {
        "critical": "border-left:4px solid #ff4757;background:rgba(255,71,87,0.08);",
        "warning": "border-left:4px solid #f59e0b;background:rgba(245,158,11,0.08);",
        "info": "border-left:4px solid #3b82f6;background:rgba(59,130,246,0.08);",
    }
    
    html_parts = []
    for a in alerts:
        style = severity_styles.get(a["severity"], severity_styles["info"])
        html_parts.append(f"""
        <div style="{style}padding:10px 14px;margin:6px 0;border-radius:8px;">
            <b>{a['emoji']} {a['title']}</b><br>
            <span style="color:#aaa;font-size:0.85rem;">{a['detail']}</span>
        </div>
        """)
    
    return "\n".join(html_parts)


def format_alerts_telegram(ticker: str, alerts: list) -> str:
    """Format alerts into a Telegram-ready HTML message for one ticker."""
    if not alerts:
        return ""
    
    severity_label = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    
    lines = [f"📌 <b>{ticker.replace('.JK', '')}</b>"]
    for a in alerts:
        icon = severity_label.get(a["severity"], "🔵")
        lines.append(f"  {icon} {a['emoji']} <b>{a['title']}</b>")
        lines.append(f"     {a['detail']}")
    
    return "\n".join(lines)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_total_watchlist_alerts() -> int:
    """Calculate the total number of alerts across the entire watchlist."""
    from lib.watchlist import load_watchlist
    from lib.market_data import get_quote
    
    watchlist = load_watchlist()
    total = 0
    for item in watchlist:
        t = item["ticker"]
        alerts = check_stock_alerts(t)
        total += len(alerts)
        
        q = get_quote(t)
        price = q.get("price", 0)
        tb = item.get("target_buy", 0)
        ts = item.get("target_sell", 0)
        
        if tb > 0 and price > 0 and price <= tb:
            total += 1
        if ts > 0 and price > 0 and price >= ts:
            total += 1
            
    return total
