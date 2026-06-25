"""🔍 Analisis Saham – Full stock analyzer with technicals, financials, and AI."""

from lib.config import setup_page, show_disclosure, stream_text
setup_page("Analisis Saham – Analis Saham")

import streamlit as st
from lib.market_data import (
    PERIOD_MAP, TOP_IDX_STOCKS, get_quote, get_history,
    get_stock_fundamentals, get_previous_close,
    format_idr, format_pct, format_number,
)
from lib.charts import render_price_chart, render_gauge, render_technical_chart, CHART_VIEWS, INTERACTIVE_CONFIG
from lib.signals import compute_technical_score, compute_fundamental_score, at_a_glance
from lib.technicals import get_all_indicators
from lib.financials import (
    get_income_statement, get_balance_sheet, get_cash_flow,
    render_revenue_profit_chart, render_margin_trend_chart,
    render_balance_sheet_chart, render_cashflow_chart, format_financial_table,
)
from lib.logos import get_logo_html
from lib.news import get_ticker_news
from lib.groq_analyst import bull_bear_case, deep_analysis

st.title(":material/troubleshoot: Analisis Saham")

# ── Ticker Input ──
col_input, col_period = st.columns([2, 3])
with col_input:
    ticker_input = st.text_input(
        "Kode Saham", value="BBCA.JK", placeholder="Contoh: BBCA.JK, TLKM.JK",
        help="Masukkan kode saham IDX dengan akhiran .JK",
    )

ticker = ticker_input.strip().upper()
if not ticker.endswith(".JK") and not ticker.startswith("^"):
    ticker = ticker + ".JK"

with col_period:
    periods = list(PERIOD_MAP.keys())
    selected_period = st.radio("Periode", periods, index=6, horizontal=True, key="sa_period")
    yf_period = PERIOD_MAP[selected_period]

# ── Load Data ──
with st.spinner(f"Memuat data {ticker}..."):
    quote = get_quote(ticker)
    fundamentals = get_stock_fundamentals(ticker)
    hist = get_history(ticker, yf_period)

if quote.get("price", 0) == 0:
    st.error(f"Tidak dapat memuat data untuk **{ticker}**. Pastikan kode saham benar.")
    show_disclosure()
    st.stop()

# ── Header Row ──
logo_html = get_logo_html(ticker, size=64)
name = fundamentals.get("shortName") or fundamentals.get("longName") or quote["name"]
sector = fundamentals.get("sector", "N/A")
industry = fundamentals.get("industry", "N/A")

st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;margin:16px 0;">
    {logo_html}
    <div>
        <h2 style="margin:0;">{name}</h2>
        <p style="color:#888;margin:4px 0;">{ticker} · {sector} · {industry}</p>
    </div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Harga", f"Rp{quote['price']:,.0f}", f"{quote['pctChange']:+.2f}%")
with m2:
    st.metric("Market Cap", format_idr(quote["marketCap"]))
with m3:
    pe = fundamentals.get("trailingPE")
    st.metric("Trailing P/E", f"{pe:.1f}x" if pe else "N/A")
with m4:
    beta = fundamentals.get("beta")
    st.metric("Beta", f"{beta:.2f}" if beta else "N/A")

st.divider()

# ── Price Chart ──
st.subheader(":material/candlestick_chart: Grafik Harga")
view = st.radio("Tampilan", CHART_VIEWS, horizontal=True, key="sa_view")

if not hist.empty:
    baseline = get_previous_close(ticker) if selected_period == "1D" else None
    fig = render_price_chart(hist, view=view, title=f"{ticker}", baseline_price=baseline)
    if fig:
        st.plotly_chart(fig, use_container_width=True, config=INTERACTIVE_CONFIG)
else:
    st.warning("Data historis tidak tersedia.")

st.divider()

# ══════════════════════════════════════════════════════════════
# ── NEW: Technical Indicators Chart ──
# ══════════════════════════════════════════════════════════════
st.subheader(":material/stacked_line_chart: Indikator Teknikal")

