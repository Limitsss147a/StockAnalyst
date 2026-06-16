"""Portfolio management – save/load user holdings to data/portfolio.json."""

import json
import os
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).resolve().parent.parent / "data" / "portfolio.json"


def load_portfolio() -> list:
    """Load portfolio from JSON file. Returns list of holdings."""
    if not PORTFOLIO_PATH.exists():
        return []
    try:
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_portfolio(holdings: list):
    """Save portfolio to JSON file."""
    PORTFOLIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PORTFOLIO_PATH, "w", encoding="utf-8") as f:
        json.dump(holdings, f, indent=2, ensure_ascii=False)


def add_holding(ticker: str, shares: float, avg_price: float):
    """Add or update a holding."""
    holdings = load_portfolio()
    # Check if ticker already exists
    for h in holdings:
        if h["ticker"].upper() == ticker.upper():
            # Update: average down/up
            total_shares = h["shares"] + shares
            total_cost = (h["shares"] * h["avg_price"]) + (shares * avg_price)
            h["shares"] = total_shares
            h["avg_price"] = total_cost / total_shares if total_shares else 0
            save_portfolio(holdings)
            return
    # New holding
    holdings.append({
        "ticker": ticker.upper(),
        "shares": shares,
        "avg_price": avg_price,
    })
    save_portfolio(holdings)


def update_holding(ticker: str, shares: float, avg_price: float):
    """Overwrite an existing holding's shares and avg_price."""
    holdings = load_portfolio()
    for h in holdings:
        if h["ticker"].upper() == ticker.upper():
            h["shares"] = shares
            h["avg_price"] = avg_price
            save_portfolio(holdings)
            return
    # If not found, add it
    add_holding(ticker, shares, avg_price)


def remove_holding(ticker: str):
    """Remove a holding by ticker."""
    holdings = load_portfolio()
    holdings = [h for h in holdings if h["ticker"].upper() != ticker.upper()]
    save_portfolio(holdings)


def calculate_portfolio_metrics(holdings: list, quotes: dict) -> dict:
    """Calculate portfolio metrics given current quotes."""
    total_cost = 0
    total_value = 0
    items = []

    for h in holdings:
        ticker = h["ticker"]
        shares = h["shares"]
        avg_price = h["avg_price"]
        cost = shares * avg_price
        total_cost += cost

        q = quotes.get(ticker, {})
        current_price = q.get("price", 0)
        current_value = shares * current_price
        total_value += current_value

        ret = ((current_price - avg_price) / avg_price * 100) if avg_price else 0
        items.append({
            **h,
            "current_price": current_price,
            "current_value": current_value,
            "cost_basis": cost,
            "return_pct": ret,
            "return_value": current_value - cost,
            "name": q.get("name", ticker),
            "sector": q.get("sector", "N/A"),
            "weight": 0,  # computed below
        })

    # Compute weights
    for item in items:
        item["weight"] = (item["current_value"] / total_value * 100) if total_value else 0

    total_return_pct = ((total_value - total_cost) / total_cost * 100) if total_cost else 0

    return {
        "holdings": items,
        "total_cost": total_cost,
        "total_value": total_value,
        "total_return_pct": total_return_pct,
        "total_return_value": total_value - total_cost,
    }
