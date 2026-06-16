"""Automated technical analysis engine with timeframe-specific configurations."""

import numpy as np
import pandas as pd
from lib.technicals import (
    calc_sma, calc_ema, calc_rsi, calc_macd, calc_bollinger_bands,
    calc_stochastic, calc_atr,
)

# ── Timeframe configurations ──
TIMEFRAMES = {
    "Day Trade": {
        "label": "⚡ Day Trade",
        "description": "Intraday – 1 sampai beberapa jam",
        "period": "5d",
        "interval": "5m",
        "sma_fast": 9,
        "sma_mid": 21,
        "sma_slow": 50,
        "rsi_period": 9,
        "rsi_ob": 75,
        "rsi_os": 25,
        "macd_fast": 5,
        "macd_slow": 13,
        "macd_signal": 1,
        "bb_period": 10,
        "bb_std": 2.0,
        "stoch_k": 9,
        "stoch_d": 3,
        "atr_period": 10,
    },
    "Swing Trade": {
        "label": "🔄 Swing Trade",
        "description": "Beberapa hari sampai beberapa minggu",
        "period": "3mo",
        "interval": "1d",
        "sma_fast": 10,
        "sma_mid": 20,
        "sma_slow": 50,
        "rsi_period": 14,
        "rsi_ob": 70,
        "rsi_os": 30,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "bb_period": 20,
        "bb_std": 2.0,
        "stoch_k": 14,
        "stoch_d": 3,
        "atr_period": 14,
    },
    "Long Term": {
        "label": "📅 Long Term",
        "description": "Beberapa bulan sampai tahun",
        "period": "2y",
        "interval": "1d",
        "sma_fast": 50,
        "sma_mid": 100,
        "sma_slow": 200,
        "rsi_period": 14,
        "rsi_ob": 70,
        "rsi_os": 30,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "bb_period": 20,
        "bb_std": 2.0,
        "stoch_k": 14,
        "stoch_d": 3,
        "atr_period": 14,
    },
}


def _pct(a, b):
    return ((a - b) / b * 100) if b else 0