if not hist.empty and len(hist) >= 15:
    # Indicator toggles
    tc1, tc2, tc3, tc4 = st.columns(4)
    with tc1:
        show_sma = st.checkbox("SMA (20/50/200)", value=True, key="cb_sma")
    with tc2:
        show_bb = st.checkbox("Bollinger Bands", value=True, key="cb_bb")
    with tc3:
        show_macd = st.checkbox("MACD", value=True, key="cb_macd")
    with tc4:
        show_rsi = st.checkbox("RSI", value=True, key="cb_rsi")

    # Calculate indicators
    indicators = get_all_indicators(hist)

    fig_tech_chart = render_technical_chart(
        hist, indicators,
        show_sma=show_sma, show_bb=show_bb,
        show_macd=show_macd, show_rsi=show_rsi,
        title=f"Indikator Teknikal – {ticker}",
    )
    if fig_tech_chart:
        st.plotly_chart(fig_tech_chart, use_container_width=True, config=INTERACTIVE_CONFIG)

    # Quick indicator values
    rsi_val = indicators["rsi"].iloc[-1] if "rsi" in indicators else None
    macd_val = indicators["macd_hist"].iloc[-1] if "macd_hist" in indicators else None

    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        if rsi_val is not None:
            rsi_color = "#ff4757" if rsi_val > 70 else ("#00d4aa" if rsi_val < 30 else "#888")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.85rem;">RSI (14)</p>
                <p style="font-size:1.4rem;font-weight:700;color:{rsi_color};">{rsi_val:.1f}</p>
                <p style="color:#888;font-size:0.75rem;">{'Overbought' if rsi_val > 70 else ('Oversold' if rsi_val < 30 else 'Netral')}</p>
            </div>""", unsafe_allow_html=True)
    with ic2:
        if macd_val is not None:
            m_color = "#00d4aa" if macd_val >= 0 else "#ff4757"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.85rem;">MACD Histogram</p>
                <p style="font-size:1.4rem;font-weight:700;color:{m_color};">{macd_val:,.0f}</p>
                <p style="color:#888;font-size:0.75rem;">{'Bullish' if macd_val >= 0 else 'Bearish'}</p>
            </div>""", unsafe_allow_html=True)
    with ic3:
        sma20 = indicators["sma20"].iloc[-1] if "sma20" in indicators else None
        if sma20:
            above = quote["price"] > sma20
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.85rem;">vs SMA-20</p>
                <p style="font-size:1.4rem;font-weight:700;color:{'#00d4aa' if above else '#ff4757'};">
                    {'↑ Di atas' if above else '↓ Di bawah'}</p>
                <p style="color:#888;font-size:0.75rem;">Rp{sma20:,.0f}</p>
            </div>""", unsafe_allow_html=True)
    with ic4:
        sma200 = indicators["sma200"].iloc[-1] if "sma200" in indicators else None
        if sma200 and len(hist) >= 200:
            above = quote["price"] > sma200
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.85rem;">vs SMA-200</p>
                <p style="font-size:1.4rem;font-weight:700;color:{'#00d4aa' if above else '#ff4757'};">
                    {'↑ Di atas' if above else '↓ Di bawah'}</p>
                <p style="color:#888;font-size:0.75rem;">Rp{sma200:,.0f}</p>
            </div>""", unsafe_allow_html=True)
else:
    st.info("Data tidak cukup untuk menampilkan indikator teknikal (min. 15 bar).")

st.divider()

# ── Snapshot Section ──
st.subheader(":material/summarize: Snapshot")

closes = hist["Close"].dropna().tolist() if not hist.empty else []
tech_score, tech_drivers = compute_technical_score(
    closes,
    high_52w=fundamentals.get("fiftyTwoWeekHigh"),
    low_52w=fundamentals.get("fiftyTwoWeekLow"),
    sma50=fundamentals.get("fiftyDayAverage"),
    sma200=fundamentals.get("twoHundredDayAverage"),
)
fund_score, fund_drivers = compute_fundamental_score(fundamentals)
chips = at_a_glance(quote["price"], fundamentals, closes)

st.caption(
    f"Analisis snapshot untuk {name} ({ticker}) berdasarkan data terkini. "
    "Skor bersifat edukatif, bukan rekomendasi investasi."
)

col_glance, col_tech, col_fund = st.columns([1.2, 1, 1])

with col_glance:
    html_content = '<div class="gauge-card" style="height:100%; display:flex; flex-direction:column; gap:12px;">'
    html_content += '<div style="font-weight:600;">📌 Sekilas (At a Glance)</div>'
    for chip in chips:
        html_content += f'<div><span class="chip" style="border-color:{chip["color"]};"><b>{chip["label"]}:</b> {chip["value"]}</span></div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

