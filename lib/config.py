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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Global Background */
    .stApp {
        background: radial-gradient(circle at top right, #111827 0%, #030712 100%);
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }
    
    /* Futuristic Glassmorphism Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Inner glow overlay */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 212, 170, 0.1), 0 0 0 1px rgba(0, 212, 170, 0.2);
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .gauge-card {
        background: linear-gradient(135deg, rgba(20, 27, 45, 0.8) 0%, rgba(10, 15, 30, 0.6) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 212, 170, 0.2);
        border-radius: 20px;
        padding: 24px;
        box-shadow: inset 0 0 20px rgba(0, 212, 170, 0.05);
    }
    
    .chip {
        display: inline-block;
        background: rgba(0, 212, 170, 0.15);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 20px;
        padding: 6px 14px;
        margin: 4px;
        font-size: 0.85em;
        font-weight: 500;
        backdrop-filter: blur(4px);
        box-shadow: 0 2px 8px rgba(0,212,170,0.1);
    }
    
    .green-text { color: #00e6b8; text-shadow: 0 0 10px rgba(0, 230, 184, 0.3); }
    .red-text { color: #ff4757; text-shadow: 0 0 10px rgba(255, 71, 87, 0.3); }
    
    div[data-testid="stSidebar"] {
        background: rgba(10, 15, 26, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    h1, h2, h3 { 
        font-weight: 600; 
        letter-spacing: -0.02em;
    }
    
    /* Styling standard Streamlit metrics */
    [data-testid="stMetricValue"] {
        font-weight: 700;
    }
    
    .news-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        transition: background 0.2s;
    }
    .news-card:hover {
        background: rgba(30, 41, 59, 0.8);
    }
    
    /* Button enhancement */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #00d4aa 0%, #00a383 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(0, 212, 170, 0.3) !important;
        color: white !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.5) !important;
    }
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
