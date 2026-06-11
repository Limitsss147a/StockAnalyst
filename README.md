# StockAnalyst

Simple CLI app to analyze Indonesian stock market historical prices (IDX symbols like `BBCA.JK`) from CSV data.

## Requirements
- Python 3.9+

## CSV format
Input CSV must include:
- `date`
- `close`

Example:
```csv
date,close
2026-01-02,9400
2026-01-03,9450
```

## Usage
```bash
python stock_analyst_id.py --symbol BBCA.JK --csv /path/to/prices.csv
```