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
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
<style>
    /* Global Background and Typography */
    
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
    
    /* Sidebar Layout Reordering */
    div[data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stSidebarNav"] {
        order: 2;
    }
    div[data-testid="stSidebarContent"] > div:not([data-testid="stSidebarNav"]) {
        order: 1; /* Pushes our custom header above the nav */
    }

    /* Active State for Sidebar Navigation */
    div[data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, rgba(0, 212, 170, 0.15) 0%, rgba(0, 212, 170, 0.05) 100%) !important;
        border-left: 3px solid #00d4aa !important;
        border-radius: 0 8px 8px 0 !important;
        margin-left: 0 !important;
    }
    div[data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #00d4aa !important;
        font-weight: 700 !important;
    }
    div[data-testid="stSidebarNav"] a {
        border-left: 3px solid transparent;
        border-radius: 0 8px 8px 0 !important;
        transition: all 0.2s;
    }
    div[data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid rgba(0, 212, 170, 0.5) !important;
        transform: translateX(2px);
    }

    /* Section Label and Thin Divider */
    div[data-testid="stSidebarNav"] ul li > div:first-child {
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        color: #64748b !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        padding-bottom: 8px !important;
        margin-top: 24px !important;
        margin-bottom: 8px !important;
    }

    /* Contextual Badges */
    div[data-testid="stSidebarNav"] a[href*="Auto_Analisis"] span:last-child::after {
        content: "AI";
        background: linear-gradient(135deg, #a855f7, #6366f1);
        color: white;
        font-size: 0.6rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 10px;
        margin-left: 8px;
        vertical-align: middle;
        box-shadow: 0 2px 6px rgba(168, 85, 247, 0.4);
    }
    
    div[data-testid="stSidebarNav"] a[href*="Watchlist"] span:last-child::after {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #ff4757;
        border-radius: 50%;
        margin-left: 8px;
        vertical-align: middle;
        box-shadow: 0 0 8px rgba(255, 71, 87, 0.6);
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
    
    /* Skeleton Loading Animation */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    .skeleton-box {
        display: inline-block;
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, rgba(30,41,59,0.5) 25%, rgba(51,65,85,0.8) 50%, rgba(30,41,59,0.5) 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
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
    # Removing st.logo() to use custom header instead


def show_disclosure():
    """Show the disclosure footer."""
    import streamlit as st
    st.markdown(DISCLOSURE)

def stream_text(text: str, delay: float = 0.03):
    """Generator to simulate typing animation."""
    import time
    words = text.split(" ")
    for word in words:
        yield word + " "
        time.sleep(delay)
