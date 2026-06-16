"""💹 Market Pulse – Indices, sectors, top movers, and headlines."""

from lib.config import setup_page, show_disclosure
setup_page("Market Pulse – Analis Saham")

import streamlit as st
import pandas as pd
from lib.market_data import (
    INDEX_TICKERS, SECTOR_STOCKS, PERIOD_MAP, TOP_IDX_STOCKS,
    get_quote, get_history, get_quotes_bulk, get_previous_close,
    format_idr, format_pct, color_for_change,
)
from lib.charts import render_price_chart, render_sparkline, render_sector_heatmap, CHART_VIEWS
from lib.news import get_market_news
from lib.logos import get_logo_html

st.title(":material/vital_signs: Market Pulse")
st.caption("Pantauan pasar saham Indonesia & global")

# ── Period selector ──
periods = list(PERIOD_MAP.keys())
selected_period = st.radio("Periode", periods, index=6, horizontal=True, key="mp_period")
yf_period = PERIOD_MAP[selected_period]

# ── Index / Asset Cards Grid ──
st.subheader(":material/monitoring: Indeks & Aset Utama")

tickers_list = list(INDEX_TICKERS.keys())

with st.spinner("Memuat data indeks..."):
    quotes = get_quotes_bulk(tickers_list)

# Grid: 5 columns x 2 rows
for row_start in range(0, len(tickers_list), 5):
    cols = st.columns(5)
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx >= len(tickers_list):
            break
        ticker = tickers_list[idx]
        info = INDEX_TICKERS[ticker]
        q = quotes.get(ticker, {})
        color = color_for_change(q.get("pctChange", 0))
        pct = q.get("pctChange", 0)
        price = q.get("price", 0)

        # Sparkline
        hist = get_history(ticker, yf_period)
        sparkline_fig = None
        if not hist.empty:
            closes = hist["Close"].dropna().tolist()
            baseline = get_previous_close(ticker) if selected_period == "1D" and closes else None
            if baseline and closes:
                closes = [baseline] + closes
            sparkline_fig = render_sparkline(closes, base_price=baseline)

        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:12px;">
                <p style="font-size:0.8rem; color:#888; margin:0;">{info['emoji']} {info['name']}</p>
                <p style="font-size:1.1rem; font-weight:700; margin:4px 0;">{price:,.2f}</p>
                <p style="color:{color}; font-weight:600; margin:0;">{pct:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
            if sparkline_fig:
                st.plotly_chart(sparkline_fig, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── Big IHSG Chart ──
st.subheader(":material/location_on: IHSG (Jakarta Composite Index)")
view = st.radio("Tampilan", CHART_VIEWS, horizontal=True, key="ihsg_view")

ihsg_hist = get_history("^JKSE", yf_period)
if not ihsg_hist.empty:
    baseline = get_previous_close("^JKSE") if selected_period == "1D" else None
    fig = render_price_chart(ihsg_hist, view=view, title="IHSG", baseline_price=baseline)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data IHSG tidak tersedia.")

st.divider()

# ── Sector Heatmap ──
st.subheader(":material/factory: Kinerja Sektor")

with st.spinner("Memuat data sektor..."):
    sector_perf = {}
    for ticker, sector_name in SECTOR_STOCKS.items():
        hist = get_history(ticker, yf_period)
        if not hist.empty and len(hist["Close"].dropna()) >= 2:
            closes = hist["Close"].dropna()
            base = get_previous_close(ticker) if selected_period == "1D" else closes.iloc[0]
            if base and base > 0:
                ret = (closes.iloc[-1] - base) / base * 100
                sector_perf[f"{sector_name} ({ticker.replace('.JK', '')})"] = ret

if sector_perf:
    fig_sector = render_sector_heatmap(sector_perf, title=f"Kinerja Sektor ({selected_period})")
    st.plotly_chart(fig_sector, use_container_width=True)

st.divider()

# ── Top Gainers / Losers ──
st.subheader(":material/moving: Top Movers")

with st.spinner("Memuat data saham..."):
    stock_quotes = get_quotes_bulk(TOP_IDX_STOCKS[:30])

valid_quotes = [q for q in stock_quotes.values() if q.get("price", 0) > 0]
sorted_by_change = sorted(valid_quotes, key=lambda x: x.get("pctChange", 0), reverse=True)

col_gain, col_lose, col_active = st.columns(3)

with col_gain:
    st.markdown("**:material/trending_up: Top Gainers**")
    for q in sorted_by_change[:5]:
        ticker = q["ticker"]
        logo = get_logo_html(ticker, size=28)
        color = color_for_change(q["pctChange"])
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            {logo}
            <div style="flex:1;">
                <span style="font-weight:600;">{ticker.replace('.JK','')}</span>
                <span style="color:#888;font-size:0.8rem;"> {q['name'][:20]}</span>
            </div>
            <div style="text-align:right;">
                <div>Rp{q['price']:,.0f}</div>
                <div style="color:{color};font-weight:600;">{q['pctChange']:+.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_lose:
    st.markdown("**:material/trending_down: Top Losers**")
    for q in sorted_by_change[-5:][::-1]:
        ticker = q["ticker"]
        logo = get_logo_html(ticker, size=28)
        color = color_for_change(q["pctChange"])
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            {logo}
            <div style="flex:1;">
                <span style="font-weight:600;">{ticker.replace('.JK','')}</span>
                <span style="color:#888;font-size:0.8rem;"> {q['name'][:20]}</span>
            </div>
            <div style="text-align:right;">
                <div>Rp{q['price']:,.0f}</div>
                <div style="color:{color};font-weight:600;">{q['pctChange']:+.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_active:
    st.markdown("**:material/bolt: Paling Aktif (Volume)**")
    sorted_by_vol = sorted(valid_quotes, key=lambda x: x.get("volume", 0), reverse=True)
    for q in sorted_by_vol[:5]:
        ticker = q["ticker"]
        logo = get_logo_html(ticker, size=28)
        color = color_for_change(q["pctChange"])
        vol_str = f"{q['volume']/1e6:.1f}M" if q['volume'] >= 1e6 else f"{q['volume']:,.0f}"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            {logo}
            <div style="flex:1;">
                <span style="font-weight:600;">{ticker.replace('.JK','')}</span>
                <span style="color:#888;font-size:0.8rem;"> Vol: {vol_str}</span>
            </div>
            <div style="text-align:right;">
                <div>Rp{q['price']:,.0f}</div>
                <div style="color:{color};font-weight:600;">{q['pctChange']:+.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Headlines ──
st.subheader(":material/feed: Berita Terkini")
news = get_market_news(max_items=5)

if news:
    for item in news[:3]:
        st.markdown(f"""
        <div class="news-card">
            <p style="font-weight:600; margin-bottom:4px;">{item['title']}</p>
            <p style="color:#888; font-size:0.8rem; margin:0;">
                {item['publisher']} · {item['time_ago']}
            </p>
            {f'<p style="color:#aaa; font-size:0.85rem; margin-top:6px;">{item["summary"][:150]}...</p>' if item.get('summary') else ''}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Tidak ada berita tersedia saat ini.")

show_disclosure()
