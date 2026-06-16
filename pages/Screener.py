"""🔎 Screener – Stock screener with technical and fundamental filters."""

from lib.config import setup_page, show_disclosure
setup_page("Screener Saham – Analis Saham")

import streamlit as st
from lib.screener import screen_stocks, PRESETS
from lib.market_data import TOP_IDX_STOCKS, format_idr, color_for_change
from lib.logos import get_logo_html

st.title("🔎 Screener Saham")
st.caption("Filter saham IDX berdasarkan kriteria teknikal dan fundamental")

# ── Preset Filters ──
st.subheader("⚡ Preset Cepat")
preset_cols = st.columns(len(PRESETS))
selected_preset = None
for i, (name, _) in enumerate(PRESETS.items()):
    with preset_cols[i]:
        if st.button(name, key=f"preset_{i}", use_container_width=True):
            selected_preset = name

# ── Custom Filters ──
with st.expander("🔧 Filter Kustom", expanded=selected_preset is None):
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**📉 Teknikal**")
        rsi_range = st.slider("RSI Range", 0, 100, (0, 100), key="rsi_range")
        sma_filter = st.selectbox("Posisi vs SMA", [
            "Semua", "Di atas SMA-20", "Di bawah SMA-20",
            "Di atas SMA-50", "Di bawah SMA-50",
            "Di atas SMA-200", "Di bawah SMA-200",
        ], key="sma_filter")
        vol_surge = st.checkbox("Volume Surge (> 2x rata-rata)", key="vol_surge")

    with fc2:
        st.markdown("**💰 Fundamental**")
        pe_range = st.slider("P/E Range", 0, 100, (0, 100), key="pe_range")
        min_roe = st.number_input("Min ROE (%)", value=0.0, step=1.0, key="min_roe")
        min_mcap = st.number_input("Min Market Cap (Rp Miliar)", value=0.0, step=100.0, key="min_mcap")

# ── Build filter kwargs ──
if selected_preset:
    kwargs = PRESETS[selected_preset].copy()
    kwargs["min_rsi"] = kwargs.get("min_rsi", 0)
    kwargs["max_rsi"] = kwargs.get("max_rsi", 100)
else:
    kwargs = {
        "min_rsi": rsi_range[0],
        "max_rsi": rsi_range[1],
        "min_pe": pe_range[0],
        "max_pe": pe_range[1],
        "min_roe": min_roe,
        "min_mcap": min_mcap * 1e9,
        "volume_surge": vol_surge,
    }
    # SMA filter
    if sma_filter == "Di atas SMA-20":
        kwargs["above_sma20"] = True
    elif sma_filter == "Di bawah SMA-20":
        kwargs["above_sma20"] = False
    elif sma_filter == "Di atas SMA-50":
        kwargs["above_sma50"] = True
    elif sma_filter == "Di bawah SMA-50":
        kwargs["above_sma50"] = False
    elif sma_filter == "Di atas SMA-200":
        kwargs["above_sma200"] = True
    elif sma_filter == "Di bawah SMA-200":
        kwargs["above_sma200"] = False

# ── Run Screener ──
st.divider()

if st.button("🔍 Jalankan Screener", type="primary", use_container_width=True, key="btn_screen"):
    with st.spinner("Memindai saham... (ini mungkin memakan waktu 30-60 detik)"):
        results = screen_stocks(TOP_IDX_STOCKS[:35], **kwargs)

    if results:
        st.success(f"Ditemukan **{len(results)}** saham yang sesuai kriteria.")
        st.subheader("📊 Hasil Screener")

        # Sort options
        sort_by = st.selectbox("Urutkan berdasarkan", [
            "% Perubahan", "RSI", "P/E", "ROE", "Market Cap"
        ], key="sort_by")

        sort_map = {
            "% Perubahan": ("pctChange", True),
            "RSI": ("rsi", False),
            "P/E": ("pe", False),
            "ROE": ("roe", True),
            "Market Cap": ("marketCap", True),
        }
        sort_key, sort_desc = sort_map.get(sort_by, ("pctChange", True))
        results.sort(key=lambda x: x.get(sort_key, 0) or 0, reverse=sort_desc)

        # Results display
        for r in results:
            col_logo, col_info, col_price, col_tech, col_fund = st.columns([0.4, 1.8, 1.2, 1.3, 1.3])
            color = color_for_change(r["pctChange"])
            logo = get_logo_html(r["ticker"], size=36)

            with col_logo:
                st.markdown(f'<div style="padding-top:8px;">{logo}</div>', unsafe_allow_html=True)

            with col_info:
                st.markdown(f"""
                **{r['ticker'].replace('.JK', '')}** · {r['name'][:25]}  
                <span style="color:#888;font-size:0.8rem;">{r.get('sector', 'N/A')}</span>
                """, unsafe_allow_html=True)

            with col_price:
                st.markdown(f"""
                **Rp{r['price']:,.0f}**  
                <span style="color:{color};font-weight:600;">{r['pctChange']:+.2f}%</span>
                """, unsafe_allow_html=True)

            with col_tech:
                rsi = r.get("rsi", 0)
                rsi_color = "#ff4757" if rsi > 70 else ("#00d4aa" if rsi < 30 else "#888")
                sma20_icon = "✅" if r.get("above_sma20") else ("❌" if r.get("above_sma20") is False else "—")
                sma200_icon = "✅" if r.get("above_sma200") else ("❌" if r.get("above_sma200") is False else "—")
                st.markdown(f"""
                RSI: <span style="color:{rsi_color};font-weight:600;">{rsi:.0f}</span> · 
                SMA20: {sma20_icon} · SMA200: {sma200_icon}
                {"🔥 Vol Surge" if r.get("vol_surge") else ""}
                """, unsafe_allow_html=True)

            with col_fund:
                pe_val = r.get("pe", 0)
                roe_val = r.get("roe", 0)
                mcap_str = format_idr(r.get("marketCap", 0))
                st.markdown(f"""
                P/E: **{pe_val:.1f}x** · ROE: **{roe_val:.1f}%**  
                MCap: {mcap_str}
                """)

            st.markdown('<hr style="margin:4px 0;border-color:rgba(255,255,255,0.05);">', unsafe_allow_html=True)

    else:
        st.warning("Tidak ada saham yang sesuai dengan kriteria filter.")

elif selected_preset:
    # Auto-run for presets
    with st.spinner("Memindai saham..."):
        results = screen_stocks(TOP_IDX_STOCKS[:35], **kwargs)

    if results:
        st.success(f"Preset **{selected_preset}**: Ditemukan **{len(results)}** saham.")

        for r in results:
            col_logo, col_info, col_price, col_tech = st.columns([0.4, 2, 1.2, 2])
            color = color_for_change(r["pctChange"])
            logo = get_logo_html(r["ticker"], size=32)

            with col_logo:
                st.markdown(f'<div style="padding-top:6px;">{logo}</div>', unsafe_allow_html=True)
            with col_info:
                st.markdown(f"**{r['ticker'].replace('.JK', '')}** · {r['name'][:25]}")
            with col_price:
                st.markdown(f"Rp{r['price']:,.0f} <span style='color:{color};'>{r['pctChange']:+.2f}%</span>",
                            unsafe_allow_html=True)
            with col_tech:
                rsi = r.get("rsi", 0)
                st.markdown(f"RSI: **{rsi:.0f}** · P/E: **{r.get('pe', 0):.1f}x** · ROE: **{r.get('roe', 0):.1f}%**")
    else:
        st.warning("Tidak ada saham yang sesuai dengan preset ini.")

show_disclosure()
