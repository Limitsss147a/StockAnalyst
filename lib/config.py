"""Configuration constants for Analis Saham Indonesia."""

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "📈 Analis Saham"
APP_TITLE = "Analis Saham Indonesia"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

DISCLOSURE = """
---
> ⚠️ **Disclaimer / Penyangkalan**
>
> Dashboard ini hanya untuk tujuan edukasi dan informasi. Bukan merupakan saran keuangan,
> bukan rekomendasi untuk membeli atau menjual sekuritas apapun, dan tidak dipersonalisasi
> untuk situasi Anda. Konsultasikan dengan penasihat keuangan berlisensi sebelum membuat
> keputusan investasi.
>
> *This dashboard is for educational and informational purposes only. It is not financial advice,
> not a recommendation to buy or sell any security, and is not personalized to your situation.
> Consult a licensed advisor before making investment decisions.*
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 16px 20px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .gauge-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #1e2538 100%);
        border: 1px solid rgba(0,212,170,0.15);
        border-radius: 16px;
        padding: 24px;
    }
    
    .chip {
        display: inline-block;
        background: rgba(0,212,170,0.1);
        border: 1px solid rgba(0,212,170,0.2);
        border-radius: 20px;
        padding: 6px 14px;
        margin: 4px;
        font-size: 0.85em;
    }
    
    .green-text { color: #00d4aa; }
    .red-text { color: #ff4757; }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0f1a 0%, #141b2d 100%);
    }
    
    h1 { font-weight: 700; }
    h2, h3 { font-weight: 600; }
    
    .news-card {
        background: #1a1f2e;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }
    
    .sparkline-up { color: #00d4aa; }
    .sparkline-down { color: #ff4757; }
</style>
"""


def setup_page(title="Analis Saham Indonesia", layout="wide"):
    """Configure Streamlit page settings."""
    import streamlit as st
    st.set_page_config(
        page_title=title,
        page_icon="📈",
        layout=layout,
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(f"# {APP_NAME}")
        st.caption("Dashboard Analisis Pasar Saham Indonesia")


def show_disclosure():
    """Show the disclosure footer."""
    import streamlit as st
    st.markdown(DISCLOSURE)
