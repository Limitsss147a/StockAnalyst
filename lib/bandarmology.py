"""Bandarmology analysis – tracking big money / institutional flow.

This module provides volume-price analysis to detect institutional
(bandar) accumulation and distribution patterns in IDX stocks.

Key indicators:
- Money Flow Index (MFI) – volume-weighted RSI
- On-Balance Volume (OBV) – cumulative volume direction
- Accumulation/Distribution Line (A/D Line)
- Volume-Price Trend (VPT)
- Big Money Flow estimation using volume threshold
- Smart Money analysis via price-volume divergence
"""

import numpy as np
import pandas as pd
from lib.technicals import calc_sma, calc_ema, calc_obv


# ── Core Bandarmology Indicators ──────────────────────────────────────────────

def calc_money_flow_index(high: pd.Series, low: pd.Series,
                          close: pd.Series, volume: pd.Series,
                          period: int = 14) -> pd.Series:
    """Money Flow Index (MFI) – volume-weighted RSI (0-100)."""
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume

    tp_diff = typical_price.diff()
    pos_flow = raw_money_flow.where(tp_diff > 0, 0)
    neg_flow = raw_money_flow.where(tp_diff < 0, 0)

    pos_sum = pos_flow.rolling(window=period, min_periods=1).sum()
    neg_sum = neg_flow.rolling(window=period, min_periods=1).sum()

    money_ratio = pos_sum / neg_sum.replace(0, np.nan)
    mfi = 100 - (100 / (1 + money_ratio))
    return mfi.fillna(50)


def calc_accumulation_distribution(high: pd.Series, low: pd.Series,
                                    close: pd.Series, volume: pd.Series) -> pd.Series:
    """Accumulation/Distribution Line (A/D Line).

    Measures the cumulative flow of money into/out of a stock.
    Positive = accumulation (buying pressure), Negative = distribution (selling).
    """
    clv_denom = (high - low).replace(0, np.nan)
    clv = ((close - low) - (high - close)) / clv_denom
    clv = clv.fillna(0)
    ad_flow = clv * volume
    return ad_flow.cumsum()


