import yfinance as yf
import pandas as pd
import datetime

def get_corporate_actions(ticker_symbol):
    """Fetch corporate actions: dividends, splits, and estimate next dividend."""
    try:
        t = yf.Ticker(ticker_symbol)
        
        # Dividends
        divs = t.dividends
        if not divs.empty:
            # Ensure timezone-aware
            if hasattr(divs.index, 'tz') and divs.index.tz is None:
                divs.index = divs.index.tz_localize('UTC')
            # Filter last 5 years
            cutoff_date = pd.Timestamp.now(tz="UTC") - pd.DateOffset(years=5)
            try:
                divs = divs[divs.index >= cutoff_date]
            except:
                pass
        
        # Splits
        splits = t.splits
        if not splits.empty:
            if hasattr(splits.index, 'tz') and splits.index.tz is None:
                splits.index = splits.index.tz_localize('UTC')
            cutoff_date = pd.Timestamp.now(tz="UTC") - pd.DateOffset(years=5)
            try:
                splits = splits[splits.index >= cutoff_date]
            except:
                pass
        
        # 3. Calendar & Estimations (Earnings, RUPS, Right Issue)
        calendar = t.calendar
        earnings_date = None
        ex_div_date = None
        if isinstance(calendar, dict):
            if "Earnings Date" in calendar and calendar["Earnings Date"]:
                ed = calendar["Earnings Date"][0]
                earnings_date = ed.strftime("%Y-%m-%d") if hasattr(ed, "strftime") else str(ed)
            if "Ex-Dividend Date" in calendar and calendar["Ex-Dividend Date"]:
                exd = calendar["Ex-Dividend Date"]
                ex_div_date = exd.strftime("%Y-%m-%d") if hasattr(exd, "strftime") else str(exd)
                
        # Estimate RUPS (AGM) - typically 2-4 weeks before Ex-Dividend, or just an estimation
        rups_est = None
        if ex_div_date:
            try:
                exd_obj = datetime.datetime.strptime(ex_div_date, "%Y-%m-%d")
                rups_obj = exd_obj - datetime.timedelta(days=20)
                rups_est = rups_obj.strftime("%Y-%m-%d")
            except:
                pass
        
        # Estimate Next Dividend (simple logic based on last year)
        next_div_est = None
        if not divs.empty and len(divs) > 0:
            last_div_date = divs.index[-1]
            # Look at exactly 1 year ago, or similar frequency
            # Find average days between dividends if multiple
            if len(divs) >= 2:
                # diffs = divs.index.to_series().diff().dt.days.dropna()
                # Simple estimation: add 365 days to last year's same occurrence
                # For Indonesia, many have 1 or 2 per year. 
                # Let's just find the last dividend and predict the next one roughly
                pass
                
            est_date = last_div_date + pd.DateOffset(years=1)
            next_div_est = {
                "estimated_date": est_date.strftime("%Y-%m-%d"),
                "last_amount": float(divs.iloc[-1]),
                "is_passed": est_date < pd.Timestamp.now(tz=est_date.tz)
            }
            
        return {
            "dividends": divs,
            "splits": splits,
            "next_div_est": next_div_est,
            "earnings_date": earnings_date,
            "rups_est": rups_est,
            "right_issue": None # Not available in standard free API
        }
    except Exception as e:
        print(f"Error fetching CA for {ticker_symbol}: {e}")
        return {
            "dividends": pd.Series(), 
            "splits": pd.Series(), 
            "next_div_est": None,
            "earnings_date": None,
            "rups_est": None,
            "right_issue": None
        }

def format_ca_dataframe(series, ca_type="Dividen"):
    """Convert yfinance Series to a nicely formatted DataFrame."""
    if series.empty:
        return pd.DataFrame()
    
    df = series.reset_index()
    # rename columns
    df.columns = ["Tanggal", "Nilai"]
    df["Tipe"] = ca_type
    
    # Format dates
    df["Tanggal"] = df["Tanggal"].dt.strftime("%d %b %Y")
    
    # Sort descending
    df = df.sort_values(by="Tanggal", ascending=False).reset_index(drop=True)
    return df