with col_tech:
    fig_tech = render_gauge(tech_score, title="Technical Strength",
                            subtitle="Tren, momentum, posisi vs rata-rata", height=220)
    st.plotly_chart(fig_tech, use_container_width=True)
    with st.expander("Detail Teknikal"):
        for d in tech_drivers:
            st.markdown(f"• {d}")

with col_fund:
    fig_fund = render_gauge(fund_score, title="Fundamental Quality",
                            subtitle="Margin, return, leverage, pertumbuhan", height=220)
    st.plotly_chart(fig_fund, use_container_width=True)
    with st.expander("Detail Fundamental"):
        for d in fund_drivers:
            st.markdown(f"• {d}")

st.divider()

# ══════════════════════════════════════════════════════════════
# ── NEW: Laporan Keuangan Multi-Periode ──
# ══════════════════════════════════════════════════════════════
st.subheader(":material/receipt_long: Laporan Keuangan")

fin_period = st.radio("Periode Laporan", ["Tahunan", "Kuartalan"], horizontal=True, key="fin_period")
is_quarterly = fin_period == "Kuartalan"

with st.spinner("Memuat laporan keuangan..."):
    income = get_income_statement(ticker, quarterly=is_quarterly)
    balance = get_balance_sheet(ticker, quarterly=is_quarterly)
    cashflow = get_cash_flow(ticker, quarterly=is_quarterly)

fin_tab1, fin_tab2, fin_tab3, fin_tab4 = st.tabs([
    ":material/bar_chart: Revenue & Laba", ":material/show_chart: Tren Margin", ":material/account_balance: Neraca", ":material/payments: Arus Kas"
])

with fin_tab1:
    if not income.empty:
        fig_rev = render_revenue_profit_chart(income)
        if fig_rev:
            st.plotly_chart(fig_rev, use_container_width=True)
        with st.expander(":material/table: Data Lengkap – Laba Rugi"):
            st.dataframe(format_financial_table(income), use_container_width=True)
    else:
        st.info("Data laba rugi tidak tersedia.")

with fin_tab2:
    if not income.empty:
        fig_margin = render_margin_trend_chart(income)
        if fig_margin:
            st.plotly_chart(fig_margin, use_container_width=True)
    else:
        st.info("Data margin tidak tersedia.")

with fin_tab3:
    if not balance.empty:
        fig_bs = render_balance_sheet_chart(balance)
        if fig_bs:
            st.plotly_chart(fig_bs, use_container_width=True)
        with st.expander(":material/table: Data Lengkap – Neraca"):
            st.dataframe(format_financial_table(balance), use_container_width=True)
    else:
        st.info("Data neraca tidak tersedia.")

with fin_tab4:
    if not cashflow.empty:
        fig_cf = render_cashflow_chart(cashflow)
        if fig_cf:
            st.plotly_chart(fig_cf, use_container_width=True)
        with st.expander(":material/table: Data Lengkap – Arus Kas"):
            st.dataframe(format_financial_table(cashflow), use_container_width=True)
    else:
        st.info("Data arus kas tidak tersedia.")

st.divider()

# ── Key Statistics ──
st.subheader(":material/query_stats: Statistik Kunci")

stat_cols = st.columns(3)

with stat_cols[0]:
    st.markdown("**Valuasi**")
    for k, v in {
        "Trailing P/E": format_number(fundamentals.get("trailingPE"), "x"),
        "Forward P/E": format_number(fundamentals.get("forwardPE"), "x"),
        "P/B Ratio": format_number(fundamentals.get("priceToBook"), "x"),
        "EV": format_idr(fundamentals.get("enterpriseValue")),
        "Dividend Yield": format_number((fundamentals.get("dividendYield") or 0) * 100, "%")
            if fundamentals.get("dividendYield") else "N/A",
    }.items():
        st.markdown(f"**{k}:** {v}")

    st.markdown("**Perdagangan**")
    for k, v in {
        "52W High": f"Rp{fundamentals.get('fiftyTwoWeekHigh', 0):,.0f}",
        "52W Low": f"Rp{fundamentals.get('fiftyTwoWeekLow', 0):,.0f}",
        "SMA-50": f"Rp{fundamentals.get('fiftyDayAverage', 0):,.0f}",
        "SMA-200": f"Rp{fundamentals.get('twoHundredDayAverage', 0):,.0f}",
        "Avg Volume": format_number(fundamentals.get("averageVolume"), decimals=0),
    }.items():
        st.markdown(f"**{k}:** {v}")

