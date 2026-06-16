"""📈 Analis Saham Indonesia – Landing Page with quick market snapshot."""

from lib.config import setup_page, show_disclosure, APP_NAME
setup_page("Analis Saham Indonesia")

import streamlit as st
from lib.market_data import get_quote, format_idr, format_pct, color_for_change

# ── Header ──
st.markdown("""
<div style="text-align:center; padding: 20px 0 10px 0;">
    <h1 style="font-size:2.5rem; margin-bottom:0;"><span class="material-symbols-rounded" style="font-size:2.5rem; vertical-align:middle; color:#00d4aa;">trending_up</span> Analis Saham Indonesia</h1>
    <p style="color:#888; font-size:1.1rem; margin-top:8px;">
        Dashboard analisis pasar saham Indonesia – Edukasi & Riset
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Quick Market Snapshot ──
st.subheader(":material/dashboard: Ringkasan Pasar")

col1, col2, col3, col4 = st.columns(4)

with st.spinner("Memuat data pasar..."):
    ihsg = get_quote("^JKSE")
    usd_idr = get_quote("USDIDR=X")
    gold = get_quote("GC=F")
    oil = get_quote("CL=F")

with col1:
    st.metric(
        ":material/location_on: IHSG",
        f"{ihsg['price']:,.0f}",
        f"{ihsg['pctChange']:+.2f}%",
    )

with col2:
    st.metric(
        ":material/currency_exchange: USD/IDR",
        f"Rp{usd_idr['price']:,.0f}",
        f"{usd_idr['pctChange']:+.2f}%",
        delta_color="inverse",
    )

with col3:
    st.metric(
        ":material/workspace_premium: Emas",
        f"${gold['price']:,.1f}",
        f"{gold['pctChange']:+.2f}%",
    )

with col4:
    st.metric(
        ":material/water_drop: Minyak",
        f"${oil['price']:,.1f}",
        f"{oil['pctChange']:+.2f}%",
    )

st.divider()

# ── Quick Navigation ──
st.subheader(":material/explore: Menu Utama")

nav_cols = st.columns(3)
with nav_cols[0]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">vital_signs</span> Market Pulse</h3>
        <p style="color:#888;">Pantau indeks, sektor, saham unggulan, dan berita pasar secara real-time.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_cols[1]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">troubleshoot</span> Analis Saham</h3>
        <p style="color:#888;">Analisis teknikal & fundamental lengkap untuk saham IDX pilihan Anda.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_cols[2]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">donut_small</span> Analisis Indeks</h3>
        <p style="color:#888;">Performa indeks IHSG, konstituen, dan perbandingan sektor.</p>
    </div>
    """, unsafe_allow_html=True)

nav_cols2 = st.columns(3)
with nav_cols2[0]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">travel_explore</span> Makroekonomi</h3>
        <p style="color:#888;">Data makro Indonesia: kurs, inflasi, BI Rate, dan analisis AI.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_cols2[1]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">wallet</span> Portofolio</h3>
        <p style="color:#888;">Kelola dan analisis portofolio investasi saham Anda.</p>
    </div>
    """, unsafe_allow_html=True)

with nav_cols2[2]:
    st.markdown("""
    <div class="metric-card">
        <h3><span class="material-symbols-rounded" style="vertical-align:middle; color:#00d4aa;">article</span> Berita</h3>
        <p style="color:#888;">Berita terkini seputar pasar saham dan ekonomi.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Top Blue Chips Quick View ──
st.divider()
st.subheader(":material/military_tech: Saham Blue Chip")

blue_chips = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK"]
bc_cols = st.columns(len(blue_chips))

with st.spinner("Memuat data saham..."):
    for i, ticker in enumerate(blue_chips):
        q = get_quote(ticker)
        with bc_cols[i]:
            color = color_for_change(q["pctChange"])
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="font-weight:700; margin-bottom:4px;">{ticker.replace('.JK', '')}</p>
                <p style="font-size:1.1rem; margin:4px 0;">Rp{q['price']:,.0f}</p>
                <p style="color:{color}; font-weight:600;">{q['pctChange']:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ──
show_disclosure()
