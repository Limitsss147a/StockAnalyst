"""Historical backtesting engine for technical signal validation."""

import pandas as pd
import numpy as np
from lib.technicals import calc_sma, calc_rsi, calc_macd, calc_stochastic, calc_atr


SIGNAL_TYPES = {
    "MACD_GOLDEN_CROSS": "MACD Golden Cross",
    "MACD_DEATH_CROSS": "MACD Death Cross",
    "RSI_OVERSOLD": "RSI Oversold Bounce",
    "RSI_OVERBOUGHT": "RSI Overbought Reversal",
    "SMA_CROSSOVER": "Price Crosses Above SMA-50",
    "SMA_CROSSUNDER": "Price Crosses Below SMA-50",
    "GOLDEN_CROSS_SMA": "SMA-50 Crosses Above SMA-200",
    "STOCH_OVERSOLD": "Stochastic Oversold Bounce",
    "BB_LOWER_TOUCH": "Bollinger Band Lower Touch",
}


def run_backtest(hist: pd.DataFrame, signal_type: str, forward_days: int = 10):
    """
    Run a backtest on historical OHLCV data to evaluate a signal's accuracy.
    
    Uses raw hist data directly and computes its own indicators internally,
    so there's no dependency on external indicator format.
    
    Args:
        hist: Historical OHLCV dataframe (must have Close, High, Low columns)
        signal_type: One of the SIGNAL_TYPES keys
        forward_days: How many days forward to check profitability
    
    Returns:
        dict with total, wins, losses, win_rate, avg_return, max_return, 
        max_drawdown, and trades list
    """
    empty_result = {
        "total": 0, "wins": 0, "losses": 0, "win_rate": 0.0,
        "avg_return": 0.0, "max_return": 0.0, "max_drawdown": 0.0,
        "trades": [], "signal_name": SIGNAL_TYPES.get(signal_type, signal_type)
    }
    
    if hist is None or hist.empty or len(hist) < 50:
        return empty_result

    close = hist["Close"]
    high = hist["High"]
    low = hist["Low"]
    
    # Compute indicators internally
    sma_50 = calc_sma(close, 50)
    sma_200 = calc_sma(close, 200)
    rsi = calc_rsi(close, 14)
    macd_line, macd_signal, macd_hist = calc_macd(close)
    stoch_k, stoch_d = calc_stochastic(high, low, close)
    
    # Bollinger Bands
    bb_mid = calc_sma(close, 20)
    bb_std = close.rolling(20, min_periods=1).std()
    bb_lower = bb_mid - 2 * bb_std

    # Find signal indices
    signals_idx = []
    
    if signal_type == "MACD_GOLDEN_CROSS":
        for i in range(1, len(macd_hist)):
            if pd.notna(macd_hist.iloc[i-1]) and pd.notna(macd_hist.iloc[i]):
                if macd_hist.iloc[i-1] < 0 and macd_hist.iloc[i] >= 0:
                    signals_idx.append(i)
                    
    elif signal_type == "MACD_DEATH_CROSS":
        for i in range(1, len(macd_hist)):
            if pd.notna(macd_hist.iloc[i-1]) and pd.notna(macd_hist.iloc[i]):
                if macd_hist.iloc[i-1] >= 0 and macd_hist.iloc[i] < 0:
                    signals_idx.append(i)
                    
    elif signal_type == "RSI_OVERSOLD":
        for i in range(1, len(rsi)):
            if pd.notna(rsi.iloc[i-1]) and pd.notna(rsi.iloc[i]):
                if rsi.iloc[i-1] < 30 and rsi.iloc[i] >= 30:
                    signals_idx.append(i)
                    
    elif signal_type == "RSI_OVERBOUGHT":
        for i in range(1, len(rsi)):
            if pd.notna(rsi.iloc[i-1]) and pd.notna(rsi.iloc[i]):
                if rsi.iloc[i-1] > 70 and rsi.iloc[i] <= 70:
                    signals_idx.append(i)
                    
    elif signal_type == "SMA_CROSSOVER":
        for i in range(1, len(close)):
            if pd.notna(sma_50.iloc[i-1]) and pd.notna(sma_50.iloc[i]):
                if close.iloc[i-1] < sma_50.iloc[i-1] and close.iloc[i] >= sma_50.iloc[i]:
                    signals_idx.append(i)
                    
    elif signal_type == "SMA_CROSSUNDER":
        for i in range(1, len(close)):
            if pd.notna(sma_50.iloc[i-1]) and pd.notna(sma_50.iloc[i]):
                if close.iloc[i-1] >= sma_50.iloc[i-1] and close.iloc[i] < sma_50.iloc[i]:
                    signals_idx.append(i)

    elif signal_type == "GOLDEN_CROSS_SMA":
        for i in range(1, len(sma_50)):
            if pd.notna(sma_50.iloc[i-1]) and pd.notna(sma_200.iloc[i-1]):
                if pd.notna(sma_50.iloc[i]) and pd.notna(sma_200.iloc[i]):
                    if sma_50.iloc[i-1] < sma_200.iloc[i-1] and sma_50.iloc[i] >= sma_200.iloc[i]:
                        signals_idx.append(i)
                    
    elif signal_type == "STOCH_OVERSOLD":
        for i in range(1, len(stoch_k)):
            if pd.notna(stoch_k.iloc[i-1]) and pd.notna(stoch_k.iloc[i]):
                if stoch_k.iloc[i-1] < 20 and stoch_k.iloc[i] >= 20:
                    if stoch_k.iloc[i] > stoch_d.iloc[i]:
                        signals_idx.append(i)
                        
    elif signal_type == "BB_LOWER_TOUCH":
        for i in range(len(close)):
            if pd.notna(bb_lower.iloc[i]):
                if low.iloc[i] <= bb_lower.iloc[i] and close.iloc[i] > bb_lower.iloc[i]:
                    signals_idx.append(i)

    # Evaluate signals — skip signals that are too close together (min 3-day gap)
    wins = 0
    losses = 0
    returns = []
    trades = []
    last_signal_idx = -5
    
    for idx in signals_idx:
        if idx - last_signal_idx < 3:
            continue  # Skip clustered signals
        if idx + forward_days >= len(hist):
            continue  # Not enough forward data
            
        entry_price = close.iloc[idx]
        exit_price = close.iloc[idx + forward_days]
        
        # Also track maximum drawdown during the holding period
        hold_slice = close.iloc[idx:idx + forward_days + 1]
        min_price = hold_slice.min()
        max_dd = (min_price - entry_price) / entry_price * 100
        
        ret = (exit_price - entry_price) / entry_price * 100
        returns.append(ret)
        
        # For short signals (DEATH_CROSS, RSI_OVERBOUGHT, SMA_CROSSUNDER), invert the logic
        is_short_signal = signal_type in ("MACD_DEATH_CROSS", "RSI_OVERBOUGHT", "SMA_CROSSUNDER")
        actual_ret = -ret if is_short_signal else ret
        
        if actual_ret > 0:
            wins += 1
        else:
            losses += 1
            
        trade_date = hist.index[idx]
        date_str = trade_date.strftime("%Y-%m-%d") if hasattr(trade_date, "strftime") else str(trade_date)
        
        trades.append({
            "date": date_str,
            "entry": round(entry_price, 0),
            "exit": round(exit_price, 0),
            "return_pct": round(ret, 2),
            "max_dd_pct": round(max_dd, 2),
            "result": "Win" if actual_ret > 0 else "Loss"
        })
        
        last_signal_idx = idx
                
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0.0
    avg_return = float(np.mean(returns)) if returns else 0.0
    max_return = float(max(returns)) if returns else 0.0
    max_drawdown = float(min([t["max_dd_pct"] for t in trades])) if trades else 0.0
    
    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "max_return": max_return,
        "max_drawdown": max_drawdown,
        "trades": trades,
        "signal_name": SIGNAL_TYPES.get(signal_type, signal_type)
    }
