"""📊 Analisis Indeks – Index analysis (replaces ETF Analyzer for IDX market)."""

from lib.config import setup_page, show_disclosure
setup_page("Analisis Indeks – Analis Saham")

import streamlit as st
import pandas as pd
from lib.market_data import (
    PERIOD_MAP, SECTOR_STOCKS, get_quote, get_history, get_previous_close,
    get_stock_fundamentals, format_idr, format_pct, color_for_change,
)
from lib.charts import render_price_chart, render_gauge, render_sector_heatmap, CHART_VIEWS
from lib.risk import compute_risk_score
from lib.logos import get_logo_html

st.title("📊 Analisis Indeks")
st.caption("Analisis indeks pasar saham Indonesia")

# ── Index Selection ──
IDX_INDICES = {
    "^JKSE": "IHSG (Jakarta Composite Index)",
}

# Top constituents of IHSG (LQ45-like)
LQ45_STOCKS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK",
    "ASII.JK", "UNVR.JK", "HMSP.JK", "ICBP.JK", "KLBF.JK",
    "INDF.JK", "ADRO.JK", "PTBA.JK", "ANTM.JK", "PGAS.JK",
    "SMGR.JK", "TOWR.JK", "EXCL.JK", "BSDE.JK", "GOTO.JK",
]

col_idx, col_period = st.columns([2, 3])
with col_idx:
    idx_ticker = st.selectbox(
        "Pilih Indeks",
        list(IDX_INDICES.keys()),
        format_func=lambda x: IDX_INDICES[x],
    )
with col_period:
    periods = list(PERIOD_MAP.keys())
    selected_period = st.radio("Periode", periods, index=6, horizontal=True, key="idx_period")
    yf_period = PERIOD_MAP[selected_period]

# ── Index Quote ──
with st.spinner("Memuat data indeks..."):
    quote = get_quote(idx_ticker)

if quote.get("price", 0) > 0:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Indeks", f"{quote['price']:,.2f}", f"{quote['pctChange']:+.2f}%")
    with m2:
        st.metric("Nama", IDX_INDICES.get(idx_ticker, idx_ticker))
    with m3:
        st.metric("Volume", f"{quote.get('volume', 0) / 1e6:.1f}M" if quote.get("volume") else "N/A")
    with m4:
        st.metric("Prev Close", f"{quote.get('previousClose', 0):,.2f}")

st.divider()

# ── Chart ──
st.subheader("📈 Grafik Indeks")
view = st.radio("Tampilan", CHART_VIEWS, horizontal=True, key="idx_view")

hist = get_history(idx_ticker, yf_period)
if not hist.empty:
    baseline = get_previous_close(idx_ticker) if selected_period == "1D" else None
    fig = render_price_chart(hist, view=view, title=IDX_INDICES.get(idx_ticker, ""), baseline_price=baseline)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Returns Table ──
st.subheader("📊 Tabel Return")

return_periods = {"YTD": "ytd", "1Y": "1y", "3Y": "3y", "5Y": "5y"}
returns_data = {}
for label, period in return_periods.items():
    h = get_history(idx_ticker, period)
    if not h.empty and len(h["Close"].dropna()) >= 2:
        closes = h["Close"].dropna()
        ret = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0] * 100
        if label in ("3Y", "5Y"):
            years = 3 if label == "3Y" else 5
            ret = ret / years  # annualized approximation
            returns_data[f"{label} (Avg/yr)"] = ret
        else:
            returns_data[label] = ret

if returns_data:
    ret_cols = st.columns(len(returns_data))
    for i, (label, val) in enumerate(returns_data.items()):
        with ret_cols[i]:
            color = color_for_change(val)
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.85rem;">{label}</p>
                <p style="font-size:1.3rem;font-weight:700;color:{color};">{val:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ── Risk Gauge ──
st.subheader("⚠️ Profil Risiko Indeks")

if not hist.empty:
    closes_list = hist["Close"].dropna().tolist()
    risk_score, risk_desc = compute_risk_score(closes_list, beta=1.0)

    col_risk, col_desc = st.columns([1, 1])
    with col_risk:
        fig_risk = render_gauge(risk_score, title="Risk Score", subtitle=risk_desc, height=250)
        st.plotly_chart(fig_risk, use_container_width=True)
    with col_desc:
        st.markdown(f"""
        <div class="gauge-card">
            <h4>Profil Risiko: {risk_desc}</h4>
            <p style="color:#888;">
                Skor risiko dihitung berdasarkan volatilitas historis, 
                maximum drawdown, dan beta terhadap pasar. 
                Skor 0 = sangat konservatif, 100 = sangat agresif.
            </p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Sector Breakdown ──
st.subheader("🏭 Komposisi Sektor")

with st.spinner("Memuat data sektor..."):
    sector_perf = {}
    for ticker, sector_name in SECTOR_STOCKS.items():
        h = get_history(ticker, yf_period)
        if not h.empty and len(h["Close"].dropna()) >= 2:
            closes = h["Close"].dropna()
            base = get_previous_close(ticker) if selected_period == "1D" else closes.iloc[0]
            if base and base > 0:
                ret = (closes.iloc[-1] - base) / base * 100
                sector_perf[sector_name] = ret

if sector_perf:
    fig_sector = render_sector_heatmap(sector_perf, title="Kinerja per Sektor")
    st.plotly_chart(fig_sector, use_container_width=True)

st.divider()

# ── Top Constituents ──
st.subheader("🏆 Konstituen Utama")

with st.spinner("Memuat data konstituen..."):
    const_data = []
    for ticker in LQ45_STOCKS[:20]:
        q = get_quote(ticker)
        if q.get("price", 0) > 0:
            const_data.append(q)

if const_data:
    # Two-column layout
    half = len(const_data) // 2
    col_left, col_right = st.columns(2)

    for i, q in enumerate(const_data):
        target_col = col_left if i < half else col_right
        with target_col:
            logo = get_logo_html(q["ticker"], size=32)
            color = color_for_change(q["pctChange"])
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                {logo}
                <div style="flex:1;">
                    <span style="font-weight:600;">{q['ticker'].replace('.JK','')}</span>
                    <span style="color:#888;font-size:0.8rem;"> {q['name'][:25]}</span>
                </div>
                <div style="text-align:right;">
                    <div>Rp{q['price']:,.0f}</div>
                    <div style="color:{color};font-weight:600;font-size:0.9rem;">{q['pctChange']:+.2f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

show_disclosure()
