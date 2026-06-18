"""🤖 Auto Analisis – Automated technical analysis by timeframe."""

from lib.config import setup_page, show_disclosure, GROQ_API_KEY, stream_text
setup_page("Auto Analisis – Analis Saham")

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lib.market_data import get_quote, get_history, get_stock_fundamentals, format_idr
from lib.auto_analysis import TIMEFRAMES, run_auto_analysis
from lib.groq_analyst import timeframe_analysis
from lib.logos import get_logo_html
from lib.charts import _GREEN, _RED, INTERACTIVE_CONFIG

st.title(":material/robot_2: Auto Analisis Teknikal")
st.caption("Analisis teknikal otomatis dengan indikator yang disesuaikan per timeframe")

# ── Input ──
col_ticker, col_tf = st.columns([1, 2])
with col_ticker:
    ticker_input = st.text_input("Kode Saham", value="BBCA.JK", placeholder="BBCA.JK",
                                 help="Kode saham IDX dengan akhiran .JK")

with col_tf:
    tf_options = list(TIMEFRAMES.keys())
    selected_tf = st.radio("Timeframe", tf_options, horizontal=True, key="aa_tf",
                           captions=[TIMEFRAMES[t]["description"] for t in tf_options])

ticker = ticker_input.strip().upper()
if not ticker.endswith(".JK") and not ticker.startswith("^"):
    ticker += ".JK"

config = TIMEFRAMES[selected_tf]

