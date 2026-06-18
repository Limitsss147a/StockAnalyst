"""📅 Kalender CA – Corporate Actions tracker (Dividends, Splits)."""

from lib.config import setup_page, show_disclosure
setup_page("Kalender CA – Analis Saham")

import streamlit as st
import pandas as pd
from lib.corporate_actions import get_corporate_actions, format_ca_dataframe
from lib.portfolio import load_portfolio
from lib.market_data import format_idr
from lib.logos import get_logo_html

st.title(":material/event_note: Kalender Aksi Korporasi")
st.caption("Lacak jadwal dividen dan *stock split* untuk emiten di pasar saham Indonesia.")

tab_portofolio, tab_cari = st.tabs([":material/account_balance_wallet: CA Portofolio Saya", ":material/search: Cari Saham"])

# ── TAB: CA Portofolio ──
with tab_portofolio:
    st.subheader(":material/inventory_2: Aksi Korporasi Portofolio")
    
    holdings = load_portfolio()
    if not holdings:
        st.info(":material/folder_open: Portofolio Anda masih kosong. Tambahkan saham di halaman Portofolio untuk melihat kalendernya di sini.")
    else:
        tickers = [h["ticker"] for h in holdings]
        
        if st.button(":material/sync: Muat Data Portofolio", type="primary", key="btn_load_porto_ca"):
            with st.spinner("Memuat riwayat dividen dan split portofolio Anda..."):
                all_divs = []
                all_splits = []
                
                for ticker in tickers:
                    ca = get_corporate_actions(ticker)
                    
                    df_div = format_ca_dataframe(ca["dividends"], "Dividen")
                    if not df_div.empty:
                        df_div["Emiten"] = ticker.replace('.JK', '')
                        all_divs.append(df_div)
                        
                    df_split = format_ca_dataframe(ca["splits"], "Stock Split")
                    if not df_split.empty:
                        df_split["Emiten"] = ticker.replace('.JK', '')
                        all_splits.append(df_split)
                
                if all_divs:
                    combined_divs = pd.concat(all_divs, ignore_index=True)
                    # Convert 'Tanggal' back to datetime for sorting
                    combined_divs["DateObj"] = pd.to_datetime(combined_divs["Tanggal"], format="%d %b %Y")
                    combined_divs = combined_divs.sort_values(by="DateObj", ascending=False).drop(columns=["DateObj"])
                    
                    st.markdown("#### 💰 Histori Dividen Terakhir (Portofolio)")
                    st.dataframe(
                        combined_divs[["Tanggal", "Emiten", "Nilai", "Tipe"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Nilai": st.column_config.NumberColumn("Nilai (Rp/Rasio)", format="Rp %.2f")
                        }
                    )
                else:
                    st.info("Tidak ada histori dividen untuk saham di portofolio Anda dalam 5 tahun terakhir.")

# ── TAB: Cari Saham ──
with tab_cari:
    st.subheader(":material/manage_search: Cari Histori Dividen & Split")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Kode Saham", value="BBCA.JK", placeholder="Contoh: BBRI.JK")
    with col_btn:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        search_ca = st.button(":material/search: Cari", use_container_width=True)
        
    if search_ca:
        ticker = ticker_input.strip().upper()
        if not ticker.endswith(".JK") and not ticker.startswith("^"):
            ticker += ".JK"
            
        with st.spinner(f"Mengambil data {ticker}..."):
            ca_data = get_corporate_actions(ticker)
            
        logo = get_logo_html(ticker, size=48)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;margin:12px 0;">
            {logo}
            <div>
                <h3 style="margin:0;">{ticker.replace('.JK', '')}</h3>
                <p style="color:#888;margin:2px 0;">Histori Aksi Korporasi (5 Tahun Terakhir)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Next Div Estimation
        est = ca_data["next_div_est"]
        if est:
            status_color = "#888" if est["is_passed"] else "#00d4aa"
            status_text = "Sudah Lewat (Estimasi)" if est["is_passed"] else "Mendekati (Estimasi)"
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {status_color};">
                <h4 style="margin-top:0;">:material/calendar_month: Estimasi Siklus Dividen Selanjutnya</h4>
                <p style="font-size:1.1rem;margin:4px 0;">Berdasarkan riwayat, dividen berikutnya diperkirakan sekitar: <b>{est['estimated_date']}</b></p>
                <p style="color:#888;margin:0;">Nilai dividen sebelumnya: <b>Rp{est['last_amount']:.2f}</b> · Status: <span style="color:{status_color};font-weight:600;">{status_text}</span></p>
                <p style="color:#555;font-size:0.8rem;margin-top:8px;">*Ini hanya perhitungan kalender kasar berdasarkan interval 1 tahun dari dividen terakhir. Bukan jaminan.</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 💰 Histori Dividen")
            df_div = format_ca_dataframe(ca_data["dividends"], "Dividen")
            if not df_div.empty:
                st.dataframe(
                    df_div, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Nilai": st.column_config.NumberColumn("Dividen (Rp)", format="Rp %.2f")
                    }
                )
            else:
                st.info("Tidak ada data dividen.")
                
        with c2:
            st.markdown("#### ✂️ Histori Stock Split")
            df_split = format_ca_dataframe(ca_data["splits"], "Stock Split")
            if not df_split.empty:
                st.dataframe(df_split, use_container_width=True, hide_index=True)
            else:
                st.info("Tidak ada histori stock split.")

show_disclosure()
