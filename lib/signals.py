"""Technical and fundamental signal scoring (educational, NOT buy/sell)."""

import numpy as np


def _safe(val, default=0):
    """Return val if not None/NaN, else default."""
    if val is None:
        return default
    try:
        if np.isnan(val):
            return default
    except (TypeError, ValueError):
        pass
    return val


# ── Technical score (0-100) ──

def compute_technical_score(closes: list, high_52w=None, low_52w=None,
                            sma50=None, sma200=None) -> tuple[int, list[str]]:
    """Return (score 0-100, list of driver strings)."""
    if len(closes) < 20:
        return 50, ["Data tidak cukup"]

    score = 50  # neutral start
    drivers = []
    price = closes[-1]

    # RSI-14
    if len(closes) >= 15:
        deltas = np.diff(closes[-15:])
        gains = np.mean([d for d in deltas if d > 0]) if any(d > 0 for d in deltas) else 0
        losses = abs(np.mean([d for d in deltas if d < 0])) if any(d < 0 for d in deltas) else 0.001
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))

        if rsi > 70:
            score += 5
            drivers.append(f"RSI {rsi:.0f} – Momentum sangat kuat")
        elif rsi > 55:
            score += 10
            drivers.append(f"RSI {rsi:.0f} – Momentum positif")
        elif rsi < 30:
            score -= 10
            drivers.append(f"RSI {rsi:.0f} – Oversold")
        elif rsi < 45:
            score -= 5
            drivers.append(f"RSI {rsi:.0f} – Momentum lemah")
        else:
            drivers.append(f"RSI {rsi:.0f} – Netral")

    # SMA 20 vs price
    sma20 = np.mean(closes[-20:]) if len(closes) >= 20 else None
    if sma20:
        if price > sma20:
            score += 8
            drivers.append("Harga di atas SMA-20")
        else:
            score -= 8
            drivers.append("Harga di bawah SMA-20")

    # SMA 50
    if sma50:
        if price > sma50:
            score += 8
            drivers.append("Harga di atas SMA-50")
        else:
            score -= 8
            drivers.append("Harga di bawah SMA-50")

    # SMA 200 (major trend)
    if sma200:
        if price > sma200:
            score += 12
            drivers.append("Tren jangka panjang positif (di atas SMA-200)")
        else:
            score -= 12
            drivers.append("Tren jangka panjang negatif (di bawah SMA-200)")

    # 52-week range position
    if high_52w and low_52w and high_52w > low_52w:
        pos = (price - low_52w) / (high_52w - low_52w) * 100
        if pos > 80:
            score += 7
            drivers.append(f"Dekat 52-week high ({pos:.0f}% range)")
        elif pos > 50:
            score += 3
            drivers.append(f"Di paruh atas 52-week range ({pos:.0f}%)")
        elif pos < 20:
            score -= 7
            drivers.append(f"Dekat 52-week low ({pos:.0f}% range)")
        else:
            score -= 3
            drivers.append(f"Di paruh bawah 52-week range ({pos:.0f}%)")

    return max(0, min(100, score)), drivers


# ── Fundamental score (0-100) ──

def compute_fundamental_score(fundamentals: dict) -> tuple[int, list[str]]:
    """Return (score 0-100, list of driver strings)."""
    score = 50
    drivers = []

    # ROE
    roe = _safe(fundamentals.get("returnOnEquity"))
    if roe:
        roe_pct = roe * 100
        if roe_pct > 20:
            score += 12
            drivers.append(f"ROE {roe_pct:.1f}% – Profitabilitas tinggi")
        elif roe_pct > 10:
            score += 6
            drivers.append(f"ROE {roe_pct:.1f}% – Profitabilitas baik")
        elif roe_pct > 0:
            drivers.append(f"ROE {roe_pct:.1f}% – Profitabilitas moderat")
        else:
            score -= 10
            drivers.append(f"ROE {roe_pct:.1f}% – Profitabilitas rendah")

    # Profit margins
    margin = _safe(fundamentals.get("profitMargins"))
    if margin:
        m_pct = margin * 100
        if m_pct > 20:
            score += 8
            drivers.append(f"Margin laba {m_pct:.1f}% – Sangat sehat")
        elif m_pct > 10:
            score += 4
            drivers.append(f"Margin laba {m_pct:.1f}% – Sehat")
        elif m_pct > 0:
            drivers.append(f"Margin laba {m_pct:.1f}% – Tipis")
        else:
            score -= 8
            drivers.append(f"Margin laba {m_pct:.1f}% – Negatif")

    # D/E ratio
    de = _safe(fundamentals.get("debtToEquity"))
    if de:
        if de < 50:
            score += 8
            drivers.append(f"D/E {de:.0f}% – Leverage rendah")
        elif de < 100:
            score += 3
            drivers.append(f"D/E {de:.0f}% – Leverage moderat")
        elif de < 200:
            score -= 3
            drivers.append(f"D/E {de:.0f}% – Leverage tinggi")
        else:
            score -= 8
            drivers.append(f"D/E {de:.0f}% – Leverage sangat tinggi")

    # P/E ratio
    pe = _safe(fundamentals.get("trailingPE"))
    if pe and pe > 0:
        if pe < 10:
            score += 8
            drivers.append(f"P/E {pe:.1f}x – Valuasi rendah")
        elif pe < 20:
            score += 4
            drivers.append(f"P/E {pe:.1f}x – Valuasi wajar")
        elif pe < 35:
            score -= 2
            drivers.append(f"P/E {pe:.1f}x – Valuasi tinggi")
        else:
            score -= 6
            drivers.append(f"P/E {pe:.1f}x – Valuasi premium")

    # Revenue growth
    rev_g = _safe(fundamentals.get("revenueGrowth"))
    if rev_g:
        rg_pct = rev_g * 100
        if rg_pct > 20:
            score += 8
            drivers.append(f"Pertumbuhan pendapatan {rg_pct:.1f}% – Kuat")
        elif rg_pct > 5:
            score += 4
            drivers.append(f"Pertumbuhan pendapatan {rg_pct:.1f}% – Stabil")
        elif rg_pct > 0:
            drivers.append(f"Pertumbuhan pendapatan {rg_pct:.1f}% – Lambat")
        else:
            score -= 6
            drivers.append(f"Pertumbuhan pendapatan {rg_pct:.1f}% – Menurun")

    # Current ratio
    cr = _safe(fundamentals.get("currentRatio"))
    if cr:
        if cr > 2:
            score += 5
            drivers.append(f"Current ratio {cr:.1f}x – Likuiditas kuat")
        elif cr > 1:
            score += 2
            drivers.append(f"Current ratio {cr:.1f}x – Likuiditas cukup")
        else:
            score -= 5
            drivers.append(f"Current ratio {cr:.1f}x – Likuiditas rendah")

    return max(0, min(100, score)), drivers


