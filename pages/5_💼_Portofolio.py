"""💼 Portofolio – Portfolio tracker with holdings management."""

from lib.config import setup_page, show_disclosure, GROQ_API_KEY
setup_page("Portofolio – Analis Saham")

import streamlit as st
import plotly.graph_objects as go
from lib.portfolio import load_portfolio, save_portfolio, add_holding, remove_holding, calculate_portfolio_metrics
from lib.market_data import get_quotes_bulk, format_idr, color_for_change
from lib.risk import compute_risk_score, portfolio_risk_score
from lib.charts import render_gauge
from lib.logos import get_logo_html
from lib.groq_analyst import portfolio_analysis
from lib.market_data import get_history

st.title("💼 Portofolio Saya")
st.caption("Kelola dan analisis portofolio investasi saham Anda")

# ── Add Holdings ──
with st.expander("➕ Tambah Saham", expanded=False):
    col_t, col_s, col_p = st.columns(3)
    with col_t:
        new_ticker = st.text_input("Kode Saham", placeholder="BBCA.JK", key="new_ticker")
    with col_s:
        new_shares = st.number_input("Jumlah Lembar", min_value=1, value=100, key="new_shares")
    with col_p:
        new_price = st.number_input("Harga Rata-rata (Rp)", min_value=1, value=8000, key="new_price")

    if st.button("💾 Simpan", key="btn_add"):
        ticker = new_ticker.strip().upper()
        if not ticker.endswith(".JK"):
            ticker += ".JK"
        if ticker and new_shares > 0 and new_price > 0:
            add_holding(ticker, new_shares, new_price)
            st.success(f"✅ {ticker} berhasil ditambahkan!")
            st.rerun()
        else:
            st.error("Mohon isi semua field dengan benar.")

# ── Load Portfolio ──
holdings = load_portfolio()

if not holdings:
    st.info("📂 Portofolio kosong. Tambahkan saham di atas untuk memulai.")
    show_disclosure()
    st.stop()

# Get current quotes
tickers = [h["ticker"] for h in holdings]
with st.spinner("Memuat data harga terkini..."):
    quotes = get_quotes_bulk(tickers)

metrics = calculate_portfolio_metrics(holdings, quotes)

# ── Portfolio Summary ──
st.subheader("📊 Ringkasan Portofolio")

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("Total Nilai", format_idr(metrics["total_value"], compact=False))
with s2:
    st.metric("Total Modal", format_idr(metrics["total_cost"], compact=False))
with s3:
    color = "#00d4aa" if metrics["total_return_pct"] >= 0 else "#ff4757"
    st.metric(
        "Total Return",
        format_idr(metrics["total_return_value"], compact=False),
        f"{metrics['total_return_pct']:+.2f}%",
    )
with s4:
    st.metric("Jumlah Saham", f"{len(holdings)} posisi")

st.divider()

# ── Holdings Table ──
st.subheader("📋 Daftar Holding")

for item in metrics["holdings"]:
    col_logo, col_info, col_val, col_ret, col_del = st.columns([0.5, 2, 1.5, 1.5, 0.5])
    color = color_for_change(item["return_pct"])
    logo = get_logo_html(item["ticker"], size=36)

    with col_logo:
        st.markdown(f'<div style="padding-top:8px;">{logo}</div>', unsafe_allow_html=True)
    with col_info:
        st.markdown(f"""
        **{item['ticker'].replace('.JK','')}** · {item.get('name', '')}  
        {item['shares']:,.0f} lembar @ Rp{item['avg_price']:,.0f}
        """)
    with col_val:
        st.markdown(f"""
        **Nilai:** Rp{item['current_value']:,.0f}  
        **Harga:** Rp{item['current_price']:,.0f}
        """)
    with col_ret:
        st.markdown(f"""
        <span style="color:{color};font-weight:600;font-size:1.1rem;">
            {item['return_pct']:+.2f}%
        </span>  
        <span style="color:{color};">Rp{item['return_value']:,.0f}</span>
        """, unsafe_allow_html=True)
    with col_del:
        if st.button("🗑️", key=f"del_{item['ticker']}"):
            remove_holding(item["ticker"])
            st.rerun()

st.divider()

# ── Allocation Pie ──
st.subheader("📊 Alokasi Portofolio")

col_pie, col_sector = st.columns(2)

with col_pie:
    labels = [h["ticker"].replace(".JK", "") for h in metrics["holdings"]]
    values = [h["current_value"] for h in metrics["holdings"]]

    fig_pie = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.4, textinfo="label+percent",
        marker=dict(line=dict(color="#0e1117", width=2)),
        hovertemplate="%{label}: Rp%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig_pie.update_layout(
        template="plotly_dark", title="Alokasi per Saham",
        height=350, margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_sector:
    # Sector breakdown
    sector_vals = {}
    for h in metrics["holdings"]:
        sector = h.get("sector", "Lainnya")
        if sector == "N/A":
            sector = "Lainnya"
        sector_vals[sector] = sector_vals.get(sector, 0) + h["current_value"]

    if sector_vals:
        fig_sector = go.Figure(go.Pie(
            labels=list(sector_vals.keys()),
            values=list(sector_vals.values()),
            hole=0.4, textinfo="label+percent",
            marker=dict(line=dict(color="#0e1117", width=2)),
        ))
        fig_sector.update_layout(
            template="plotly_dark", title="Alokasi per Sektor",
            height=350, margin=dict(l=10, r=10, t=45, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_sector, use_container_width=True)

st.divider()

# ── Portfolio Risk ──
st.subheader("⚠️ Profil Risiko Portofolio")

risk_data = []
for h in metrics["holdings"]:
    hist = get_history(h["ticker"], "1y")
    if not hist.empty:
        closes = hist["Close"].dropna().tolist()
        score, _ = compute_risk_score(closes)
        risk_data.append({"weight": h["weight"], "risk_score": score})

if risk_data:
    p_risk, p_desc = portfolio_risk_score(risk_data)
    col_rg, col_rd = st.columns([1, 1])
    with col_rg:
        fig_risk = render_gauge(p_risk, title="Portfolio Risk", subtitle=p_desc, height=250)
        st.plotly_chart(fig_risk, use_container_width=True)
    with col_rd:
        st.markdown(f"""
        <div class="gauge-card">
            <h4>{p_desc}</h4>
            <p style="color:#888;">Skor risiko portofolio dihitung berdasarkan rata-rata tertimbang 
            risiko masing-masing saham, dengan penalti untuk konsentrasi berlebihan.</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── AI Portfolio Analysis ──
st.subheader("🤖 Analisis AI Portofolio")

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY belum diset.")
else:
    if st.button("🔍 Generate Analisis Portofolio", key="btn_port_ai"):
        with st.spinner("AI sedang menganalisis portofolio Anda..."):
            result = portfolio_analysis(
                metrics["holdings"],
                metrics["total_value"],
                metrics["total_return_pct"],
            )
        st.markdown(result)

show_disclosure()