def run_auto_analysis(df: pd.DataFrame, config: dict) -> dict:
    """Run full automated analysis on OHLCV data with the given timeframe config.

    Returns a structured report dict.
    """
    if df is None or df.empty or len(df) < 20:
        return {"error": "Data tidak cukup (min 20 bar)"}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(0, index=df.index)
    price = close.iloc[-1]

    # ── Calculate indicators ──
    sma_fast = calc_sma(close, config["sma_fast"])
    sma_mid = calc_sma(close, config["sma_mid"])
    sma_slow = calc_sma(close, config["sma_slow"])
    ema_fast = calc_ema(close, config["sma_fast"])
    ema_mid = calc_ema(close, config["sma_mid"])

    rsi = calc_rsi(close, config["rsi_period"])
    macd_line, macd_signal, macd_hist = calc_macd(
        close, config["macd_fast"], config["macd_slow"], config["macd_signal"]
    )
    bb_upper, bb_mid, bb_lower = calc_bollinger_bands(close, config["bb_period"], config["bb_std"])
    stoch_k, stoch_d = calc_stochastic(high, low, close, config["stoch_k"], config["stoch_d"])
    atr = calc_atr(high, low, close, config["atr_period"])

    # Latest values
    vals = {
        "price": price,
        "sma_fast": sma_fast.iloc[-1],
        "sma_mid": sma_mid.iloc[-1],
        "sma_slow": sma_slow.iloc[-1],
        "ema_fast": ema_fast.iloc[-1],
        "ema_mid": ema_mid.iloc[-1],
        "rsi": rsi.iloc[-1],
        "macd_line": macd_line.iloc[-1],
        "macd_signal_line": macd_signal.iloc[-1],
        "macd_hist": macd_hist.iloc[-1],
        "macd_hist_prev": macd_hist.iloc[-2] if len(macd_hist) > 1 else 0,
        "bb_upper": bb_upper.iloc[-1],
        "bb_mid": bb_mid.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "stoch_k": stoch_k.iloc[-1],
        "stoch_d": stoch_d.iloc[-1],
        "atr": atr.iloc[-1],
        "volume_last": volume.iloc[-1],
        "volume_avg": volume.tail(20).mean(),
    }

    # ── Detect signals ──
    signals = []
    bull_points = 0
    bear_points = 0

    # 1. Trend: Price vs SMAs
    if price > vals["sma_fast"]:
        bull_points += 1
        signals.append({"type": "bullish", "name": "Harga di atas SMA-Fast",
                        "detail": f"Harga Rp{price:,.0f} > SMA({config['sma_fast']}) Rp{vals['sma_fast']:,.0f}"})
    else:
        bear_points += 1
        signals.append({"type": "bearish", "name": "Harga di bawah SMA-Fast",
                        "detail": f"Harga Rp{price:,.0f} < SMA({config['sma_fast']}) Rp{vals['sma_fast']:,.0f}"})

    if price > vals["sma_slow"]:
        bull_points += 2
        signals.append({"type": "bullish", "name": "Harga di atas SMA-Slow",
                        "detail": f"Harga > SMA({config['sma_slow']}) – Tren utama positif"})
    else:
        bear_points += 2
        signals.append({"type": "bearish", "name": "Harga di bawah SMA-Slow",
                        "detail": f"Harga < SMA({config['sma_slow']}) – Tren utama negatif"})

    # 2. SMA alignment (all SMAs aligned = strong trend)
    if vals["sma_fast"] > vals["sma_mid"] > vals["sma_slow"]:
        bull_points += 2
        signals.append({"type": "bullish", "name": "SMA Alignment Bullish",
                        "detail": f"SMA-{config['sma_fast']} > SMA-{config['sma_mid']} > SMA-{config['sma_slow']} – Tren naik kuat"})
    elif vals["sma_fast"] < vals["sma_mid"] < vals["sma_slow"]:
        bear_points += 2
        signals.append({"type": "bearish", "name": "SMA Alignment Bearish",
                        "detail": f"SMA-{config['sma_fast']} < SMA-{config['sma_mid']} < SMA-{config['sma_slow']} – Tren turun kuat"})

    # 3. EMA crossover
    ema_fast_prev = ema_fast.iloc[-2] if len(ema_fast) > 1 else ema_fast.iloc[-1]
    ema_mid_prev = ema_mid.iloc[-2] if len(ema_mid) > 1 else ema_mid.iloc[-1]
    if ema_fast_prev <= ema_mid_prev and vals["ema_fast"] > vals["ema_mid"]:
        bull_points += 2
        signals.append({"type": "bullish", "name": "🔥 EMA Golden Cross",
                        "detail": f"EMA-{config['sma_fast']} baru saja menembus ke atas EMA-{config['sma_mid']}"})
    elif ema_fast_prev >= ema_mid_prev and vals["ema_fast"] < vals["ema_mid"]:
        bear_points += 2
        signals.append({"type": "bearish", "name": "💀 EMA Death Cross",
                        "detail": f"EMA-{config['sma_fast']} baru saja menembus ke bawah EMA-{config['sma_mid']}"})

    # 4. RSI
    rsi_val = vals["rsi"]
    if rsi_val > config["rsi_ob"]:
        bear_points += 1
        signals.append({"type": "bearish", "name": "RSI Overbought",
                        "detail": f"RSI({config['rsi_period']}) = {rsi_val:.1f} > {config['rsi_ob']} – Potensi koreksi"})
    elif rsi_val < config["rsi_os"]:
        bull_points += 1
        signals.append({"type": "bullish", "name": "RSI Oversold",
                        "detail": f"RSI({config['rsi_period']}) = {rsi_val:.1f} < {config['rsi_os']} – Potensi rebound"})
    elif 50 < rsi_val <= config["rsi_ob"]:
        bull_points += 0.5
        signals.append({"type": "neutral", "name": "RSI Momentum Positif",
                        "detail": f"RSI({config['rsi_period']}) = {rsi_val:.1f} – Di atas 50, momentum positif"})
    else:
        bear_points += 0.5
        signals.append({"type": "neutral", "name": "RSI Momentum Negatif",
                        "detail": f"RSI({config['rsi_period']}) = {rsi_val:.1f} – Di bawah 50, momentum negatif"})

    # 5. MACD
    if vals["macd_hist"] > 0 and vals["macd_hist_prev"] <= 0:
        bull_points += 2
        signals.append({"type": "bullish", "name": "🔥 MACD Bullish Crossover",
                        "detail": "MACD histogram baru saja berubah positif"})
    elif vals["macd_hist"] < 0 and vals["macd_hist_prev"] >= 0:
        bear_points += 2
        signals.append({"type": "bearish", "name": "💀 MACD Bearish Crossover",
                        "detail": "MACD histogram baru saja berubah negatif"})
    elif vals["macd_hist"] > 0:
        bull_points += 1
        signals.append({"type": "bullish", "name": "MACD Positif",
                        "detail": f"Histogram MACD = {vals['macd_hist']:,.0f} – Momentum bullish"})
    else:
        bear_points += 1
        signals.append({"type": "bearish", "name": "MACD Negatif",
                        "detail": f"Histogram MACD = {vals['macd_hist']:,.0f} – Momentum bearish"})

    # 6. Bollinger Bands position
    bb_pct = (price - vals["bb_lower"]) / (vals["bb_upper"] - vals["bb_lower"]) * 100 \
        if vals["bb_upper"] != vals["bb_lower"] else 50
    if bb_pct > 95:
        bear_points += 1
        signals.append({"type": "bearish", "name": "Harga di Upper Bollinger Band",
                        "detail": f"BB Position {bb_pct:.0f}% – Harga di batas atas, potensi koreksi"})
    elif bb_pct < 5:
        bull_points += 1
        signals.append({"type": "bullish", "name": "Harga di Lower Bollinger Band",
                        "detail": f"BB Position {bb_pct:.0f}% – Harga di batas bawah, potensi rebound"})

    # 7. Stochastic
    if vals["stoch_k"] > 80 and vals["stoch_d"] > 80:
        bear_points += 0.5
        signals.append({"type": "bearish", "name": "Stochastic Overbought",
                        "detail": f"%K={vals['stoch_k']:.0f}, %D={vals['stoch_d']:.0f} – Zona overbought"})
    elif vals["stoch_k"] < 20 and vals["stoch_d"] < 20:
        bull_points += 0.5
        signals.append({"type": "bullish", "name": "Stochastic Oversold",
                        "detail": f"%K={vals['stoch_k']:.0f}, %D={vals['stoch_d']:.0f} – Zona oversold"})

    # 8. Volume analysis
    if vals["volume_avg"] > 0:
        vol_ratio = vals["volume_last"] / vals["volume_avg"]
        if vol_ratio > 2:
            signals.append({"type": "neutral", "name": "🔥 Volume Surge",
                            "detail": f"Volume {vol_ratio:.1f}x di atas rata-rata – Perhatian tinggi"})
        elif vol_ratio < 0.5:
            signals.append({"type": "neutral", "name": "Volume Rendah",
                            "detail": f"Volume hanya {vol_ratio:.1f}x rata-rata – Likuiditas rendah"})

    # ── Overall signal ──
    total = bull_points + bear_points
    if total == 0:
        total = 1
    bull_pct = bull_points / total * 100
    bear_pct = bear_points / total * 100

    if bull_pct > 65:
        overall = "BULLISH"
        confidence = min(95, int(bull_pct))
    elif bear_pct > 65:
        overall = "BEARISH"
        confidence = min(95, int(bear_pct))
    else:
        overall = "NETRAL"
        confidence = int(max(bull_pct, bear_pct))

    # ── Support / Resistance levels ──
    recent_high = high.tail(20).max()
    recent_low = low.tail(20).min()
    atr_val = vals["atr"]

    support_1 = vals["sma_fast"]
    support_2 = vals["sma_slow"]
    support_3 = recent_low
    resistance_1 = recent_high
    resistance_2 = vals["bb_upper"]

    # ── Build report ──
    return {
        "overall_signal": overall,
        "confidence": confidence,
        "bull_points": bull_points,
        "bear_points": bear_points,
        "signals": signals,
        "values": vals,
        "config": config,
        "levels": {
            "support_1": support_1,
            "support_2": support_2,
            "support_3": support_3,
            "resistance_1": resistance_1,
            "resistance_2": resistance_2,
            "atr": atr_val,
            "stop_loss_suggest": price - (1.5 * atr_val),
            "take_profit_suggest": price + (2 * atr_val),
        },
        "indicators_series": {
            "sma_fast": sma_fast, "sma_mid": sma_mid, "sma_slow": sma_slow,
            "ema_fast": ema_fast, "ema_mid": ema_mid,
            "rsi": rsi,
            "macd_line": macd_line, "macd_signal": macd_signal, "macd_hist": macd_hist,
            "bb_upper": bb_upper, "bb_mid": bb_mid, "bb_lower": bb_lower,
            "stoch_k": stoch_k, "stoch_d": stoch_d,
        },
    }
