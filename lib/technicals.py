"""Technical indicator calculations for chart overlays."""

import numpy as np
import pandas as pd


def calc_sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=period, min_periods=1).mean()


def calc_ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def calc_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Bollinger Bands → (upper, middle, lower)."""
    middle = calc_sma(series, period)
    std = series.rolling(window=period, min_periods=1).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (0-100)."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD → (macd_line, signal_line, histogram)."""
    ema_fast = calc_ema(series, fast)
    ema_slow = calc_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                     k_period: int = 14, d_period: int = 3):
    """Stochastic Oscillator → (%K, %D)."""
    lowest_low = low.rolling(window=k_period, min_periods=1).min()
    highest_high = high.rolling(window=k_period, min_periods=1).max()
    denom = (highest_high - lowest_low).replace(0, np.nan)
    k = ((close - lowest_low) / denom) * 100
    d = k.rolling(window=d_period, min_periods=1).mean()
    return k.fillna(50), d.fillna(50)


def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series,
             period: int = 14) -> pd.Series:
    """Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean()


def calc_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0)
    return (volume * direction).cumsum()


def get_all_indicators(df: pd.DataFrame) -> dict:
    """Calculate all indicators from an OHLCV dataframe. Returns dict of Series."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(0, index=df.index)

    sma20 = calc_sma(close, 20)
    sma50 = calc_sma(close, 50)
    sma200 = calc_sma(close, 200)
    ema12 = calc_ema(close, 12)
    ema26 = calc_ema(close, 26)
    bb_upper, bb_mid, bb_lower = calc_bollinger_bands(close, 20, 2)
    rsi = calc_rsi(close, 14)
    macd_line, macd_signal, macd_hist = calc_macd(close)
    stoch_k, stoch_d = calc_stochastic(high, low, close)
    atr = calc_atr(high, low, close)
    obv = calc_obv(close, volume)

    return {
        "sma20": sma20, "sma50": sma50, "sma200": sma200,
        "ema12": ema12, "ema26": ema26,
        "bb_upper": bb_upper, "bb_mid": bb_mid, "bb_lower": bb_lower,
        "rsi": rsi,
        "macd_line": macd_line, "macd_signal": macd_signal, "macd_hist": macd_hist,
        "stoch_k": stoch_k, "stoch_d": stoch_d,
        "atr": atr, "obv": obv,
    }


def quick_screen_indicators(closes: list) -> dict:
    """Quick indicator snapshot for screener (from a list of closes)."""
    if len(closes) < 15:
        return {"rsi": 50, "above_sma20": None, "above_sma50": None, "above_sma200": None}

    s = pd.Series(closes)
    rsi = calc_rsi(s, 14).iloc[-1]
    price = closes[-1]
    sma20 = s.rolling(20, min_periods=1).mean().iloc[-1]
    sma50 = s.rolling(50, min_periods=1).mean().iloc[-1] if len(closes) >= 50 else None
    sma200 = s.rolling(200, min_periods=1).mean().iloc[-1] if len(closes) >= 200 else None

    return {
        "rsi": round(rsi, 1),
        "above_sma20": price > sma20 if sma20 else None,
        "above_sma50": price > sma50 if sma50 else None,
        "above_sma200": price > sma200 if sma200 else None,
        "sma20": round(sma20, 0) if sma20 else None,
        "sma50": round(sma50, 0) if sma50 else None,
        "sma200": round(sma200, 0) if sma200 else None,
    }
