import pandas as pd
from lib.market_data import get_history
from lib.technicals import get_all_indicators

def check_stock_alerts(ticker: str):
    """
    Check if a stock triggers any alerts (RSI Oversold, MACD Golden Cross, Support).
    Returns a list of alert messages (strings).
    """
    alerts = []
    
    # Get 6 months of data to ensure enough for 200 SMA and MACD
    hist = get_history(ticker, "6mo")
    if hist.empty or len(hist) < 50:
        return alerts
        
    indicators = get_all_indicators(hist)
    
    current_price = hist['Close'].iloc[-1]
    
    # 1. RSI Oversold (RSI < 30)
    if 'rsi' in indicators:
        current_rsi = indicators['rsi'].iloc[-1]
        if current_rsi < 30:
            alerts.append(f"📉 <b>RSI Oversold</b> ({current_rsi:.1f})")
            
    # 2. MACD Golden Cross
    if 'macd_hist' in indicators and len(indicators['macd_hist']) >= 2:
        prev_hist = indicators['macd_hist'].iloc[-2]
        curr_hist = indicators['macd_hist'].iloc[-1]
        # Crosses from negative to positive
        if prev_hist < 0 and curr_hist > 0:
            alerts.append("✨ <b>MACD Golden Cross</b> terdeteksi!")
            
    # 3. Support Krusial (Near SMA-200 or Recent Low)
    if 'sma_200' in indicators:
        sma_200 = indicators['sma_200'].iloc[-1]
        if pd.notna(sma_200):
            # If price is within 2% above SMA 200
            if sma_200 <= current_price <= (sma_200 * 1.02):
                alerts.append(f"🛡️ <b>Mendekati Support Kuat SMA-200</b> (Rp{sma_200:,.0f})")
                
    # 4. Stochastic Oversold
    if 'stoch_k' in indicators and 'stoch_d' in indicators:
        curr_k = indicators['stoch_k'].iloc[-1]
        curr_d = indicators['stoch_d'].iloc[-1]
        if curr_k < 20 and curr_d < 20 and curr_k > curr_d:
            alerts.append("⚡ <b>Stochastic Golden Cross di area Oversold</b>")
            
    return alerts
