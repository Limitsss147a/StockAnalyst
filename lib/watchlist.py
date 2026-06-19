import json
import os

WATCHLIST_FILE = "data/watchlist.json"

def load_watchlist():
    """Load watchlist from JSON file."""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_watchlist(watchlist):
    """Save watchlist to JSON file."""
    os.makedirs("data", exist_ok=True)
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=4)

def add_to_watchlist(ticker, target_buy=0, target_sell=0):
    """Add or update a stock in the watchlist."""
    watchlist = load_watchlist()
    for item in watchlist:
        if item["ticker"] == ticker:
            item["target_buy"] = target_buy
            item["target_sell"] = target_sell
            save_watchlist(watchlist)
            return
    watchlist.append({
        "ticker": ticker,
        "target_buy": target_buy,
        "target_sell": target_sell
    })
    save_watchlist(watchlist)

def remove_from_watchlist(ticker):
    """Remove a stock from the watchlist."""
    watchlist = load_watchlist()
    watchlist = [w for w in watchlist if w["ticker"] != ticker]
    save_watchlist(watchlist)