def calc_volume_price_trend(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Volume Price Trend (VPT).

    Combines price change percentage with volume to measure strength of trends.
    """
    pct_change = close.pct_change().fillna(0)
    vpt = (pct_change * volume).cumsum()
    return vpt


def calc_force_index(close: pd.Series, volume: pd.Series,
                     period: int = 13) -> pd.Series:
    """Elder's Force Index – measures the power behind a price move.

    Positive = bulls in control, Negative = bears in control.
    """
    raw_force = close.diff() * volume
    return calc_ema(raw_force.fillna(0), period)


def calc_chaikin_money_flow(high: pd.Series, low: pd.Series,
                            close: pd.Series, volume: pd.Series,
                            period: int = 20) -> pd.Series:
    """Chaikin Money Flow (CMF) – measures buying/selling pressure over period.

    Range: -1 to +1
    > 0 = buying pressure (accumulation)
    < 0 = selling pressure (distribution)
    """
    clv_denom = (high - low).replace(0, np.nan)
    clv = ((close - low) - (high - close)) / clv_denom
    clv = clv.fillna(0)
    ad_volume = clv * volume
    cmf = (ad_volume.rolling(window=period, min_periods=1).sum() /
           volume.rolling(window=period, min_periods=1).sum().replace(0, np.nan))
    return cmf.fillna(0)


# ── Big Money Flow Detection ─────────────────────────────────────────────────

def detect_big_money_flow(df: pd.DataFrame, vol_threshold: float = 1.5,
                          lookback: int = 20) -> dict:
    """Detect big money (bandar) flow patterns.

    Analyzes volume spikes combined with price action to identify
    when institutional money is flowing in or out.

    Parameters
    ----------
    df : DataFrame – OHLCV data
    vol_threshold : float – Volume spike multiplier (vs average)
    lookback : int – Period for average volume calculation

    Returns
    -------
    dict with big money flow analysis results
    """
    close = df["Close"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(0, index=df.index)
    high = df["High"]
    low = df["Low"]
    open_ = df["Open"]

    avg_vol = volume.rolling(window=lookback, min_periods=1).mean()
    vol_ratio = volume / avg_vol.replace(0, 1)

    # Identify big volume days
    big_vol_mask = vol_ratio > vol_threshold

    # Classify big volume days as accumulation or distribution
    # Accumulation: big volume + price close near high (buyers win)
    # Distribution: big volume + price close near low (sellers win)
    candle_range = (high - low).replace(0, np.nan)
    close_position = (close - low) / candle_range  # 0=closed at low, 1=closed at high
    close_position = close_position.fillna(0.5)

    # Price change direction
    price_change = close.diff()

    # Accumulation days: big volume + close in upper half + price up
    accum_mask = big_vol_mask & (close_position > 0.5) & (price_change > 0)
    # Distribution days: big volume + close in lower half + price down
    distrib_mask = big_vol_mask & (close_position < 0.5) & (price_change < 0)

    # Calculate money flow value (volume × price change proxy)
    money_value = volume * close  # simple proxy for money flow value

    # Recent pattern (last N bars)
    recent_n = min(10, len(df))
    recent_accum = accum_mask.tail(recent_n).sum()
    recent_distrib = distrib_mask.tail(recent_n).sum()

    # Net big money flow
    big_buy_value = money_value[accum_mask].tail(lookback).sum()
    big_sell_value = money_value[distrib_mask].tail(lookback).sum()
    net_big_money = big_buy_value - big_sell_value

    # Score accumulation vs distribution (-100 to +100)
    total_big = big_buy_value + big_sell_value
    if total_big > 0:
        bandar_score = ((big_buy_value - big_sell_value) / total_big) * 100
    else:
        bandar_score = 0

    return {
        "big_vol_days_total": int(big_vol_mask.sum()),
        "accumulation_days": int(accum_mask.sum()),
        "distribution_days": int(distrib_mask.sum()),
        "recent_accum": int(recent_accum),
        "recent_distrib": int(recent_distrib),
        "net_big_money": net_big_money,
        "big_buy_value": big_buy_value,
        "big_sell_value": big_sell_value,
        "bandar_score": bandar_score,
        "accum_mask": accum_mask,
        "distrib_mask": distrib_mask,
        "vol_ratio": vol_ratio,
        "close_position": close_position,
    }


def detect_divergences(close: pd.Series, indicator: pd.Series,
                       window: int = 5) -> list:
    """Detect price-indicator divergences (bullish/bearish).

    Bullish divergence: price makes lower low, indicator makes higher low
    Bearish divergence: price makes higher high, indicator makes lower high
    """
    divergences = []

    if len(close) < window * 3:
        return divergences

    # Find local extremes
    for i in range(window * 2, len(close) - 1):
        # Check for local lows (bullish divergence)
        price_low_curr = close.iloc[i - window:i + 1].min()
        price_low_prev = close.iloc[i - window * 2:i - window + 1].min()
        ind_low_curr = indicator.iloc[i - window:i + 1].min()
        ind_low_prev = indicator.iloc[i - window * 2:i - window + 1].min()

        if (price_low_curr < price_low_prev and
                ind_low_curr > ind_low_prev):
            divergences.append({
                "type": "bullish",
                "index": i,
                "date": close.index[i],
                "detail": "Harga membuat lower low tapi indikator higher low"
            })

        # Check for local highs (bearish divergence)
        price_high_curr = close.iloc[i - window:i + 1].max()
        price_high_prev = close.iloc[i - window * 2:i - window + 1].max()
        ind_high_curr = indicator.iloc[i - window:i + 1].max()
        ind_high_prev = indicator.iloc[i - window * 2:i - window + 1].max()

        if (price_high_curr > price_high_prev and
                ind_high_curr < ind_high_prev):
            divergences.append({
                "type": "bearish",
                "index": i,
                "date": close.index[i],
                "detail": "Harga membuat higher high tapi indikator lower high"
            })

    return divergences


# ── Full Bandarmology Report ──────────────────────────────────────────────────

def run_bandarmology_analysis(df: pd.DataFrame, config: dict) -> dict:
    """Run comprehensive bandarmology analysis.

    Parameters
    ----------
    df : DataFrame – OHLCV data
    config : dict – Timeframe config from TIMEFRAMES

    Returns
    -------
    dict – Complete bandarmology report
    """
    if df is None or df.empty or len(df) < 20:
        return {"error": "Data tidak cukup untuk analisis bandarmologi (min 20 bar)"}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(0, index=df.index)
    price = close.iloc[-1]

    # ── Calculate all bandarmology indicators ──
    mfi = calc_money_flow_index(high, low, close, volume, 14)
    obv = calc_obv(close, volume)
    ad_line = calc_accumulation_distribution(high, low, close, volume)
    vpt = calc_volume_price_trend(close, volume)
    force_idx = calc_force_index(close, volume, 13)
    cmf = calc_chaikin_money_flow(high, low, close, volume, 20)

    # OBV with SMA for trend detection
    obv_sma = calc_sma(obv, 20)

    # Big money flow detection
    big_money = detect_big_money_flow(df, vol_threshold=1.5)

    # A/D Line divergence check
    ad_divergences = detect_divergences(close, ad_line, window=5)
    recent_divergences = [d for d in ad_divergences if d["index"] >= len(close) - 10]

    # ── Collect latest values ──
    vals = {
        "price": price,
        "mfi": mfi.iloc[-1],
        "mfi_prev": mfi.iloc[-2] if len(mfi) > 1 else mfi.iloc[-1],
        "obv": obv.iloc[-1],
        "obv_sma": obv_sma.iloc[-1],
        "obv_prev": obv.iloc[-2] if len(obv) > 1 else obv.iloc[-1],
        "ad_line": ad_line.iloc[-1],
        "ad_line_prev": ad_line.iloc[-5] if len(ad_line) > 5 else ad_line.iloc[0],
        "vpt": vpt.iloc[-1],
        "vpt_prev": vpt.iloc[-5] if len(vpt) > 5 else vpt.iloc[0],
        "force_index": force_idx.iloc[-1],
        "cmf": cmf.iloc[-1],
        "volume_last": volume.iloc[-1],
        "volume_avg_20": volume.tail(20).mean(),
        "volume_avg_5": volume.tail(5).mean(),
        "bandar_score": big_money["bandar_score"],
    }

    # ── Generate signals ──
    signals = []
    accum_points = 0
    distrib_points = 0

    # 1. Money Flow Index (MFI)
    mfi_val = vals["mfi"]
    if mfi_val > 80:
        distrib_points += 1.5
        signals.append({
            "type": "distribution",
            "name": "🔴 MFI Overbought",
            "detail": f"MFI = {mfi_val:.1f} > 80 – Tekanan jual meningkat, uang besar mulai keluar",
            "indicator": "MFI"
        })
    elif mfi_val < 20:
        accum_points += 1.5
        signals.append({
            "type": "accumulation",
            "name": "🟢 MFI Oversold",
            "detail": f"MFI = {mfi_val:.1f} < 20 – Potensi akumulasi oleh smart money",
            "indicator": "MFI"
        })
    elif mfi_val > 50:
        accum_points += 0.5
        signals.append({
            "type": "accumulation",
            "name": "MFI Positif",
            "detail": f"MFI = {mfi_val:.1f} – Arus uang masuk lebih besar dari keluar",
            "indicator": "MFI"
        })
    else:
        distrib_points += 0.5
        signals.append({
            "type": "distribution",
            "name": "MFI Negatif",
            "detail": f"MFI = {mfi_val:.1f} – Arus uang keluar lebih besar dari masuk",
            "indicator": "MFI"
        })

    # 2. OBV Trend
    if vals["obv"] > vals["obv_sma"]:
        accum_points += 1
        signals.append({
            "type": "accumulation",
            "name": "🟢 OBV di Atas SMA",
            "detail": "On-Balance Volume di atas rata-rata – Volume pembelian mendominasi",
            "indicator": "OBV"
        })
    else:
        distrib_points += 1
        signals.append({
            "type": "distribution",
            "name": "🔴 OBV di Bawah SMA",
            "detail": "On-Balance Volume di bawah rata-rata – Volume penjualan mendominasi",
            "indicator": "OBV"
        })

    # OBV direction vs Price direction (divergence check)
    price_up = close.iloc[-1] > close.iloc[-5] if len(close) > 5 else True
    obv_up = obv.iloc[-1] > obv.iloc[-5] if len(obv) > 5 else True

    if price_up and not obv_up:
        distrib_points += 2
        signals.append({
            "type": "distribution",
            "name": "⚠️ Divergensi Bearish OBV-Harga",
            "detail": "Harga naik tapi OBV turun – Bandar mungkin sedang DISTRIBUSI (jual diam-diam)",
            "indicator": "OBV"
        })
    elif not price_up and obv_up:
        accum_points += 2
        signals.append({
            "type": "accumulation",
            "name": "💰 Divergensi Bullish OBV-Harga",
            "detail": "Harga turun tapi OBV naik – Bandar mungkin sedang AKUMULASI (beli diam-diam)",
            "indicator": "OBV"
        })

    # 3. Accumulation/Distribution Line trend
    if vals["ad_line"] > vals["ad_line_prev"]:
        accum_points += 1
        signals.append({
            "type": "accumulation",
            "name": "A/D Line Naik",
            "detail": "Accumulation/Distribution Line trennya naik – Tekanan beli kuat",
            "indicator": "A/D"
        })
    else:
        distrib_points += 1
        signals.append({
            "type": "distribution",
            "name": "A/D Line Turun",
            "detail": "Accumulation/Distribution Line trennya turun – Tekanan jual kuat",
            "indicator": "A/D"
        })

    # 4. Chaikin Money Flow
    cmf_val = vals["cmf"]
    if cmf_val > 0.1:
        accum_points += 1.5
        signals.append({
            "type": "accumulation",
            "name": "🟢 CMF Kuat Positif",
            "detail": f"Chaikin MF = {cmf_val:.3f} – Tekanan beli institusional sangat kuat",
            "indicator": "CMF"
        })
    elif cmf_val > 0:
        accum_points += 0.5
        signals.append({
            "type": "accumulation",
            "name": "CMF Positif",
            "detail": f"Chaikin MF = {cmf_val:.3f} – Tekanan beli ringan",
            "indicator": "CMF"
        })
    elif cmf_val < -0.1:
        distrib_points += 1.5
        signals.append({
            "type": "distribution",
            "name": "🔴 CMF Kuat Negatif",
            "detail": f"Chaikin MF = {cmf_val:.3f} – Tekanan jual institusional sangat kuat",
            "indicator": "CMF"
        })
    else:
        distrib_points += 0.5
        signals.append({
            "type": "distribution",
            "name": "CMF Negatif",
            "detail": f"Chaikin MF = {cmf_val:.3f} – Tekanan jual ringan",
            "indicator": "CMF"
        })

    # 5. Force Index
    if vals["force_index"] > 0:
        accum_points += 1
        signals.append({
            "type": "accumulation",
            "name": "Force Index Positif",
            "detail": f"Force Index = {vals['force_index']:,.0f} – Kekuatan beli mendominasi",
            "indicator": "Force"
        })
    else:
        distrib_points += 1
        signals.append({
            "type": "distribution",
            "name": "Force Index Negatif",
            "detail": f"Force Index = {vals['force_index']:,.0f} – Kekuatan jual mendominasi",
            "indicator": "Force"
        })

    # 6. Big Money Flow Pattern
    bandar_score = big_money["bandar_score"]
    if bandar_score > 30:
        accum_points += 2
        signals.append({
            "type": "accumulation",
            "name": "💰 Big Money MASUK",
            "detail": f"Bandar Score = {bandar_score:+.0f} – Uang besar terdeteksi masuk ({big_money['accumulation_days']} hari akumulasi)",
            "indicator": "BigMoney"
        })
    elif bandar_score < -30:
        distrib_points += 2
        signals.append({
            "type": "distribution",
            "name": "🚨 Big Money KELUAR",
            "detail": f"Bandar Score = {bandar_score:+.0f} – Uang besar terdeteksi keluar ({big_money['distribution_days']} hari distribusi)",
            "indicator": "BigMoney"
        })
    else:
        signals.append({
            "type": "neutral",
            "name": "Big Money Netral",
            "detail": f"Bandar Score = {bandar_score:+.0f} – Belum ada pergerakan signifikan uang besar",
            "indicator": "BigMoney"
        })

    # 7. Volume profile analysis
    vol_ratio_5 = vals["volume_avg_5"] / max(vals["volume_avg_20"], 1)
    if vol_ratio_5 > 1.5:
        signals.append({
            "type": "neutral",
            "name": "🔥 Volume Meningkat",
            "detail": f"Volume 5 hari terakhir {vol_ratio_5:.1f}x di atas rata-rata 20 hari – Aktivitas meningkat",
            "indicator": "Volume"
        })
    elif vol_ratio_5 < 0.5:
        signals.append({
            "type": "neutral",
            "name": "💤 Volume Sangat Rendah",
            "detail": f"Volume 5 hari terakhir hanya {vol_ratio_5:.1f}x rata-rata – Sepi, bandar belum bergerak",
            "indicator": "Volume"
        })

    # 8. Recent divergences
    if recent_divergences:
        for div in recent_divergences[-2:]:  # Max 2 recent
            if div["type"] == "bullish":
                accum_points += 1
                signals.append({
                    "type": "accumulation",
                    "name": "💰 Divergensi Bullish A/D",
                    "detail": div["detail"],
                    "indicator": "Divergence"
                })
            else:
                distrib_points += 1
                signals.append({
                    "type": "distribution",
                    "name": "⚠️ Divergensi Bearish A/D",
                    "detail": div["detail"],
                    "indicator": "Divergence"
                })

    # ── Overall assessment ──
    total = accum_points + distrib_points
    if total == 0:
        total = 1
    accum_pct = accum_points / total * 100
    distrib_pct = distrib_points / total * 100

    if accum_pct > 65:
        overall = "AKUMULASI"
        conclusion = "Bandar terindikasi sedang melakukan AKUMULASI (pembelian)"
        confidence = min(95, int(accum_pct))
    elif distrib_pct > 65:
        overall = "DISTRIBUSI"
        conclusion = "Bandar terindikasi sedang melakukan DISTRIBUSI (penjualan)"
        confidence = min(95, int(distrib_pct))
    else:
        overall = "NETRAL"
        conclusion = "Belum ada pola akumulasi/distribusi yang dominan"
        confidence = int(max(accum_pct, distrib_pct))

    return {
        "overall": overall,
        "conclusion": conclusion,
        "confidence": confidence,
        "accum_points": accum_points,
        "distrib_points": distrib_points,
        "signals": signals,
        "values": vals,
        "big_money": big_money,
        "divergences": recent_divergences,
        "indicators_series": {
            "mfi": mfi,
            "obv": obv,
            "obv_sma": obv_sma,
            "ad_line": ad_line,
            "vpt": vpt,
            "force_index": force_idx,
            "cmf": cmf,
            "vol_ratio": big_money["vol_ratio"],
        },
    }
