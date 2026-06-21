"""🤖 Auto Analisis – Automated technical analysis by timeframe."""

from lib.config import setup_page, show_disclosure, GROQ_API_KEY, stream_text
setup_page("Auto Analisis – Analis Saham")

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lib.market_data import get_quote, get_history, get_stock_fundamentals, format_idr
from lib.auto_analysis import TIMEFRAMES, run_auto_analysis
from lib.bandarmology import run_bandarmology_analysis
from lib.groq_analyst import timeframe_analysis, bandarmology_analysis
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
            <h4>Level Kunci</h4>
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
            <h4>Level Edukatif (Berdasarkan ATR)</h4>
            <p style="color:#888;font-size:0.85rem;">Level ini dihitung otomatis dari ATR, bukan rekomendasi.</p>
            <p>🛑 <b>Stop Loss Area:</b> Rp{levels['stop_loss_suggest']:,.0f} <span style="color:#888;">(−1.5x ATR)</span></p>
            <p>🎯 <b>Take Profit Area:</b> Rp{levels['take_profit_suggest']:,.0f} <span style="color:#888;">(+2x ATR)</span></p>
            <p>📏 <b>ATR({config['atr_period']}):</b> Rp{levels['atr']:,.0f}</p>
            <p>📊 <b>Risk/Reward Ratio:</b> 1 : {2/1.5:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════
    # ── Historical Backtesting ──
    # ══════════════════════════════════════════════
    st.subheader(":material/history: Backtesting Historis")
    st.caption("Uji akurasi sinyal indikator di masa lalu. Berapa persentase kemenangan (Win Rate) jika Anda mengikuti sinyal ini?")
    
    import pandas as pd
    from lib.backtester import SIGNAL_TYPES
    
    bt_col1, bt_col2 = st.columns(2)
    with bt_col1:
        bt_signal_label = st.selectbox(
            "Pilih Sinyal untuk Diuji",
            list(SIGNAL_TYPES.values()),
            help="Pilih jenis sinyal teknikal yang ingin divalidasi akurasinya."
        )
    with bt_col2:
        bt_days = st.slider("Target Evaluasi (Hari)", 3, 30, 10, 
                            help="Setelah sinyal muncul, harga dievaluasi X hari kemudian.")
    
    # Reverse-lookup signal key
    sig_key = [k for k, v in SIGNAL_TYPES.items() if v == bt_signal_label][0]
    
    if st.button(":material/science: Jalankan Backtest", type="secondary", use_container_width=True):
        # Use longer history for backtesting (2 years)
        from lib.market_data import get_history as bt_get_history
        bt_hist = bt_get_history(ticker, "2y")
        
        with st.spinner(f"Menghitung backtest {bt_signal_label} pada {ticker}..."):
            from lib.backtester import run_backtest
            bt_results = run_backtest(bt_hist, sig_key, bt_days)
        
        st.session_state["bt_results"] = bt_results
        st.session_state["bt_signal_label"] = bt_signal_label
        st.session_state["bt_ticker"] = ticker
        st.session_state["bt_days"] = bt_days
    
    # Display results from session state
    if "bt_results" in st.session_state and st.session_state.get("bt_ticker") == ticker:
        bt_results = st.session_state["bt_results"]
        bt_signal_label = st.session_state["bt_signal_label"]
        bt_days = st.session_state["bt_days"]
        
        btc1, btc2, btc3, btc4, btc5 = st.columns(5)
        with btc1:
            st.metric("Total Sinyal", bt_results["total"])
        with btc2:
            wr = bt_results["win_rate"]
            delta_text = "Akurat" if wr >= 60 else ("Netral" if wr >= 40 else "Buruk")
            st.metric("Win Rate", f"{wr:.1f}%", delta=delta_text, delta_color="normal" if wr >= 50 else "inverse")
        with btc3:
            st.metric("Win / Loss", f"{bt_results['wins']} / {bt_results['losses']}")
        with btc4:
            avg_r = bt_results["avg_return"]
            st.metric("Avg Return", f"{avg_r:+.2f}%", delta_color="normal" if avg_r >= 0 else "inverse")
        with btc5:
            st.metric("Max Drawdown", f"{bt_results['max_drawdown']:.2f}%")
            
        if bt_results["total"] > 0:
            wr = bt_results["win_rate"]
            avg_r = bt_results["avg_return"]
            
            if wr >= 70 and avg_r > 0:
                st.success(f"🏆 Sinyal **{bt_signal_label}** terbukti **Sangat Akurat** (Win Rate {wr:.1f}%, Avg Return {avg_r:+.2f}%) pada {ticker.replace('.JK', '')} dalam 2 tahun terakhir.")
            elif wr >= 55 and avg_r > 0:
                st.success(f"✅ Sinyal **{bt_signal_label}** menunjukkan hasil **Cukup Baik** (Win Rate {wr:.1f}%, Avg Return {avg_r:+.2f}%).")
            elif wr <= 40 or avg_r < -1:
                st.error(f"❌ Sinyal **{bt_signal_label}** ternyata **Kurang Efektif** (Win Rate {wr:.1f}%, Avg Return {avg_r:+.2f}%) untuk {ticker.replace('.JK', '')}.")
            else:
                st.info(f"⚖️ Sinyal **{bt_signal_label}** memberikan hasil **Netral** (Win Rate {wr:.1f}%) — tidak cukup konsisten.")
                
            # Trade Log Table
            if bt_results["trades"]:
                with st.expander(f":material/table_chart: Lihat Detail {bt_results['total']} Trade"):
                    trade_df = pd.DataFrame(bt_results["trades"])
                    trade_df.columns = ["Tanggal", "Entry (Rp)", "Exit (Rp)", "Return (%)", "Max DD (%)", "Hasil"]
                    
                    st.dataframe(
                        trade_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Return (%)": st.column_config.NumberColumn(format="%.2f%%"),
                            "Max DD (%)": st.column_config.NumberColumn(format="%.2f%%"),
                            "Entry (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                            "Exit (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                            "Hasil": st.column_config.TextColumn(),
                        }
                    )
        else:
            st.warning(f"Tidak ada sinyal **{bt_signal_label}** yang terjadi pada {ticker.replace('.JK', '')} dalam 2 tahun terakhir.")

    st.divider()

    # ══════════════════════════════════════════════
    # ── Bandarmology Analysis ──
    # ══════════════════════════════════════════════
    st.subheader(":material/account_balance: Analisis Bandarmologi")
    st.caption("Tracking pergerakan big money (bandar) menggunakan indikator money flow, OBV, dan pola akumulasi/distribusi")

    with st.spinner("Menganalisis pergerakan bandar..."):
        bandar_report = run_bandarmology_analysis(hist, config)

    if "error" in bandar_report:
        st.warning(bandar_report["error"])
    else:
        bandar_overall = bandar_report["overall"]
        bandar_confidence = bandar_report["confidence"]
        bandar_colors = {
            "AKUMULASI": "#00d4aa",
            "DISTRIBUSI": "#ff4757",
            "NETRAL": "#f59e0b"
        }
        bandar_icons = {
            "AKUMULASI": "💰",
            "DISTRIBUSI": "🚨",
            "NETRAL": "⚖️"
        }
        b_color = bandar_colors.get(bandar_overall, "#888")
        b_icon = bandar_icons.get(bandar_overall, "")

        # ── Bandar Signal Badge ──
        bc1, bc2, bc3, bc4 = st.columns([1.5, 1, 1, 1])
        with bc1:
            st.markdown(f"""
            <div class="gauge-card" style="text-align:center;border:2px solid {b_color};">
                <p style="font-size:2.5rem;margin:0;">{b_icon}</p>
                <h2 style="color:{b_color};margin:8px 0;font-size:1.5rem;">{bandar_overall}</h2>
                <p style="color:#888;font-size:0.85rem;">{bandar_report['conclusion']}</p>
            </div>
            """, unsafe_allow_html=True)
        with bc2:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Confidence</p>
                <p style="font-size:2rem;font-weight:700;color:{b_color};margin:8px 0;">{bandar_confidence}%</p>
                <p style="color:#888;font-size:0.75rem;">Akum: {bandar_report['accum_points']:.1f} · Dist: {bandar_report['distrib_points']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        with bc3:
            bandar_score = bandar_report['values']['bandar_score']
            bs_color = "#00d4aa" if bandar_score > 0 else ("#ff4757" if bandar_score < 0 else "#888")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Bandar Score</p>
                <p style="font-size:2rem;font-weight:700;color:{bs_color};margin:8px 0;">{bandar_score:+.0f}</p>
                <p style="color:#888;font-size:0.75rem;">-100 (distribusi) ↔ +100 (akumulasi)</p>
            </div>
            """, unsafe_allow_html=True)
        with bc4:
            mfi_val = bandar_report['values']['mfi']
            mfi_color = "#ff4757" if mfi_val > 80 else ("#00d4aa" if mfi_val < 20 else "#f59e0b" if mfi_val > 60 else "#888")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Money Flow Index</p>
                <p style="font-size:2rem;font-weight:700;color:{mfi_color};margin:8px 0;">{mfi_val:.1f}</p>
                <p style="color:#888;font-size:0.75rem;">{'Overbought' if mfi_val > 80 else 'Oversold' if mfi_val < 20 else 'Normal'}</p>
            </div>
            """, unsafe_allow_html=True)

        # ── Bandar Signals ──
        st.markdown("")
        accum_signals = [s for s in bandar_report["signals"] if s["type"] == "accumulation"]
        distrib_signals = [s for s in bandar_report["signals"] if s["type"] == "distribution"]
        neutral_signals_b = [s for s in bandar_report["signals"] if s["type"] == "neutral"]

        bsig1, bsig2 = st.columns(2)
        with bsig1:
            st.markdown("**:material/add_circle: Sinyal Akumulasi (Beli)**")
            if accum_signals:
                for s in accum_signals:
                    st.markdown(f"""
                    <div style="padding:8px 12px;margin:4px 0;border-left:3px solid #00d4aa;background:rgba(0,212,170,0.05);border-radius:6px;">
                        <b style="color:#00d4aa;">{s['name']}</b><br>
                        <span style="color:#aaa;font-size:0.85rem;">{s['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Tidak ada sinyal akumulasi")

        with bsig2:
            st.markdown("**:material/remove_circle: Sinyal Distribusi (Jual)**")
            if distrib_signals:
                for s in distrib_signals:
                    st.markdown(f"""
                    <div style="padding:8px 12px;margin:4px 0;border-left:3px solid #ff4757;background:rgba(255,71,87,0.05);border-radius:6px;">
                        <b style="color:#ff4757;">{s['name']}</b><br>
                        <span style="color:#aaa;font-size:0.85rem;">{s['detail']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Tidak ada sinyal distribusi")

        if neutral_signals_b:
            for s in neutral_signals_b:
                st.markdown(f"""
                <div style="padding:6px 12px;margin:3px 0;border-left:3px solid #f59e0b;background:rgba(245,158,11,0.05);border-radius:6px;">
                    <b style="color:#f59e0b;">{s['name']}</b> – <span style="color:#aaa;">{s['detail']}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── Money Flow Chart ──
        st.markdown("")
        st.markdown("**:material/waterfall_chart: Chart Bandarmologi**")

        b_ind = bandar_report["indicators_series"]
        x = hist.index

        from plotly.subplots import make_subplots
        import plotly.graph_objects as go

        fig_bandar = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.3, 0.25, 0.25, 0.2],
            subplot_titles=["Harga + Volume Bandar", "Money Flow Index (MFI)",
                            "On-Balance Volume (OBV)", "Chaikin Money Flow (CMF)"]
        )

        # Panel 1: Candlestick + Big Volume markers
        fig_bandar.add_trace(go.Candlestick(
            x=x, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"],
            increasing_line_color=_GREEN, decreasing_line_color=_RED,
            showlegend=False,
        ), row=1, col=1)

        # Mark accumulation days
        big_money_data = bandar_report["big_money"]
        accum_mask = big_money_data["accum_mask"]
        distrib_mask = big_money_data["distrib_mask"]

        if accum_mask.any():
            accum_dates = hist.index[accum_mask]
            accum_prices = hist["Low"][accum_mask] * 0.98
            fig_bandar.add_trace(go.Scatter(
                x=accum_dates, y=accum_prices,
                mode="markers", name="Akumulasi",
                marker=dict(symbol="triangle-up", size=12, color="#00d4aa",
                           line=dict(width=1, color="white")),
                hovertemplate="Akumulasi<br>%{x}<extra></extra>",
            ), row=1, col=1)

        if distrib_mask.any():
            distrib_dates = hist.index[distrib_mask]
            distrib_prices = hist["High"][distrib_mask] * 1.02
            fig_bandar.add_trace(go.Scatter(
                x=distrib_dates, y=distrib_prices,
                mode="markers", name="Distribusi",
                marker=dict(symbol="triangle-down", size=12, color="#ff4757",
                           line=dict(width=1, color="white")),
                hovertemplate="Distribusi<br>%{x}<extra></extra>",
            ), row=1, col=1)

        # Panel 2: MFI
        mfi_colors = []
        for v in b_ind["mfi"]:
            if v > 80:
                mfi_colors.append("#ff4757")
            elif v < 20:
                mfi_colors.append("#00d4aa")
            else:
                mfi_colors.append("#a855f7")

        fig_bandar.add_trace(go.Scatter(
            x=x, y=b_ind["mfi"], name="MFI", mode="lines",
            line=dict(color="#a855f7", width=1.5),
        ), row=2, col=1)
        fig_bandar.add_hline(y=80, line_dash="dash", line_color="rgba(255,71,87,0.5)", row=2, col=1)
        fig_bandar.add_hline(y=20, line_dash="dash", line_color="rgba(0,212,170,0.5)", row=2, col=1)
        fig_bandar.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,0.15)", row=2, col=1)
        fig_bandar.add_hrect(y0=80, y1=100, fillcolor="rgba(255,71,87,0.05)", line_width=0, row=2, col=1)
        fig_bandar.add_hrect(y0=0, y1=20, fillcolor="rgba(0,212,170,0.05)", line_width=0, row=2, col=1)
        fig_bandar.update_yaxes(title_text="MFI", range=[0, 100], row=2, col=1)

        # Panel 3: OBV + OBV SMA
        fig_bandar.add_trace(go.Scatter(
            x=x, y=b_ind["obv"], name="OBV", mode="lines",
            line=dict(color="#3b82f6", width=1.5),
        ), row=3, col=1)
        fig_bandar.add_trace(go.Scatter(
            x=x, y=b_ind["obv_sma"], name="OBV SMA(20)", mode="lines",
            line=dict(color="#f59e0b", width=1, dash="dash"),
        ), row=3, col=1)
        fig_bandar.update_yaxes(title_text="OBV", row=3, col=1)

        # Panel 4: CMF
        cmf_vals = b_ind["cmf"]
        cmf_colors = [_GREEN if v >= 0 else _RED for v in cmf_vals]
        fig_bandar.add_trace(go.Bar(
            x=x, y=cmf_vals, marker_color=cmf_colors, opacity=0.7,
            showlegend=False, name="CMF",
        ), row=4, col=1)
        fig_bandar.add_hline(y=0, line_color="rgba(255,255,255,0.2)", row=4, col=1)
        fig_bandar.update_yaxes(title_text="CMF", row=4, col=1)

        fig_bandar.update_layout(
            template="plotly_dark", height=800,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_rangeslider_visible=False, hovermode="x unified",
            font=dict(family="Inter"),
            legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
            dragmode="pan",
        )
        fig_bandar.update_xaxes(gridcolor="rgba(255,255,255,0.04)")
        fig_bandar.update_yaxes(gridcolor="rgba(255,255,255,0.04)")

        st.plotly_chart(fig_bandar, use_container_width=True, config=INTERACTIVE_CONFIG)

        # ── Money Flow Indicator Cards ──
        st.markdown("")
        st.markdown("**:material/monitoring: Indikator Money Flow**")

        bv = bandar_report["values"]
        bic1, bic2, bic3, bic4, bic5 = st.columns(5)

        with bic1:
            cmf_v = bv["cmf"]
            cmf_c = "#00d4aa" if cmf_v > 0.05 else ("#ff4757" if cmf_v < -0.05 else "#888")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Chaikin MF</p>
                <p style="font-size:1.4rem;font-weight:700;color:{cmf_c};">{cmf_v:.3f}</p>
                <p style="color:#888;font-size:0.7rem;">{'Beli 🟢' if cmf_v > 0 else 'Jual 🔴'}</p>
            </div>""", unsafe_allow_html=True)
        with bic2:
            fi_v = bv["force_index"]
            fi_c = "#00d4aa" if fi_v > 0 else "#ff4757"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Force Index</p>
                <p style="font-size:1.4rem;font-weight:700;color:{fi_c};">{fi_v:,.0f}</p>
                <p style="color:#888;font-size:0.7rem;">{'Bulls 🐂' if fi_v > 0 else 'Bears 🐻'}</p>
            </div>""", unsafe_allow_html=True)
        with bic3:
            obv_above = bv["obv"] > bv["obv_sma"]
            obv_c = "#00d4aa" if obv_above else "#ff4757"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">OBV Trend</p>
                <p style="font-size:1.4rem;font-weight:700;color:{obv_c};">{'↗ Naik' if obv_above else '↘ Turun'}</p>
                <p style="color:#888;font-size:0.7rem;">vs SMA(20)</p>
            </div>""", unsafe_allow_html=True)
        with bic4:
            big_money_info = bandar_report["big_money"]
            acc_d = big_money_info["accumulation_days"]
            dis_d = big_money_info["distribution_days"]
            ratio_text = f"{acc_d}A / {dis_d}D"
            ratio_c = "#00d4aa" if acc_d > dis_d else ("#ff4757" if dis_d > acc_d else "#f59e0b")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Akum vs Dist</p>
                <p style="font-size:1.4rem;font-weight:700;color:{ratio_c};">{ratio_text}</p>
                <p style="color:#888;font-size:0.7rem;">Hari volume besar</p>
            </div>""", unsafe_allow_html=True)
        with bic5:
            vol_5_20 = bv["volume_avg_5"] / max(bv["volume_avg_20"], 1)
            vol_c = "#f59e0b" if vol_5_20 > 1.5 else ("#888" if vol_5_20 > 0.7 else "#3b82f6")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <p style="color:#888;font-size:0.8rem;">Vol Trend</p>
                <p style="font-size:1.4rem;font-weight:700;color:{vol_c};">{vol_5_20:.1f}x</p>
                <p style="color:#888;font-size:0.7rem;">5d vs 20d avg</p>
            </div>""", unsafe_allow_html=True)

        # ── Bandarmology AI Analysis ──
        st.markdown("")
        if GROQ_API_KEY:
            ai_bandar_key = f"aa_bandar_ai_{ticker}_{selected_tf}"

            if st.button(":material/psychology: Generate Analisis AI Bandarmologi", key="btn_ai_bandar"):
                with st.spinner("AI sedang menganalisis pergerakan bandar..."):
                    bandar_ai_result = bandarmology_analysis(
                        ticker, name, bandar_report, report, selected_tf
                    )
                    st.session_state[ai_bandar_key] = bandar_ai_result
                    st.session_state[ai_bandar_key + "_new"] = True

            if ai_bandar_key in st.session_state:
                if st.session_state.get(ai_bandar_key + "_new"):
                    st.write_stream(stream_text(st.session_state[ai_bandar_key]))
                    st.session_state[ai_bandar_key + "_new"] = False
                else:
                    st.markdown(st.session_state[ai_bandar_key])

    st.divider()

    # ══════════════════════════════════════════════
    # ── AI Analysis ──
    # ══════════════════════════════════════════════
    st.subheader(":material/smart_toy: Analisis AI Teknikal")

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
