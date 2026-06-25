"""Financial statement data fetching and visualization via yfinance."""

import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

_GREEN = "#00d4aa"
_RED = "#ff4757"
_BLUE = "#3b82f6"
_AMBER = "#f59e0b"


@st.cache_data(ttl=600)
def get_income_statement(ticker: str, quarterly: bool = False) -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_income_stmt if quarterly else t.income_stmt
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_balance_sheet(ticker: str, quarterly: bool = False) -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_balance_sheet if quarterly else t.balance_sheet
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_cash_flow(ticker: str, quarterly: bool = False) -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_cashflow if quarterly else t.cashflow
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _fmt(val):
    if pd.isna(val) or val is None:
        return "N/A"
    if abs(val) >= 1e12:
        return f"Rp{val/1e12:,.1f}T"
    if abs(val) >= 1e9:
        return f"Rp{val/1e9:,.1f}M"
    if abs(val) >= 1e6:
        return f"Rp{val/1e6:,.1f}Jt"
    return f"Rp{val:,.0f}"


def _safe_row(df, names):
    for n in names:
        if n in df.index:
            return df.loc[n]
    return None


def render_revenue_profit_chart(income: pd.DataFrame):
    rev = _safe_row(income, ["Total Revenue", "TotalRevenue", "Revenue"])
    ni = _safe_row(income, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
    if rev is None:
        return None
    dates = [d.strftime("%Y-%m") if hasattr(d, "strftime") else str(d) for d in rev.index][::-1]
    rv = list(rev.values)[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=rv, name="Revenue", marker_color=_BLUE, opacity=0.85,
                         text=[_fmt(v) for v in rv], textposition="outside", textfont=dict(size=10)))
    if ni is not None:
        nv = list(ni.values)[::-1]
        fig.add_trace(go.Bar(x=dates, y=nv, name="Net Income",
                             marker_color=[_GREEN if v >= 0 else _RED for v in nv], opacity=0.85,
                             text=[_fmt(v) for v in nv], textposition="outside", textfont=dict(size=10)))
    fig.update_layout(template="plotly_dark", title="Revenue vs Laba Bersih", barmode="group",
                      height=380, margin=dict(l=10, r=10, t=45, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"), font=dict(family="Inter"))
    return fig


def render_margin_trend_chart(income: pd.DataFrame):
    rev = _safe_row(income, ["Total Revenue", "TotalRevenue", "Revenue"])
    if rev is None:
        return None
    dates = [d.strftime("%Y-%m") if hasattr(d, "strftime") else str(d) for d in rev.index][::-1]
    rv = list(rev.values)[::-1]
    fig = go.Figure()
    for name, keys, color in [
        ("Gross", ["Gross Profit", "GrossProfit"], _BLUE),
        ("Operating", ["Operating Income", "OperatingIncome", "EBIT"], _AMBER),
        ("Net", ["Net Income", "NetIncome", "Net Income Common Stockholders"], _GREEN),
    ]:
        row = _safe_row(income, keys)
        if row is not None:
            vals = list(row.values)[::-1]
            margins = [(v / r * 100) if r else 0 for v, r in zip(vals, rv)]
            fig.add_trace(go.Scatter(x=dates, y=margins, name=f"{name} Margin", mode="lines+markers",
                                     line=dict(color=color, width=2)))
    fig.update_layout(template="plotly_dark", title="Tren Margin (%)", height=350,
                      margin=dict(l=10, r=10, t=45, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(title="%", gridcolor="rgba(255,255,255,0.04)"),
                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"), font=dict(family="Inter"))
    return fig


def render_balance_sheet_chart(bs: pd.DataFrame):
    equity = _safe_row(bs, ["Total Equity Gross Minority Interest",
                             "Stockholders Equity", "StockholdersEquity"])
    liab = _safe_row(bs, ["Total Liabilities Net Minority Interest",
                           "TotalLiabilitiesNetMinorityInterest", "Total Liab"])
    if equity is None and liab is None:
        return None
    ref = equity if equity is not None else liab
    dates = [d.strftime("%Y-%m") if hasattr(d, "strftime") else str(d) for d in ref.index][::-1]
    fig = go.Figure()
    if equity is not None:
        fig.add_trace(go.Bar(x=dates, y=list(equity.values)[::-1], name="Ekuitas", marker_color=_GREEN))
    if liab is not None:
        fig.add_trace(go.Bar(x=dates, y=list(liab.values)[::-1], name="Liabilitas", marker_color=_RED, opacity=0.65))
    fig.update_layout(template="plotly_dark", title="Neraca", barmode="group", height=350,
                      margin=dict(l=10, r=10, t=45, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"), font=dict(family="Inter"))
    return fig


def render_cashflow_chart(cf: pd.DataFrame):
    ops = _safe_row(cf, ["Operating Cash Flow", "OperatingCashFlow", "Total Cash From Operating Activities"])
    inv = _safe_row(cf, ["Investing Cash Flow", "InvestingCashFlow", "Total Cashflows From Investing Activities"])
    fin = _safe_row(cf, ["Financing Cash Flow", "FinancingCashFlow", "Total Cash From Financing Activities"])
    if ops is None:
        return None
    dates = [d.strftime("%Y-%m") if hasattr(d, "strftime") else str(d) for d in ops.index][::-1]
    fig = go.Figure()
    for name, row, color in [("Operasional", ops, _GREEN), ("Investasi", inv, _BLUE), ("Pendanaan", fin, _AMBER)]:
        if row is not None:
            fig.add_trace(go.Bar(x=dates, y=list(row.values)[::-1], name=name, marker_color=color, opacity=0.85))
    fig.update_layout(template="plotly_dark", title="Arus Kas", barmode="group", height=350,
                      margin=dict(l=10, r=10, t=45, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"), font=dict(family="Inter"))
    return fig


def format_financial_table(df: pd.DataFrame, max_cols: int = 6) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.iloc[:, :max_cols]
    df.columns = [c.strftime("%Y-%m") if hasattr(c, "strftime") else str(c) for c in df.columns]
    return df.map(lambda x: _fmt(x) if isinstance(x, (int, float)) else x)
