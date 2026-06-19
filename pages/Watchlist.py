"""👀 Watchlist – Pantauan saham & sistem notifikasi."""

from lib.config import setup_page, show_disclosure
setup_page("Watchlist & Alert – Analis Saham")

import streamlit as st
import datetime
from lib.watchlist import load_watchlist, add_to_watchlist, remove_from_watchlist
from lib.market_data import get_quote, format_idr, color_for_change
from lib.logos import get_logo_html
from lib.alerts import check_stock_alerts
from lib.telegram_bot import is_telegram_configured, send_telegram_message

st.title(":material/notifications_active: Watchlist & Alert System")
st.caption("Pantau saham pilihan Anda dan dapatkan notifikasi otomatis via Telegram jika ada sinyal penting.")

# ── Konfigurasi Telegram ──
if not is_telegram_configured():
    st.warning("⚠️ **Telegram Bot belum dikonfigurasi!** Untuk menerima notifikasi otomatis, tambahkan `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID` di file `.env`.")

# ── Kelola Watchlist ──
st.subheader(":material/add_box: Tambah ke Watchlist")
with st.form("form_add_watchlist"):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        ticker_input = st.text_input("Kode Saham", placeholder="Contoh: BBRI.JK")
    with c2:
        target_buy = st.number_input("Target Beli (Opsional)", min_value=0, step=100)
    with c3:
        target_sell = st.number_input("Target Jual (Opsional)", min_value=0, step=100)
    
    submitted = st.form_submit_button("Simpan ke Watchlist", use_container_width=True)
    if submitted:
        if ticker_input:
            t = ticker_input.strip().upper()
            if not t.endswith(".JK") and not t.startswith("^"):
                t += ".JK"
            add_to_watchlist(t, target_buy, target_sell)
            st.success(f"{t} ditambahkan ke watchlist!")
            st.rerun()

st.divider()

# ── Menampilkan Watchlist ──
st.subheader(":material/checklist: Daftar Pantauan Anda")

watchlist = load_watchlist()

if not watchlist:
    st.info("Watchlist Anda masih kosong. Silakan tambah saham di atas.")
else:
    # Action buttons
    col_cek, col_space = st.columns([2, 3])
    with col_cek:
        run_alerts = st.button(":material/send: Cek Sinyal & Kirim Telegram", type="primary", use_container_width=True)
        
    st.write("")
    
    all_alerts = {}
    
    for item in watchlist:
        t = item["ticker"]
        quote = get_quote(t)
        
        c1, c2, c3 = st.columns([3, 1, 1])
        
        with c1:
            logo = get_logo_html(t, size=32)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;">
                {logo}
                <div>
                    <h4 style="margin:0;">{t.replace('.JK', '')}</h4>
                    <p style="color:#888;margin:0;font-size:0.85rem;">{quote.get('name', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            if quote.get("price", 0) > 0:
                color = color_for_change(quote["pctChange"])
                st.markdown(f"""
                <div style="text-align:right;">
                    <div style="font-weight:700;font-size:1.1rem;">Rp{quote['price']:,.0f}</div>
                    <div style="color:{color};font-weight:600;">{quote['pctChange']:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("Data tidak tersedia")
                
        with c3:
            st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
            if st.button("Hapus", key=f"del_{t}", use_container_width=True):
                remove_from_watchlist(t)
                st.rerun()
                
        # Target Status
        if item['target_buy'] > 0 or item['target_sell'] > 0:
            price = quote.get('price', 0)
            target_text = []
            if item['target_buy'] > 0:
                if price <= item['target_buy']:
                    target_text.append(f"🟢 <b style='color:#00d4aa;'>Mencapai Target Beli</b> (Rp{item['target_buy']:,.0f})")
                else:
                    target_text.append(f"Target Beli: Rp{item['target_buy']:,.0f}")
            if item['target_sell'] > 0:
                if price >= item['target_sell']:
                    target_text.append(f"🔴 <b style='color:#ff4757;'>Mencapai Target Jual</b> (Rp{item['target_sell']:,.0f})")
                else:
                    target_text.append(f"Target Jual: Rp{item['target_sell']:,.0f}")
                    
            st.markdown(f"<p style='color:#888;font-size:0.85rem;margin:8px 0 0 44px;'>{' | '.join(target_text)}</p>", unsafe_allow_html=True)

        if run_alerts:
            with st.spinner(f"Mengecek sinyal untuk {t}..."):
                alerts = check_stock_alerts(t)
                # Check target buy/sell explicitly
                price = quote.get('price', 0)
                if item['target_buy'] > 0 and price <= item['target_buy']:
                    alerts.append(f"🎯 <b>Mencapai Target Beli</b> (Harga: Rp{price:,.0f} <= Target: Rp{item['target_buy']:,.0f})")
                if item['target_sell'] > 0 and price >= item['target_sell']:
                    alerts.append(f"🎯 <b>Mencapai Target Jual</b> (Harga: Rp{price:,.0f} >= Target: Rp{item['target_sell']:,.0f})")
                
                if alerts:
                    all_alerts[t] = alerts
                    st.markdown(f"<div style='margin-left:44px;padding:8px;background:rgba(0,212,170,0.1);border-left:3px solid #00d4aa;border-radius:4px;'>{'<br>'.join(alerts)}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#888;margin-left:44px;'>Tidak ada sinyal khusus saat ini.</p>", unsafe_allow_html=True)
            
        st.divider()

    # Process Sending Telegram
    if run_alerts:
        if all_alerts:
            if is_telegram_configured():
                # Format Telegram Message
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M WIB")
                msg = f"🔔 <b>STOCK ANALYST ALERT</b>\n🕒 {now}\n\n"
                
                for t, alerts in all_alerts.items():
                    msg += f"📌 <b>{t.replace('.JK', '')}</b>\n"
                    for a in alerts:
                        msg += f"• {a}\n"
                    msg += "\n"
                
                success, response_msg = send_telegram_message(msg)
                if success:
                    st.toast("✅ Pesan Telegram berhasil dikirim!")
                    st.success("Pesan peringatan berhasil dikirim ke Telegram Anda.")
                else:
                    st.error(f"Gagal mengirim Telegram: {response_msg}")
            else:
                st.warning("⚠️ Terdapat sinyal alert, namun Telegram belum dikonfigurasi. Pesan tidak terkirim.")
        else:
            st.info("Tidak ada sinyal alert yang aktif dari seluruh watchlist Anda.")

show_disclosure()