# Timeframe info card
st.markdown(f"""
<div class="metric-card" style="border-left:4px solid #00d4aa;">
    <b>{config['label']}</b> – {config['description']}<br>
    <span style="color:#888;font-size:0.85rem;">
        SMA: {config['sma_fast']}/{config['sma_mid']}/{config['sma_slow']} · 
        RSI({config['rsi_period']}) OB/OS: {config['rsi_ob']}/{config['rsi_os']} · 
        MACD({config['macd_fast']},{config['macd_slow']},{config['macd_signal']}) · 
        BB({config['bb_period']},{config['bb_std']})
    </span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Run Analysis ──
if st.button(":material/rocket_launch: Jalankan Analisis", type="primary", use_container_width=True):
    st.session_state["run_aa_ticker"] = ticker
    st.session_state["run_aa_tf"] = selected_tf

if st.session_state.get("run_aa_ticker") == ticker and st.session_state.get("run_aa_tf") == selected_tf:

    with st.spinner(f"Memuat data dan menganalisis {ticker} ({selected_tf})..."):
        quote = get_quote(ticker)
        hist = get_history(ticker, config["period"], config["interval"])
        fundamentals = get_stock_fundamentals(ticker)

    if quote.get("price", 0) == 0 or hist.empty:
        st.error(f"Tidak dapat memuat data untuk **{ticker}**.")
        show_disclosure()
        st.stop()

    report = run_auto_analysis(hist, config)
    if "error" in report:
        st.error(report["error"])
        show_disclosure()
        st.stop()

    # ── Header ──
    name = fundamentals.get("shortName") or quote["name"]
    logo = get_logo_html(ticker, size=48)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin:12px 0;">
        {logo}
        <div>
            <h2 style="margin:0;">{name}</h2>
            <p style="color:#888;margin:2px 0;">{ticker} · Rp{quote['price']:,.0f} ({quote['pctChange']:+.2f}%)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # ── Signal Badge & Confidence ──
    # ══════════════════════════════════════════════
    signal = report["overall_signal"]
    confidence = report["confidence"]
    signal_colors = {"BULLISH": "#00d4aa", "BEARISH": "#ff4757", "NETRAL": "#f59e0b"}
    signal_icons = {"BULLISH": "🐂", "BEARISH": "🐻", "NETRAL": "⚖️"}
    sig_color = signal_colors.get(signal, "#888")
    sig_icon = signal_icons.get(signal, "")

    sc1, sc2, sc3 = st.columns([1.5, 1, 1])
    with sc1:
        st.markdown(f"""
        <div class="gauge-card" style="text-align:center;border:2px solid {sig_color};">
            <p style="font-size:3rem;margin:0;">{sig_icon}</p>
            <h2 style="color:{sig_color};margin:8px 0;">{signal}</h2>
            <p style="color:#888;">Sinyal keseluruhan untuk {config['label']}</p>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.85rem;">Confidence</p>
            <p style="font-size:2.2rem;font-weight:700;color:{sig_color};margin:8px 0;">{confidence}%</p>
            <p style="color:#888;font-size:0.8rem;">Bull: {report['bull_points']:.1f} · Bear: {report['bear_points']:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        vals = report["values"]
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.85rem;">Key Levels</p>
            <p style="color:#00d4aa;font-size:0.9rem;">▲ R: Rp{report['levels']['resistance_1']:,.0f}</p>
            <p style="font-weight:700;font-size:1.1rem;">Rp{vals['price']:,.0f}</p>
            <p style="color:#ff4757;font-size:0.9rem;">▼ S: Rp{report['levels']['support_1']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════
    # ── Detected Signals ──
    # ══════════════════════════════════════════════
    st.subheader(":material/cell_tower: Sinyal Terdeteksi")

    bullish_signals = [s for s in report["signals"] if s["type"] == "bullish"]
    bearish_signals = [s for s in report["signals"] if s["type"] == "bearish"]
    neutral_signals = [s for s in report["signals"] if s["type"] == "neutral"]

    sig_col1, sig_col2 = st.columns(2)
    with sig_col1:
        st.markdown("**:material/trending_up: Sinyal Bullish**")
        if bullish_signals:
            for s in bullish_signals:
                st.markdown(f"""
                <div style="padding:8px 12px;margin:4px 0;border-left:3px solid #00d4aa;background:rgba(0,212,170,0.05);border-radius:6px;">
                    <b style="color:#00d4aa;">{s['name']}</b><br>
                    <span style="color:#aaa;font-size:0.85rem;">{s['detail']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Tidak ada sinyal bullish")

    with sig_col2:
        st.markdown("**:material/trending_down: Sinyal Bearish**")
        if bearish_signals:
            for s in bearish_signals:
                st.markdown(f"""
                <div style="padding:8px 12px;margin:4px 0;border-left:3px solid #ff4757;background:rgba(255,71,87,0.05);border-radius:6px;">
                    <b style="color:#ff4757;">{s['name']}</b><br>
                    <span style="color:#aaa;font-size:0.85rem;">{s['detail']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Tidak ada sinyal bearish")

    if neutral_signals:
        st.markdown("**:material/remove: Sinyal Netral**")
        for s in neutral_signals:
            st.markdown(f"""
            <div style="padding:6px 12px;margin:3px 0;border-left:3px solid #888;background:rgba(136,136,136,0.05);border-radius:6px;">
                <b>{s['name']}</b> – <span style="color:#aaa;">{s['detail']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════
    # ── Technical Chart ──
    # ══════════════════════════════════════════════
    st.subheader(":material/show_chart: Chart Teknikal")

    ind = report["indicators_series"]
    x = hist.index

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.45, 0.15, 0.2, 0.2])

    # Panel 1: Candlestick + SMAs + BB
    fig.add_trace(go.Candlestick(
        x=x, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"],
        increasing_line_color=_GREEN, decreasing_line_color=_RED,
        showlegend=False,
    ), row=1, col=1)

    for key, color, name_lbl in [
        ("sma_fast", "#f59e0b", f"SMA-{config['sma_fast']}"),
        ("sma_mid", "#3b82f6", f"SMA-{config['sma_mid']}"),
        ("sma_slow", "#a855f7", f"SMA-{config['sma_slow']}"),
    ]:
        fig.add_trace(go.Scatter(x=x, y=ind[key], name=name_lbl, mode="lines",
                                 line=dict(color=color, width=1.2)), row=1, col=1)

    fig.add_trace(go.Scatter(x=x, y=ind["bb_upper"], name="BB Upper", mode="lines",
                             line=dict(color="#888", width=0.7, dash="dash"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=ind["bb_lower"], name="BB Lower", mode="lines",
                             line=dict(color="#888", width=0.7, dash="dash"), showlegend=False,
                             fill="tonexty", fillcolor="rgba(136,136,136,0.04)"), row=1, col=1)

    # Support/Resistance lines
    fig.add_hline(y=report["levels"]["resistance_1"], line_dash="dot",
                  line_color="rgba(0,212,170,0.4)", row=1, col=1,
                  annotation_text="R1", annotation_position="right")
    fig.add_hline(y=report["levels"]["support_1"], line_dash="dot",
                  line_color="rgba(255,71,87,0.4)", row=1, col=1,
                  annotation_text="S1", annotation_position="right")

    # Panel 2: Volume
    if "Volume" in hist.columns:
        vol_colors = [_GREEN if hist["Close"].iloc[i] >= hist["Open"].iloc[i] else _RED
                      for i in range(len(hist))]
        fig.add_trace(go.Bar(x=x, y=hist["Volume"], marker_color=vol_colors, opacity=0.5,
                             showlegend=False), row=2, col=1)
        fig.update_yaxes(title_text="Vol", row=2, col=1)

    # Panel 3: MACD
    fig.add_trace(go.Scatter(x=x, y=ind["macd_line"], name="MACD", mode="lines",
                             line=dict(color="#3b82f6", width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=ind["macd_signal"], name="Signal", mode="lines",
                             line=dict(color="#f59e0b", width=1.2)), row=3, col=1)
    hist_colors = [_GREEN if v >= 0 else _RED for v in ind["macd_hist"]]
    fig.add_trace(go.Bar(x=x, y=ind["macd_hist"], marker_color=hist_colors, opacity=0.6,
                         showlegend=False), row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)

    # Panel 4: RSI
    fig.add_trace(go.Scatter(x=x, y=ind["rsi"], name="RSI", mode="lines",
                             line=dict(color="#a855f7", width=1.5)), row=4, col=1)
    fig.add_hline(y=config["rsi_ob"], line_dash="dash", line_color="rgba(255,71,87,0.4)", row=4, col=1)
    fig.add_hline(y=config["rsi_os"], line_dash="dash", line_color="rgba(0,212,170,0.4)", row=4, col=1)
    fig.add_hrect(y0=config["rsi_ob"], y1=100, fillcolor="rgba(255,71,87,0.05)", line_width=0, row=4, col=1)
    fig.add_hrect(y0=0, y1=config["rsi_os"], fillcolor="rgba(0,212,170,0.05)", line_width=0, row=4, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=4, col=1)

    fig.update_layout(
        template="plotly_dark", height=750,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False, hovermode="x unified",
        font=dict(family="Inter"),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)")

    fig.update_layout(dragmode="pan", newshape=dict(line_color='#00d4aa', line_width=2))
    st.plotly_chart(fig, use_container_width=True, config=INTERACTIVE_CONFIG)

    st.divider()

    # ══════════════════════════════════════════════
    # ── Indicator Summary Cards ──
    # ══════════════════════════════════════════════
    st.subheader(":material/summarize: Ringkasan Indikator")

    ic1, ic2, ic3, ic4, ic5 = st.columns(5)
    rsi_val = vals["rsi"]
    rsi_color = "#ff4757" if rsi_val > config["rsi_ob"] else ("#00d4aa" if rsi_val < config["rsi_os"] else "#888")

    with ic1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.8rem;">RSI({config['rsi_period']})</p>
            <p style="font-size:1.5rem;font-weight:700;color:{rsi_color};">{rsi_val:.1f}</p>
        </div>""", unsafe_allow_html=True)
    with ic2:
        m_color = _GREEN if vals["macd_hist"] >= 0 else _RED
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.8rem;">MACD Hist</p>
            <p style="font-size:1.5rem;font-weight:700;color:{m_color};">{vals['macd_hist']:,.0f}</p>
        </div>""", unsafe_allow_html=True)
    with ic3:
        sk_color = "#ff4757" if vals["stoch_k"] > 80 else ("#00d4aa" if vals["stoch_k"] < 20 else "#888")
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.8rem;">Stoch %K</p>
            <p style="font-size:1.5rem;font-weight:700;color:{sk_color};">{vals['stoch_k']:.0f}</p>
        </div>""", unsafe_allow_html=True)
    with ic4:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.8rem;">ATR</p>
            <p style="font-size:1.5rem;font-weight:700;">Rp{vals['atr']:,.0f}</p>
        </div>""", unsafe_allow_html=True)
    with ic5:
        vol_ratio = vals["volume_last"] / max(vals["volume_avg"], 1)
        v_color = "#f59e0b" if vol_ratio > 2 else "#888"
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#888;font-size:0.8rem;">Vol Ratio</p>
            <p style="font-size:1.5rem;font-weight:700;color:{v_color};">{vol_ratio:.1f}x</p>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════
    # ── Support / Resistance & Risk Levels ──
    # ══════════════════════════════════════════════
    st.subheader(":material/straighten: Level & Manajemen Risiko")

    lv1, lv2 = st.columns(2)
    levels = report["levels"]
    with lv1:
        st.markdown(f"""
        <div class="gauge-card">
            <h4>:material/push_pin: Level Kunci</h4>
            <p>🟢 <b>Resistance 1:</b> Rp{levels['resistance_1']:,.0f}</p>
            <p>🟢 <b>Resistance 2 (BB Upper):</b> Rp{levels['resistance_2']:,.0f}</p>
            <p>🔴 <b>Support 1 (SMA-Fast):</b> Rp{levels['support_1']:,.0f}</p>
            <p>🔴 <b>Support 2 (SMA-Slow):</b> Rp{levels['support_2']:,.0f}</p>
            <p>🔴 <b>Support 3 (Recent Low):</b> Rp{levels['support_3']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    with lv2:
        st.markdown(f"""
        <div class="gauge-card">
            <h4>:material/warning: Level Edukatif (Berdasarkan ATR)</h4>
            <p style="color:#888;font-size:0.85rem;">Level ini dihitung otomatis dari ATR, bukan rekomendasi.</p>
            <p>🛑 <b>Stop Loss Area:</b> Rp{levels['stop_loss_suggest']:,.0f} <span style="color:#888;">(−1.5x ATR)</span></p>
            <p>🎯 <b>Take Profit Area:</b> Rp{levels['take_profit_suggest']:,.0f} <span style="color:#888;">(+2x ATR)</span></p>
            <p>📏 <b>ATR({config['atr_period']}):</b> Rp{levels['atr']:,.0f}</p>
            <p>📊 <b>Risk/Reward Ratio:</b> 1 : {2/1.5:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════
    # ── AI Analysis ──
    # ══════════════════════════════════════════════
    st.subheader(":material/smart_toy: Analisis AI")

    if not GROQ_API_KEY:
        st.warning("⚠️ GROQ_API_KEY belum diset. Tambahkan ke file `.env`.")
    else:
        ai_state_key = f"aa_ai_result_{ticker}_{selected_tf}"
        
        if st.button(f":material/psychology: Generate Analisis AI ({selected_tf})", key="btn_ai_auto"):
            with st.spinner("AI sedang menganalisis..."):
                result = timeframe_analysis(ticker, name, selected_tf, report, fundamentals)
                st.session_state[ai_state_key] = result
                st.session_state[ai_state_key + "_new"] = True
                
        if ai_state_key in st.session_state:
            if st.session_state.get(ai_state_key + "_new"):
                st.write_stream(stream_text(st.session_state[ai_state_key]))
                st.session_state[ai_state_key + "_new"] = False
            else:
                st.markdown(st.session_state[ai_state_key])

show_disclosure()
