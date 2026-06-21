import streamlit as st
from lib.config import setup_page

# Set up page globally
setup_page("Analis Saham Indonesia")

# ── Custom Sidebar Header (Logo & IHSG Mini Ticker) ──
from lib.market_data import get_quote
try:
    ihsg = get_quote("^JKSE")
    ihsg_price = ihsg.get("price", 0)
    ihsg_pct = ihsg.get("pctChange", 0)
    color = "#00d4aa" if ihsg_pct >= 0 else "#ff4757"
    icon = "▲" if ihsg_pct >= 0 else "▼"
except Exception:
    ihsg_price, ihsg_pct, color, icon = 0, 0, "#888", "-"

st.sidebar.markdown(f"""
<div class="sidebar-header-custom" style="margin-bottom: 5px;">
    <!-- Logo Brand Identity -->
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
        <div style="background:linear-gradient(135deg, #00d4aa, #00a383);border-radius:10px;width:42px;height:42px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,212,170,0.4);">
            <span style="color:#111827;font-size:24px;font-weight:bold;">📈</span>
        </div>
        <div>
            <h3 style="margin:0;font-size:1.15rem;font-weight:800;color:#f8fafc;letter-spacing:0.5px;">IDX Dashboard</h3>
            <p style="margin:0;font-size:0.75rem;color:#00d4aa;font-weight:600;letter-spacing:0.5px;">StockAnalyst Pro</p>
        </div>
    </div>
    <!-- IHSG Mini Ticker -->
    <div style="background:rgba(15, 23, 42, 0.6);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;display:flex;justify-content:space-between;align-items:center;box-shadow:inset 0 2px 10px rgba(0,0,0,0.2);">
        <span style="color:#94a3b8;font-size:0.8rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;">IHSG</span>
        <div style="text-align:right;">
            <span style="color:#f8fafc;font-size:0.95rem;font-weight:700;margin-right:6px;">{ihsg_price:,.0f}</span>
            <span style="color:{color};font-size:0.8rem;font-weight:700;background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:6px;">{icon} {abs(ihsg_pct):.2f}%</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Define pages using Material symbols instead of emojis
pages = {
    "Utama": [
        st.Page("pages/Beranda.py", title="Beranda", icon=":material/home:"),
        st.Page("pages/Market_Pulse.py", title="Market Pulse", icon=":material/monitoring:"),
    ],
    "Analisis": [
        st.Page("pages/Analisis_Saham.py", title="Analisis Saham", icon=":material/candlestick_chart:"),
        st.Page("pages/Analisis_Indeks.py", title="Analisis Indeks", icon=":material/leaderboard:"),
        st.Page("pages/Auto_Analisis.py", title="Auto Analisis", icon=":material/robot_2:"),
        st.Page("pages/Screener.py", title="Screener", icon=":material/screen_search_desktop:"),
    ],
    "Riset": [
        st.Page("pages/Makroekonomi.py", title="Makroekonomi", icon=":material/public:"),
        st.Page("pages/Berita.py", title="Berita Pasar", icon=":material/newspaper:"),
        st.Page("pages/Kalender_CA.py", title="Kalender CA", icon=":material/event_note:"),
    ],
    "Personal": [
        st.Page("pages/Portofolio.py", title="Portofolio", icon=":material/account_balance_wallet:"),
        st.Page("pages/Watchlist.py", title="Watchlist & Alert", icon=":material/notifications_active:"),
    ]
}

# Run navigation
pg = st.navigation(pages)
pg.run()
