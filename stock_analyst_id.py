#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List


@dataclass
class PricePoint:
    date: str
    close: float


def read_prices(csv_path: str) -> List[PricePoint]:
    prices: List[PricePoint] = []
    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if "date" not in reader.fieldnames or "close" not in reader.fieldnames:
            raise ValueError("CSV must contain 'date' and 'close' columns.")
        for row in reader:
            prices.append(PricePoint(date=row["date"], close=float(row["close"])))
    if len(prices) < 2:
        raise ValueError("At least 2 rows are required for analysis.")
    return prices


def simple_moving_average(values: Iterable[float], period: int) -> float:
    items = list(values)
    if len(items) < period:
        raise ValueError(f"Need at least {period} values to calculate SMA.")
    return mean(items[-period:])


def daily_returns(values: List[float]) -> List[float]:
    return [(values[i] / values[i - 1]) - 1 for i in range(1, len(values))]


def annualized_volatility(returns: List[float]) -> float:
    if len(returns) < 2:
        return 0.0
    avg = mean(returns)
    variance = sum((r - avg) ** 2 for r in returns) / (len(returns) - 1)
    return math.sqrt(variance) * math.sqrt(252)


def market_signal(last_close: float, sma20: float, sma50: float) -> str:
    if last_close > sma20 > sma50:
        return "Bullish"
    if last_close < sma20 < sma50:
        return "Bearish"
    return "Sideways / Watch"


def analyze_stock(symbol: str, prices: List[PricePoint]) -> str:
    closes = [p.close for p in prices]
    last_close = closes[-1]
    first_close = closes[0]
    total_return = ((last_close / first_close) - 1) * 100
    sma20 = simple_moving_average(closes, 20 if len(closes) >= 20 else len(closes))
    sma50 = simple_moving_average(closes, 50 if len(closes) >= 50 else len(closes))
    vol = annualized_volatility(daily_returns(closes)) * 100
    signal = market_signal(last_close, sma20, sma50)

    return (
        f"Indonesian Stock Analysis ({symbol.upper()})\n"
        f"Latest Close      : {last_close:.2f}\n"
        f"Total Return      : {total_return:.2f}%\n"
        f"SMA 20            : {sma20:.2f}\n"
        f"SMA 50            : {sma50:.2f}\n"
        f"Annual Volatility : {vol:.2f}%\n"
        f"Signal            : {signal}\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze Indonesian stock market data from CSV."
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="IDX stock symbol, e.g. BBCA.JK",
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file with columns: date,close",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    prices = read_prices(args.csv)
    print(analyze_stock(args.symbol, prices))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
