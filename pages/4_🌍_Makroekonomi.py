"""🌍 Makroekonomi – Indonesian macro economic indicators."""

from lib.config import setup_page, show_disclosure, GROQ_API_KEY
setup_page("Makroekonomi – Analis Saham")

import streamlit as st
from lib.macro import (
    INDO_MACRO_DATA, get_exchange_rate_history, get_ihsg_history,
    get_live_macro_snapshot, render_exchange_rate_chart,
)
from lib.charts import render_price_chart
from lib.groq_analyst import macro_pulse

st.title("🌍 Makroekonomi Indonesia")
st.caption("Data dan analisis kondisi makroekonomi Indonesia")

# ── Live Market Indicators ──
st.subheader("📊 Indikator Pasar Live")

with st.spinner("Memuat data pasar..."):
    snapshot = get_live_macro_snapshot()

cols = st.columns(4)
indicators = list(snapshot.items())
for i, (name, data) in enumerate(indicators[:4]):
    with cols[i]:
        price = data.get("price", 0)
        pct = data.get("change_pct", 0)
        # Format based on indicator type
        if "IDR" in name:
            price_str = f"Rp{price:,.0f}"
        elif "IHSG" in name:
            price_str = f"{price:,.2f}"
        else:
            price_str = f"${price:,.2f}"

        color = "#00d4aa" if pct >= 0 else "#ff4757"
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.85rem;margin-bottom:4px;">{name}</p>
            <p style="font-size:1.3rem;font-weight:700;margin:4px 0;">{price_str}</p>
            <p style="color:{color};font-weight:600;margin:0;">{pct:+.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Indonesian Macro Data ──
st.subheader("🏦 Data Makroekonomi Indonesia")
st.caption("Sumber: Bank Indonesia, BPS (data terakhir yang tersedia)")

macro_cols = st.columns(3)
items = list(INDO_MACRO_DATA.items())
for i, (name, data) in enumerate(items):
    with macro_cols[i % 3]:
        st.markdown(f"""
        <div class="metric-card">
            <p style="font-weight:600;margin-bottom:4px;">{name}</p>
            <p style="font-size:1.3rem;font-weight:700;color:#00d4aa;margin:4px 0;">{data['value']}</p>
            <p style="color:#888;font-size:0.8rem;margin:0;">{data['description']}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Exchange Rate Chart ──
st.subheader("💱 Kurs USD/IDR")

period_fx = st.radio("Periode", ["1M", "3M", "6M", "1Y", "3Y", "5Y"], index=3, horizontal=True, key="fx_period")
period_map_fx = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "3Y": "3y", "5Y": "5y"}

fx_hist = get_exchange_rate_history(period_map_fx[period_fx])
if not fx_hist.empty:
    fig_fx = render_exchange_rate_chart(fx_hist)
    if fig_fx:
        st.plotly_chart(fig_fx, use_container_width=True)

st.divider()

# ── IHSG Historical Chart ──
st.subheader("🇮🇩 IHSG Historis")

period_ihsg = st.radio("Periode IHSG", ["1M", "3M", "6M", "1Y", "3Y", "5Y", "Max"], index=3, horizontal=True, key="ihsg_macro_period")
period_map_ihsg = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "3Y": "3y", "5Y": "5y", "Max": "max"}

ihsg_hist = get_ihsg_history(period_map_ihsg[period_ihsg])
if not ihsg_hist.empty:
    fig_ihsg = render_price_chart(ihsg_hist, view="Performance", title="IHSG")
    if fig_ihsg:
        st.plotly_chart(fig_ihsg, use_container_width=True)

st.divider()

# ── AI Macro Pulse ──
st.subheader("🤖 Analisis Makro AI")

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY belum diset. Tambahkan ke file `.env` untuk mengaktifkan analisis AI.")
else:
    if st.button("🔍 Generate Analisis Makro", key="btn_macro"):
        # Compile indicators for AI
        indicators_dict = {}
        for name, data in INDO_MACRO_DATA.items():
            indicators_dict[name] = data["value"]
        for name, data in snapshot.items():
            indicators_dict[name] = f"{data['price']:,.2f} ({data['change_pct']:+.2f}%)"

        with st.spinner("AI sedang menganalisis kondisi makro..."):
            result = macro_pulse(indicators_dict)
        st.markdown(result)

show_disclosure()
