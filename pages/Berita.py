"""📰 Berita – News aggregator for Indonesian stocks."""

from lib.config import setup_page, show_disclosure
setup_page("Berita – Analis Saham")

import streamlit as st
from lib.news import get_market_news, get_ticker_news

st.title("📰 Berita Pasar Saham")

tab_market, tab_ticker = st.tabs(["📢 Berita Pasar", "🔍 Berita per Saham"])

with tab_market:
    st.subheader("Berita Pasar Terkini")

    with st.spinner("Memuat berita..."):
        news = get_market_news(max_items=15)

    if news:
        for item in news:
            link = item.get("link", "#")
            st.markdown(f"""
            <div class="news-card">
                <a href="{link}" target="_blank" style="color:#00d4aa;text-decoration:none;font-weight:600;">
                    {item['title']}
                </a>
                <p style="color:#888;font-size:0.8rem;margin:4px 0 0 0;">
                    {item['publisher']} · {item['time_ago']}
                </p>
                {f'<p style="color:#aaa;font-size:0.85rem;margin-top:6px;">{item["summary"][:200]}</p>' if item.get('summary') else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada berita pasar tersedia saat ini.")

with tab_ticker:
    st.subheader("Cari Berita per Saham")

    ticker_input = st.text_input(
        "Kode Saham",
        value="BBCA.JK",
        placeholder="Contoh: BBCA.JK",
        key="news_ticker",
    )

    ticker = ticker_input.strip().upper()
    if not ticker.endswith(".JK") and not ticker.startswith("^"):
        ticker += ".JK"

    if st.button("🔍 Cari Berita", key="btn_search_news"):
        with st.spinner(f"Memuat berita {ticker}..."):
            ticker_news = get_ticker_news(ticker, max_items=15)

        if ticker_news:
            st.success(f"Ditemukan {len(ticker_news)} berita untuk {ticker}")
            for item in ticker_news:
                link = item.get("link", "#")
                st.markdown(f"""
                <div class="news-card">
                    <a href="{link}" target="_blank" style="color:#00d4aa;text-decoration:none;font-weight:600;">
                        {item['title']}
                    </a>
                    <p style="color:#888;font-size:0.8rem;margin:4px 0 0 0;">
                        {item['publisher']} · {item['time_ago']}
                    </p>
                    {f'<p style="color:#aaa;font-size:0.85rem;margin-top:6px;">{item["summary"][:200]}</p>' if item.get('summary') else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"Tidak ada berita ditemukan untuk {ticker}.")

show_disclosure()
