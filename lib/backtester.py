import pandas as pd
import numpy as np

def run_simple_backtest(hist: pd.DataFrame, indicators: pd.DataFrame, signal_type: str, forward_days: int = 10):
    """
    Run a simplified backtest on historical data to evaluate a specific signal's accuracy.
    Checks if the price was higher `forward_days` after the signal occurred.
    
    Args:
        hist: Historical price dataframe
        indicators: DataFrame with technical indicators
        signal_type: 'MACD_GOLDEN_CROSS', 'RSI_OVERSOLD', 'SMA_CROSSOVER'
        forward_days: How many days forward to check profitability
    
    Returns:
        dict: Backtest results (total signals, wins, losses, win_rate)
    """
    if hist.empty or indicators.empty or len(hist) < 30:
        return {"total": 0, "wins": 0, "losses": 0, "win_rate": 0.0, "avg_return": 0.0}
        
    signals_idx = []
    
    if signal_type == "MACD_GOLDEN_CROSS" and "macd_hist" in indicators:
        # Find where macd_hist crosses from negative to positive
        macd = indicators["macd_hist"]
        for i in range(1, len(macd)):
            if macd.iloc[i-1] < 0 and macd.iloc[i] > 0:
                signals_idx.append(i)
                
    elif signal_type == "RSI_OVERSOLD" and "rsi" in indicators:
        # Find where RSI drops below 30 then crosses back above
        rsi = indicators["rsi"]
        for i in range(1, len(rsi)):
            if rsi.iloc[i-1] < 30 and rsi.iloc[i] >= 30:
                signals_idx.append(i)
                
    elif signal_type == "SMA_CROSSOVER" and "sma_50" in indicators:
        # Price crossing above SMA-50
        sma = indicators["sma_50"]
        close = hist["Close"]
        for i in range(1, len(close)):
            if close.iloc[i-1] < sma.iloc[i-1] and close.iloc[i] > sma.iloc[i]:
                signals_idx.append(i)
                
    # Evaluate signals
    wins = 0
    losses = 0
    returns = []
    
    for idx in signals_idx:
        # Ensure we have enough forward days
        if idx + forward_days < len(hist):
            entry_price = hist["Close"].iloc[idx]
            exit_price = hist["Close"].iloc[idx + forward_days]
            ret = (exit_price - entry_price) / entry_price * 100
            
            returns.append(ret)
            if ret > 0:
                wins += 1
            else:
                losses += 1
                
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0.0
    avg_return = np.mean(returns) if returns else 0.0
    
    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_return": avg_return
    }
