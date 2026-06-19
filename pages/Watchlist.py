"""👀 Watchlist – Pantauan saham & sistem notifikasi."""

from lib.config import setup_page, show_disclosure
setup_page("Watchlist & Alert – Analis Saham")

import streamlit as st
import datetime
from lib.watchlist import load_watchlist, add_to_watchlist, remove_from_watchlist
from lib.market_data import get_quote, format_idr, color_for_change
from lib.logos import get_logo_html
from lib.alerts import check_stock_alerts, format_alerts_html, format_alerts_telegram
from lib.telegram_bot import is_telegram_configured, send_telegram_message

st.title(":material/notifications_active: Watchlist & Alert System")
st.caption("Pantau saham pilihan Anda dan dapatkan notifikasi otomatis via Telegram jika ada sinyal penting.")

# ── Telegram Status ──
tg_ok = is_telegram_configured()
if tg_ok:
    st.success("✅ **Telegram Bot terhubung.** Notifikasi akan dikirim otomatis saat ada sinyal.")
else:
    st.warning("⚠️ **Telegram Bot belum dikonfigurasi.** Tambahkan `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID` di file `.env` untuk menerima notifikasi.")

# ── Kelola Watchlist ──
st.subheader(":material/add_box: Tambah ke Watchlist")
with st.form("form_add_watchlist", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        ticker_input = st.text_input("Kode Saham", placeholder="Contoh: BBRI.JK")
    with c2:
        target_buy = st.number_input("Target Beli (Opsional)", min_value=0, step=50, help="Notifikasi jika harga turun ke level ini.")
    with c3:
        target_sell = st.number_input("Target Jual (Opsional)", min_value=0, step=50, help="Notifikasi jika harga naik ke level ini.")
    
    submitted = st.form_submit_button(":material/add: Simpan ke Watchlist", use_container_width=True)
    if submitted:
        if ticker_input:
            t = ticker_input.strip().upper()
            if not t.endswith(".JK") and not t.startswith("^"):
                t += ".JK"
            # Validate ticker first
            q = get_quote(t)
            if q.get("price", 0) > 0:
                add_to_watchlist(t, target_buy, target_sell)
                st.success(f"✅ **{t.replace('.JK', '')}** ({q.get('name', '')}) berhasil ditambahkan ke watchlist!")
                st.rerun()
            else:
                st.error(f"Kode saham **{t}** tidak ditemukan. Pastikan formatnya benar (contoh: BBRI.JK).")
        else:
            st.error("Silakan masukkan kode saham terlebih dahulu.")

st.divider()

# ── Menampilkan Watchlist ──
st.subheader(":material/checklist: Daftar Pantauan Anda")

watchlist = load_watchlist()

if not watchlist:
    st.info(":material/folder_open: Watchlist Anda masih kosong. Silakan tambah saham di atas.")
else:
    # Action buttons
    col_cek, col_test = st.columns([2, 2])
    with col_cek:
        run_alerts = st.button(":material/radar: Scan Semua Sinyal", type="primary", use_container_width=True)
    with col_test:
        if tg_ok:
            test_tg = st.button(":material/send: Tes Koneksi Telegram", use_container_width=True)
        else:
            test_tg = False
    
    # Handle Telegram test
    if test_tg:
        msg = f"🔔 <b>TEST KONEKSI</b>\n\nKoneksi Telegram Anda <b>berhasil</b>! ✅\n🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M WIB')}\n\nAnda akan menerima notifikasi dari Stock Analyst di sini."
        ok, err = send_telegram_message(msg)
        if ok:
            st.toast("✅ Tes berhasil! Cek Telegram Anda.")
        else:
            st.error(f"❌ Gagal: {err}")

    st.write("")
    
    all_alerts = {}  # ticker -> list of alert dicts
    
    for item in watchlist:
        t = item["ticker"]
        quote = get_quote(t)
        price = quote.get("price", 0)
        
        # ── Stock Card Row ──
        c1, c2, c3 = st.columns([3, 1.5, 0.5])
        
        with c1:
            logo = get_logo_html(t, size=36)
            name = quote.get("name", t.replace(".JK", ""))
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;">
                {logo}
                <div>
                    <h4 style="margin:0;">{t.replace('.JK', '')}</h4>
                    <p style="color:#888;margin:0;font-size:0.85rem;">{name}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            if price > 0:
                color = color_for_change(quote.get("pctChange", 0))
                pct = quote.get("pctChange", 0)
                st.markdown(f"""
                <div style="text-align:right;">
                    <div style="font-weight:700;font-size:1.15rem;">Rp{price:,.0f}</div>
                    <div style="color:{color};font-weight:600;">{pct:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#888;'>Data tidak tersedia</p>", unsafe_allow_html=True)
                
        with c3:
            if st.button("🗑️", key=f"del_{t}", help=f"Hapus {t.replace('.JK', '')} dari watchlist"):
                remove_from_watchlist(t)
                st.rerun()
                
        # ── Target Status ──
        if item.get("target_buy", 0) > 0 or item.get("target_sell", 0) > 0:
            target_parts = []
            tb = item.get("target_buy", 0)
            ts = item.get("target_sell", 0)
            if tb > 0:
                if price > 0 and price <= tb:
                    target_parts.append(f"🟢 <b style='color:#00d4aa;'>TERCAPAI: Target Beli Rp{tb:,.0f}</b>")
                else:
                    target_parts.append(f"Target Beli: Rp{tb:,.0f}")
            if ts > 0:
                if price > 0 and price >= ts:
                    target_parts.append(f"🔴 <b style='color:#ff4757;'>TERCAPAI: Target Jual Rp{ts:,.0f}</b>")
                else:
                    target_parts.append(f"Target Jual: Rp{ts:,.0f}")
                    
            st.markdown(f"<p style='color:#888;font-size:0.85rem;margin:4px 0 0 48px;'>{' &nbsp;|&nbsp; '.join(target_parts)}</p>", unsafe_allow_html=True)

        # ── Alert Results ──
        if run_alerts:
            with st.spinner(f"Scanning {t.replace('.JK', '')}..."):
                alerts = check_stock_alerts(t)
                
                # Add target price alerts
                tb = item.get("target_buy", 0)
                ts = item.get("target_sell", 0)
                if tb > 0 and price > 0 and price <= tb:
                    alerts.insert(0, {
                        "emoji": "🎯", "title": "Mencapai Target Beli",
                        "detail": f"Harga Rp{price:,.0f} ≤ Target Rp{tb:,.0f}",
                        "severity": "critical"
                    })
                if ts > 0 and price > 0 and price >= ts:
                    alerts.insert(0, {
                        "emoji": "🎯", "title": "Mencapai Target Jual",
                        "detail": f"Harga Rp{price:,.0f} ≥ Target Rp{ts:,.0f}",
                        "severity": "critical"
                    })
                
                if alerts:
                    all_alerts[t] = alerts
                    st.markdown(f"<div style='margin-left:48px;'>{format_alerts_html(alerts)}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#888;margin-left:48px;font-size:0.9rem;'>✅ Tidak ada sinyal khusus saat ini.</p>", unsafe_allow_html=True)
            
        st.divider()

    # ── Send Telegram ──
    if run_alerts:
        # Summary
        total_alerts = sum(len(v) for v in all_alerts.values())
        critical_count = sum(1 for v in all_alerts.values() for a in v if a["severity"] == "critical")
        
        if all_alerts:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid #00d4aa;">
                <h4 style="margin-top:0;">📊 Ringkasan Scan</h4>
                <p><b>{total_alerts}</b> sinyal terdeteksi dari <b>{len(all_alerts)}</b> saham ({critical_count} kritis)</p>
            </div>
            """, unsafe_allow_html=True)
            
            if tg_ok:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M WIB")
                msg = f"🔔 <b>STOCK ANALYST ALERT</b>\n🕒 {now}\n\n"
                msg += f"📊 {total_alerts} sinyal dari {len(all_alerts)} saham\n\n"
                
                for t, alerts in all_alerts.items():
                    msg += format_alerts_telegram(t, alerts)
                    msg += "\n\n"
                
                success, response_msg = send_telegram_message(msg)
                if success:
                    st.toast("✅ Notifikasi terkirim ke Telegram!")
                    st.success("📱 Pesan peringatan berhasil dikirim ke Telegram Anda.")
                else:
                    st.error(f"❌ Gagal mengirim Telegram: {response_msg}")
            else:
                st.info("💡 Konfigurasi Telegram di `.env` untuk menerima notifikasi otomatis.")
        else:
            st.success("✅ Semua saham dalam kondisi normal. Tidak ada sinyal khusus saat ini.")

show_disclosure()