def at_a_glance(price, fundamentals, closes) -> list[dict]:
    """Return list of factual 'at a glance' chips (neutral language)."""
    chips = []

    # Trend
    sma200 = _safe(fundamentals.get("twoHundredDayAverage"))
    if sma200 and price:
        if price > sma200:
            chips.append({"label": "Tren", "value": "Di atas SMA-200", "color": "#00d4aa"})
        else:
            chips.append({"label": "Tren", "value": "Di bawah SMA-200", "color": "#ff4757"})

    # Momentum (RSI)
    if len(closes) >= 15:
        deltas = np.diff(closes[-15:])
        gains = np.mean([d for d in deltas if d > 0]) if any(d > 0 for d in deltas) else 0
        losses = abs(np.mean([d for d in deltas if d < 0])) if any(d < 0 for d in deltas) else 0.001
        rsi = 100 - (100 / (1 + gains / losses))
        if rsi > 70:
            chips.append({"label": "Momentum", "value": "Sangat kuat", "color": "#00d4aa"})
        elif rsi > 55:
            chips.append({"label": "Momentum", "value": "Positif", "color": "#00d4aa"})
        elif rsi < 30:
            chips.append({"label": "Momentum", "value": "Oversold", "color": "#ff4757"})
        elif rsi < 45:
            chips.append({"label": "Momentum", "value": "Lemah", "color": "#ff4757"})
        else:
            chips.append({"label": "Momentum", "value": "Netral", "color": "#888"})

    # 52-week range
    h52 = _safe(fundamentals.get("fiftyTwoWeekHigh"))
    l52 = _safe(fundamentals.get("fiftyTwoWeekLow"))
    if h52 and l52 and h52 > l52 and price:
        pos = (price - l52) / (h52 - l52) * 100
        chips.append({"label": "52-Week Range", "value": f"{pos:.0f}%", "color": "#00d4aa" if pos > 50 else "#ff4757"})

    # ROE
    roe = _safe(fundamentals.get("returnOnEquity"))
    if roe:
        roe_pct = roe * 100
        if roe_pct > 15:
            chips.append({"label": "Profitabilitas", "value": f"ROE {roe_pct:.1f}%", "color": "#00d4aa"})
        else:
            chips.append({"label": "Profitabilitas", "value": f"ROE {roe_pct:.1f}%", "color": "#888"})

    # D/E
    de = _safe(fundamentals.get("debtToEquity"))
    if de:
        label = "Rendah" if de < 50 else ("Moderat" if de < 150 else "Tinggi")
        chips.append({"label": "Leverage", "value": f"D/E {de:.0f}% ({label})", "color": "#00d4aa" if de < 100 else "#ff4757"})

    # Beta
    beta = _safe(fundamentals.get("beta"))
    if beta:
        label = "Rendah" if beta < 0.8 else ("Normal" if beta < 1.2 else "Tinggi")
        chips.append({"label": "Volatilitas", "value": f"Beta {beta:.2f} ({label})", "color": "#888"})

    # P/E
    pe = _safe(fundamentals.get("trailingPE"))
    if pe and pe > 0:
        label = "Rendah" if pe < 12 else ("Wajar" if pe < 25 else "Premium")
        chips.append({"label": "Valuasi", "value": f"P/E {pe:.1f}x ({label})", "color": "#888"})

    return chips
