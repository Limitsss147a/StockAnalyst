"""👀 Watchlist – Pantauan saham & sistem notifikasi."""

from lib.config import setup_page, show_disclosure, GROQ_API_KEY
setup_page("Watchlist & Alert – Analis Saham")

import streamlit as st
import datetime
from lib.watchlist import load_watchlist, add_to_watchlist, remove_from_watchlist
from lib.market_data import get_quote, format_idr, color_for_change
from lib.logos import get_logo_html
from lib.alerts import check_stock_alerts, format_alerts_html, format_alerts_telegram
from lib.telegram_bot import is_telegram_configured, send_telegram_message

# ── Page-level custom CSS for watchlist cards ──
st.markdown("""
<style>
    /* ── Watchlist Stock Card ── */
    .wl-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.55) 0%, rgba(15, 23, 42, 0.4) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .wl-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    }
    .wl-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 212, 170, 0.15);
        border-color: rgba(0, 212, 170, 0.2);
    }

    /* ── Card Header: Logo + Name + Price ── */
    .wl-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        margin-bottom: 4px;
    }
    .wl-identity {
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
        flex: 1;
    }
    .wl-logo {
        flex-shrink: 0;
    }
    .wl-info {
        min-width: 0;
    }
    .wl-ticker {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .wl-name {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 2px 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 280px;
    }

    /* ── Price Section ── */
    .wl-price-section {
        text-align: right;
        flex-shrink: 0;
    }
    .wl-price {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .wl-change-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .wl-change-up {
        background: rgba(0, 230, 184, 0.12);
        color: #00e6b8;
        border: 1px solid rgba(0, 230, 184, 0.2);
    }
    .wl-change-down {
        background: rgba(255, 71, 87, 0.12);
        color: #ff6b7a;
        border: 1px solid rgba(255, 71, 87, 0.2);
    }
    .wl-change-neutral {
        background: rgba(148, 163, 184, 0.12);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .wl-no-data {
        color: #64748b;
        font-size: 0.85rem;
        font-style: italic;
    }

    /* ── Target Section ── */
    .wl-targets {
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    .wl-target-item {
        flex: 1;
        min-width: 180px;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .wl-target-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        margin: 0 0 6px;
        font-weight: 600;
    }
    .wl-target-value {
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 8px;
    }
    .wl-target-buy .wl-target-value { color: #00e6b8; }
    .wl-target-sell .wl-target-value { color: #f59e0b; }

    /* Progress bar */
    .wl-progress-track {
        width: 100%;
        height: 6px;
        background: rgba(255,255,255,0.06);
        border-radius: 3px;
        overflow: hidden;
        margin-top: 6px;
    }
    .wl-progress-fill-buy {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, #00d4aa, #00e6b8);
        transition: width 0.5s ease;
    }
    .wl-progress-fill-sell {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        transition: width 0.5s ease;
    }
    .wl-target-status {
        font-size: 0.72rem;
        margin-top: 6px;
        color: #94a3b8;
    }
    .wl-target-reached {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-top: 4px;
    }
    .wl-reached-buy {
        background: rgba(0, 212, 170, 0.15);
        color: #00e6b8;
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    .wl-reached-sell {
        background: rgba(255, 71, 87, 0.15);
        color: #ff6b7a;
        border: 1px solid rgba(255, 71, 87, 0.3);
    }

    /* ── Summary Stats ── */
    .wl-summary {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .wl-stat {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.35) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 14px 20px;
        flex: 1;
        min-width: 120px;
        text-align: center;
    }
    .wl-stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .wl-stat-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #64748b;
        margin: 4px 0 0;
        font-weight: 500;
    }
    .wl-stat-accent { border-bottom: 2px solid #00d4aa; }
    .wl-stat-warn { border-bottom: 2px solid #f59e0b; }
    .wl-stat-danger { border-bottom: 2px solid #ff4757; }

    /* ── Empty State ── */
    .wl-empty {
        text-align: center;
        padding: 48px 24px;
        color: #64748b;
    }
    .wl-empty-icon {
        font-size: 3rem;
        margin-bottom: 12px;
        opacity: 0.5;
    }
    .wl-empty-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #94a3b8;
        margin: 0 0 6px;
    }
    .wl-empty-desc {
        font-size: 0.85rem;
        color: #64748b;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="wl-empty"><div class="wl-empty-icon">📂</div><p class="wl-empty-title">Watchlist Anda Masih Kosong</p><p class="wl-empty-desc">Tambahkan saham di form di atas untuk mulai memantau harga &amp; sinyal secara otomatis.</p></div>', unsafe_allow_html=True)
else:
    # ── Gather all data first ──
    stock_data = []
    count_up = 0
    count_down = 0
    count_target_reached = 0
    
    for item in watchlist:
        t = item["ticker"]
        quote = get_quote(t)
        price = quote.get("price", 0)
        pct = quote.get("pctChange", 0)
        name = quote.get("name", t.replace(".JK", ""))
        
        if pct > 0: count_up += 1
        elif pct < 0: count_down += 1
        
        tb = item.get("target_buy", 0)
        ts = item.get("target_sell", 0)
        buy_reached = tb > 0 and price > 0 and price <= tb
        sell_reached = ts > 0 and price > 0 and price >= ts
        if buy_reached or sell_reached:
            count_target_reached += 1
        
        stock_data.append({
            "item": item, "ticker": t, "quote": quote,
            "price": price, "pct": pct, "name": name,
            "tb": tb, "ts": ts,
            "buy_reached": buy_reached, "sell_reached": sell_reached,
        })
    
    # ── Summary Stats Bar ──
    summary_html = f'<div class="wl-summary"><div class="wl-stat wl-stat-accent"><p class="wl-stat-value">{len(watchlist)}</p><p class="wl-stat-label">Saham Dipantau</p></div><div class="wl-stat wl-stat-accent"><p class="wl-stat-value" style="color:#00e6b8;">{count_up}</p><p class="wl-stat-label">Sedang Naik ↑</p></div><div class="wl-stat wl-stat-danger"><p class="wl-stat-value" style="color:#ff6b7a;">{count_down}</p><p class="wl-stat-label">Sedang Turun ↓</p></div><div class="wl-stat wl-stat-warn"><p class="wl-stat-value" style="color:#fbbf24;">{count_target_reached}</p><p class="wl-stat-label">Target Tercapai 🎯</p></div></div>'
    st.markdown(summary_html, unsafe_allow_html=True)

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
    
    for sd in stock_data:
        t = sd["ticker"]
        item = sd["item"]
        price = sd["price"]
        pct = sd["pct"]
        name = sd["name"]
        tb = sd["tb"]
        ts = sd["ts"]
        buy_reached = sd["buy_reached"]
        sell_reached = sd["sell_reached"]
        quote = sd["quote"]
        
        logo = get_logo_html(t, size=42)
        
        # ── Change badge class ──
        if pct > 0:
            badge_cls = "wl-change-up"
            arrow = "▲"
        elif pct < 0:
            badge_cls = "wl-change-down"
            arrow = "▼"
        else:
            badge_cls = "wl-change-neutral"
            arrow = "—"
        
        # ── Target HTML ──
        target_html = ""
        if tb > 0 or ts > 0:
            target_html = '<div class="wl-targets">'
            
            if tb > 0:
                if buy_reached:
                    target_html += f'<div class="wl-target-item wl-target-buy"><p class="wl-target-label">🎯 Target Beli</p><p class="wl-target-value">Rp{tb:,.0f}</p><div class="wl-target-reached wl-reached-buy">✅ Tercapai! Harga sudah di bawah target</div></div>'
                else:
                    if price > 0 and price > tb:
                        diff_pct = ((price - tb) / price) * 100
                        progress = max(0, min(100, 100 - diff_pct * 3))
                        status_text = f"Harga saat ini {diff_pct:.1f}% di atas target"
                    else:
                        progress = 0
                        status_text = "Menunggu data harga"
                    target_html += f'<div class="wl-target-item wl-target-buy"><p class="wl-target-label">🎯 Target Beli</p><p class="wl-target-value">Rp{tb:,.0f}</p><div class="wl-progress-track"><div class="wl-progress-fill-buy" style="width:{progress:.0f}%"></div></div><p class="wl-target-status">{status_text}</p></div>'
            
            if ts > 0:
                if sell_reached:
                    target_html += f'<div class="wl-target-item wl-target-sell"><p class="wl-target-label">💰 Target Jual</p><p class="wl-target-value">Rp{ts:,.0f}</p><div class="wl-target-reached wl-reached-sell">🔔 Tercapai! Harga sudah di atas target</div></div>'
                else:
                    if price > 0 and ts > price:
                        progress_sell = max(0, min(100, (price / ts) * 100))
                        diff_sell = ((ts - price) / price) * 100
                        status_text_sell = f"Masih {diff_sell:.1f}% menuju target"
                    else:
                        progress_sell = 0
                        status_text_sell = "Menunggu data harga"
                    target_html += f'<div class="wl-target-item wl-target-sell"><p class="wl-target-label">💰 Target Jual</p><p class="wl-target-value">Rp{ts:,.0f}</p><div class="wl-progress-track"><div class="wl-progress-fill-sell" style="width:{progress_sell:.0f}%"></div></div><p class="wl-target-status">{status_text_sell}</p></div>'
            
            target_html += '</div>'

        
        # ── Price display ──
        if price > 0:
            price_html = f'<div class="wl-price-section"><p class="wl-price">Rp{price:,.0f}</p><span class="wl-change-badge {badge_cls}">{arrow} {pct:+.2f}%</span></div>'
        else:
            price_html = '<div class="wl-price-section"><span class="wl-no-data">Data tidak tersedia</span></div>'
        
        # ── Render the card ──
        card_html = f'<div class="wl-card"><div class="wl-header"><div class="wl-identity"><div class="wl-logo">{logo}</div><div class="wl-info"><p class="wl-ticker">{t.replace(".JK", "")}</p><p class="wl-name">{name}</p></div></div>{price_html}</div>{target_html}</div>'
        st.markdown(card_html, unsafe_allow_html=True)
        
        # ── Action row: Delete + AI ──
        col_ai, col_del = st.columns([5, 1])
        with col_del:
            if st.button("🗑️ Hapus", key=f"del_{t}", help=f"Hapus {t.replace('.JK', '')} dari watchlist", use_container_width=True):
                remove_from_watchlist(t)
                st.rerun()

        # ── AI Analysis Expander ──
        with st.expander(f"🤖 Analisis Sinyal AI — {t.replace('.JK', '')}"):
            st.caption("Klik tombol di bawah untuk memindai sinyal teknikal dan mendapatkan rekomendasi strategi dari AI.")
            if st.button(f":material/smart_toy: Generate Strategi AI", key=f"ai_btn_{t}", use_container_width=True):
                with st.spinner("Memproses sinyal dan menganalisis..."):
                    from lib.groq_analyst import alert_analysis
                    alerts = check_stock_alerts(t)
                    
                    # Add target price alerts
                    if tb > 0 and price > 0 and price <= tb:
                        alerts.insert(0, {
                            "emoji": "🎯", "title": "Mencapai Target Beli",
                            "detail": f"Harga Rp{price:,.0f} ≤ Target Rp{tb:,.0f}",
                            "severity": "critical",
                            "sentiment": "strong_bullish"
                        })
                    if ts > 0 and price > 0 and price >= ts:
                        alerts.insert(0, {
                            "emoji": "🎯", "title": "Mencapai Target Jual",
                            "detail": f"Harga Rp{price:,.0f} ≥ Target Rp{ts:,.0f}",
                            "severity": "critical",
                            "sentiment": "strong_bearish"
                        })
                    
                    if not alerts:
                        st.success("✅ Tidak ada sinyal khusus saat ini. Saham dalam kondisi stabil.")
                    else:
                        st.markdown("**Sinyal Terdeteksi:**")
                        st.markdown(format_alerts_html(alerts), unsafe_allow_html=True)
                        
                        if not GROQ_API_KEY:
                            st.warning("⚠️ GROQ_API_KEY belum diset. Tambahkan ke file `.env` untuk analisis AI.")
                        else:
                            st.markdown("---")
                            st.markdown("**Analisis Strategi AI:**")
                            res = alert_analysis(t, name, price, alerts)
                            st.info(res)

        # ── Alert Results ──
        if run_alerts:
            with st.spinner(f"Scanning {t.replace('.JK', '')}..."):
                alerts = check_stock_alerts(t)
                
                # Add target price alerts
                if tb > 0 and price > 0 and price <= tb:
                    alerts.insert(0, {
                        "emoji": "🎯", "title": "Mencapai Target Beli",
                        "detail": f"Harga Rp{price:,.0f} ≤ Target Rp{tb:,.0f}",
                        "severity": "critical",
                        "sentiment": "strong_bullish"
                    })
                if ts > 0 and price > 0 and price >= ts:
                    alerts.insert(0, {
                        "emoji": "🎯", "title": "Mencapai Target Jual",
                        "detail": f"Harga Rp{price:,.0f} ≥ Target Rp{ts:,.0f}",
                        "severity": "critical",
                        "sentiment": "strong_bearish"
                    })
                
                if alerts:
                    all_alerts[t] = alerts
                    st.markdown(format_alerts_html(alerts), unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#94a3b8;font-size:0.9rem;'>✅ Tidak ada sinyal khusus saat ini.</p>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 24px 0 32px 0; border: none; border-top: 1px dashed rgba(255,255,255,0.1);' />", unsafe_allow_html=True)

    # ── Send Telegram ──
    if run_alerts:
        # Summary
        total_alerts = sum(len(v) for v in all_alerts.values())
        critical_count = sum(1 for v in all_alerts.values() for a in v if a["severity"] == "critical")
        
        if all_alerts:
            st.markdown(f'<div class="metric-card" style="border-left:4px solid #00d4aa;"><h4 style="margin-top:0;">📊 Ringkasan Scan</h4><p><b>{total_alerts}</b> sinyal terdeteksi dari <b>{len(all_alerts)}</b> saham ({critical_count} kritis)</p></div>', unsafe_allow_html=True)
            
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
