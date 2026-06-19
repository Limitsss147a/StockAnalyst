import streamlit as st
from lib.config import setup_page

# Set up page globally
setup_page("Analis Saham Indonesia")

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