with stat_cols[1]:
    st.markdown("**Profitabilitas**")
    for k, v in {
        "Gross Margin": format_number((fundamentals.get("grossMargins") or 0) * 100, "%")
            if fundamentals.get("grossMargins") else "N/A",
        "Operating Margin": format_number((fundamentals.get("operatingMargins") or 0) * 100, "%")
            if fundamentals.get("operatingMargins") else "N/A",
        "Net Margin": format_number((fundamentals.get("profitMargins") or 0) * 100, "%")
            if fundamentals.get("profitMargins") else "N/A",
        "ROE": format_number((fundamentals.get("returnOnEquity") or 0) * 100, "%")
            if fundamentals.get("returnOnEquity") else "N/A",
        "ROA": format_number((fundamentals.get("returnOnAssets") or 0) * 100, "%")
            if fundamentals.get("returnOnAssets") else "N/A",
    }.items():
        st.markdown(f"**{k}:** {v}")

with stat_cols[2]:
    st.markdown("**Neraca & Pendapatan**")
    for k, v in {
        "D/E Ratio": format_number(fundamentals.get("debtToEquity"), "%"),
        "Current Ratio": format_number(fundamentals.get("currentRatio"), "x"),
        "Total Revenue": format_idr(fundamentals.get("totalRevenue")),
        "Total Debt": format_idr(fundamentals.get("totalDebt")),
        "Total Cash": format_idr(fundamentals.get("totalCash")),
        "Free Cash Flow": format_idr(fundamentals.get("freeCashflow")),
        "Revenue Growth": format_number((fundamentals.get("revenueGrowth") or 0) * 100, "%")
            if fundamentals.get("revenueGrowth") else "N/A",
        "Earnings Growth": format_number((fundamentals.get("earningsGrowth") or 0) * 100, "%")
            if fundamentals.get("earningsGrowth") else "N/A",
    }.items():
        st.markdown(f"**{k}:** {v}")

summary = fundamentals.get("longBusinessSummary")
if summary:
    with st.expander(":material/description: Deskripsi Bisnis"):
        st.write(summary)

st.divider()

# ── AI Analysis Tabs ──
st.subheader(":material/smart_toy: Analisis AI (Groq)")

tab_bull, tab_deep, tab_news = st.tabs([":material/compare_arrows: Bull/Bear Case", ":material/manage_search: Analisis Mendalam", ":material/article: Berita Terkini"])

with tab_bull:
    if st.button("Generate Bull/Bear Case", key="btn_bull"):
        with st.spinner("AI sedang menganalisis..."):
            result = bull_bear_case(ticker, name, fundamentals, quote)
            st.session_state["sa_bull_result"] = result
            st.session_state["sa_bull_new"] = True
            
    if "sa_bull_result" in st.session_state:
        if st.session_state.get("sa_bull_new"):
            st.write_stream(stream_text(st.session_state["sa_bull_result"]))
            st.session_state["sa_bull_new"] = False
        else:
            st.markdown(st.session_state["sa_bull_result"])

with tab_deep:
    if st.button("Generate Analisis Mendalam", key="btn_deep"):
        with st.spinner("AI sedang menganalisis secara mendalam..."):
            result = deep_analysis(ticker, name, fundamentals, quote)
            st.session_state["sa_deep_result"] = result
            st.session_state["sa_deep_new"] = True
            
    if "sa_deep_result" in st.session_state:
        if st.session_state.get("sa_deep_new"):
            st.write_stream(stream_text(st.session_state["sa_deep_result"]))
            st.session_state["sa_deep_new"] = False
        else:
            st.markdown(st.session_state["sa_deep_result"])

with tab_news:
    news = get_ticker_news(ticker, max_items=10)
    if news:
        for item in news:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank" style="color:#00d4aa;text-decoration:none;">
                    <b>{item['title']}</b>
                </a>
                <p style="color:#888;font-size:0.8rem;margin:4px 0 0 0;">
                    {item['publisher']} · {item['time_ago']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada berita terkini untuk saham ini.")

show_disclosure()
