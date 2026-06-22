"""Groq API wrapper for AI-powered analysis (replaces Claude/Anthropic)."""

import os
from lib.config import GROQ_API_KEY, GROQ_MODEL


def _get_client():
    """Lazy-init Groq client."""
    try:
        from groq import Groq
        key = GROQ_API_KEY
        if not key:
            return None
        return Groq(api_key=key)
    except ImportError:
        return None


def _call(system_prompt: str, user_prompt: str, temperature=0.7, max_tokens=2000) -> str:
    """Make a single Groq chat completion call."""
    client = _get_client()
    if not client:
        return "⚠️ Groq API tidak tersedia. Pastikan GROQ_API_KEY sudah diset di file .env."
    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error dari Groq API: {str(e)}"


SYSTEM_ANALYST = (
    "Kamu adalah analis pasar saham Indonesia yang berpengalaman. "
    "Berikan analisis dalam Bahasa Indonesia yang mudah dipahami. "
    "JANGAN memberikan rekomendasi beli/jual secara eksplisit. "
    "Gunakan bahasa netral dan edukatif. Fokus pada fakta dan data. "
    "Format jawaban dengan markdown yang rapi."
)


def bull_bear_case(ticker: str, name: str, fundamentals: dict, price_data: dict) -> str:
    """Generate bull and bear case analysis."""
    prompt = f"""Analisis saham {ticker} ({name}) dari Bursa Efek Indonesia.

Data Fundamental:
- P/E Ratio: {fundamentals.get('trailingPE', 'N/A')}
- P/B Ratio: {fundamentals.get('priceToBook', 'N/A')}
- ROE: {fundamentals.get('returnOnEquity', 'N/A')}
- Margin Laba: {fundamentals.get('profitMargins', 'N/A')}
- D/E Ratio: {fundamentals.get('debtToEquity', 'N/A')}
- Revenue Growth: {fundamentals.get('revenueGrowth', 'N/A')}
- Sektor: {fundamentals.get('sector', 'N/A')}
- Industri: {fundamentals.get('industry', 'N/A')}

Data Harga:
- Harga Terakhir: {price_data.get('price', 'N/A')}
- Perubahan: {price_data.get('pctChange', 'N/A')}%
- Market Cap: {price_data.get('marketCap', 'N/A')}

Berikan analisis Bull Case dan Bear Case:
1. **🐂 Bull Case** - 3-4 poin argumen positif/kekuatan
2. **🐻 Bear Case** - 3-4 poin risiko/kelemahan

Ingat: JANGAN berikan rekomendasi beli/jual. Fokus pada fakta dan analisis objektif."""

    return _call(SYSTEM_ANALYST, prompt)


def deep_analysis(ticker: str, name: str, fundamentals: dict, price_data: dict) -> str:
    """Generate comprehensive deep analysis."""
    prompt = f"""Lakukan analisis mendalam untuk saham {ticker} ({name}) dari Bursa Efek Indonesia.

Data Fundamental:
- P/E: {fundamentals.get('trailingPE', 'N/A')} | Forward P/E: {fundamentals.get('forwardPE', 'N/A')}
- P/B: {fundamentals.get('priceToBook', 'N/A')}
- ROE: {fundamentals.get('returnOnEquity', 'N/A')} | ROA: {fundamentals.get('returnOnAssets', 'N/A')}
- Gross Margin: {fundamentals.get('grossMargins', 'N/A')}
- Operating Margin: {fundamentals.get('operatingMargins', 'N/A')}
- Net Margin: {fundamentals.get('profitMargins', 'N/A')}
- D/E: {fundamentals.get('debtToEquity', 'N/A')}
- Current Ratio: {fundamentals.get('currentRatio', 'N/A')}
- Revenue Growth: {fundamentals.get('revenueGrowth', 'N/A')}
- Earnings Growth: {fundamentals.get('earningsGrowth', 'N/A')}
- Beta: {fundamentals.get('beta', 'N/A')}
- Dividend Yield: {fundamentals.get('dividendYield', 'N/A')}
- Sektor: {fundamentals.get('sector', 'N/A')}
- Industri: {fundamentals.get('industry', 'N/A')}
- Deskripsi: {(fundamentals.get('longBusinessSummary') or 'N/A')[:500]}

Data Harga: Rp{price_data.get('price', 0):,.0f} | MCap: {price_data.get('marketCap', 'N/A')}

Berikan analisis mendalam meliputi:
1. **📊 Ringkasan Bisnis** - Model bisnis dan posisi di industri
2. **💰 Analisis Keuangan** - Profitabilitas, leverage, likuiditas
3. **📈 Analisis Valuasi** - Apakah valuasi masuk akal relatif terhadap peers
4. **⚡ Katalis & Risiko** - Faktor yang bisa mempengaruhi kinerja
5. **🏭 Posisi Kompetitif** - Keunggulan/kelemahan vs kompetitor

JANGAN memberikan rekomendasi beli/jual. Analisis ini hanya untuk edukasi."""

    return _call(SYSTEM_ANALYST, prompt, max_tokens=3000)


def macro_pulse(indicators: dict) -> str:
    """Generate macro economic pulse check for Indonesia."""
    prompt = f"""Berikan analisis kondisi makroekonomi Indonesia terkini berdasarkan data berikut:

{chr(10).join(f'- {k}: {v}' for k, v in indicators.items())}

Analisis meliputi:
1. **🏦 Kebijakan Moneter** - Suku bunga BI dan implikasinya
2. **💹 Kondisi Pasar** - IHSG dan sentimen pasar
3. **💱 Nilai Tukar** - Pergerakan Rupiah
4. **📊 Inflasi & Pertumbuhan** - Tren inflasi dan GDP
5. **🔮 Outlook** - Faktor-faktor yang perlu diperhatikan ke depan

JANGAN berikan rekomendasi investasi. Fokus pada analisis objektif."""

    return _call(SYSTEM_ANALYST, prompt, max_tokens=2000)


def portfolio_analysis(holdings: list, total_value: float, total_return: float) -> str:
    """Analyze a portfolio composition."""
    holdings_str = "\n".join(
        f"- {h['ticker']}: {h.get('shares', 0)} lembar @ Rp{h.get('avg_price', 0):,.0f} "
        f"(nilai: Rp{h.get('current_value', 0):,.0f}, return: {h.get('return_pct', 0):+.1f}%)"
        for h in holdings
    )

    prompt = f"""Analisis komposisi portofolio saham Indonesia berikut:

{holdings_str}

Total Nilai: Rp{total_value:,.0f}
Total Return: {total_return:+.1f}%

Berikan analisis:
1. **📊 Diversifikasi** - Apakah portofolio terdiversifikasi dengan baik?
2. **⚖️ Konsentrasi** - Apakah ada risiko konsentrasi berlebihan?
3. **🏭 Eksposur Sektor** - Sektor apa saja yang terwakili?
4. **📈 Kinerja** - Observasi tentang kinerja keseluruhan
5. **💡 Pertimbangan** - Hal-hal yang perlu diperhatikan

JANGAN berikan rekomendasi beli/jual spesifik."""

    return _call(SYSTEM_ANALYST, prompt, max_tokens=2000)


def timeframe_analysis(ticker: str, name: str, timeframe: str,
                       report: dict, fundamentals: dict) -> str:
    """Generate AI analysis specific to a trading timeframe."""
    signals_str = "\n".join(
        f"- [{s['type'].upper()}] {s['name']}: {s['detail']}"
        for s in report.get("signals", [])
    )
    vals = report.get("values", {})
    levels = report.get("levels", {})
    config = report.get("config", {})

    timeframe_desc = {
        "Day Trade": "day trading (intraday, hitungan jam)",
        "Swing Trade": "swing trading (beberapa hari sampai minggu)",
        "Long Term": "investasi jangka panjang (bulan sampai tahun)",
    }.get(timeframe, timeframe)

    prompt = f"""Kamu diminta menganalisis saham {ticker} ({name}) dari perspektif **{timeframe_desc}**.

## Sinyal Terdeteksi:
{signals_str}

## Data Teknikal:
- Harga: Rp{vals.get('price', 0):,.0f}
- RSI({config.get('rsi_period', 14)}): {vals.get('rsi', 0):.1f}
- MACD Histogram: {vals.get('macd_hist', 0):,.0f}
- SMA-Fast({config.get('sma_fast', 0)}): Rp{vals.get('sma_fast', 0):,.0f}
- SMA-Slow({config.get('sma_slow', 0)}): Rp{vals.get('sma_slow', 0):,.0f}
- Bollinger: Lower Rp{vals.get('bb_lower', 0):,.0f} – Upper Rp{vals.get('bb_upper', 0):,.0f}
- Stochastic: %K={vals.get('stoch_k', 0):.0f}, %D={vals.get('stoch_d', 0):.0f}
- ATR: Rp{vals.get('atr', 0):,.0f}
- Volume vs Avg: {vals.get('volume_last', 0) / max(vals.get('volume_avg', 1), 1):.1f}x

## Level Penting:
- Support 1: Rp{levels.get('support_1', 0):,.0f}
- Support 2: Rp{levels.get('support_2', 0):,.0f}
- Resistance: Rp{levels.get('resistance_1', 0):,.0f}

## Sinyal Keseluruhan: {report.get('overall_signal', 'N/A')} (Confidence: {report.get('confidence', 0)}%)

Berikan analisis dalam konteks **{timeframe_desc}** meliputi:
1. **📊 Kondisi Teknikal** – Interpretasi sinyal-sinyal di atas untuk timeframe ini
2. **📈 Tren & Momentum** – Arah tren dan kekuatan momentum saat ini
3. **📐 Level Penting** – Area support/resistance yang perlu diperhatikan
4. **⚡ Skenario** – 2 skenario yang mungkin terjadi (positif dan negatif)
5. **⚠️ Risiko** – Faktor risiko spesifik untuk timeframe {timeframe_desc}

INGAT: JANGAN berikan rekomendasi beli/jual. Analisis ini hanya untuk edukasi.
Gunakan Bahasa Indonesia yang mudah dipahami."""

    return _call(SYSTEM_ANALYST, prompt, max_tokens=2500)


def alert_analysis(ticker: str, name: str, price: float, alerts: list) -> str:
    """Generate AI analysis and strategies based on triggered alerts."""
    alerts_str = "\n".join(
        f"- [{a.get('severity', 'info').upper()}] {a.get('title')}: {a.get('detail')}"
        for a in alerts
    )
    
    prompt = f"""Saham {ticker} ({name}) saat ini berada di harga Rp{price:,.0f} dan telah memicu beberapa peringatan (alert) dari sistem pemantauan.

## Sinyal & Peringatan Terdeteksi:
{alerts_str}

Berikan analisis komprehensif berdasarkan sinyal-sinyal di atas, meliputi:
1. **🔍 Interpretasi Sinyal** – Apa arti dari kumpulan sinyal tersebut dalam kondisi pasar saat ini?
2. **⚖️ Pro & Kontra** – Faktor pendukung vs penekan pergerakan harga berdasarkan sinyal yang ada.
3. **🎯 Skenario Pergerakan** – Potensi pergerakan harga selanjutnya (skenario naik vs turun).
4. **💡 Saran & Strategi Edukatif** – Strategi manajemen risiko dan opsi tindakan (misal: "wait and see", "pertimbangkan trailing stop", dsb).

PENTING:
- JANGAN berikan rekomendasi beli/jual secara eksplisit (misal: "Beli sekarang").
- Fokus pada pendekatan manajemen risiko dan strategi trading yang objektif.
- Gunakan bahasa Indonesia yang mudah dipahami.
"""
    return _call(SYSTEM_ANALYST, prompt, max_tokens=2000)
def bandarmology_analysis(ticker: str, name: str, bandar_report: dict,
                          tech_report: dict, timeframe: str) -> str:
    """Generate AI analysis for bandarmology (big money tracking)."""
    signals_str = "\n".join(
        f"- [{s['type'].upper()}] {s['name']}: {s['detail']}"
        for s in bandar_report.get("signals", [])
    )
    vals = bandar_report.get("values", {})
    big_money = bandar_report.get("big_money", {})
    tech_vals = tech_report.get("values", {}) if tech_report else {}

    prompt = f"""Kamu diminta menganalisis pergerakan **Big Money (Bandarmologi)** untuk saham {ticker} ({name}).

## Status Bandar:
- Overall: {bandar_report.get('overall', 'N/A')}
- Confidence: {bandar_report.get('confidence', 0)}%
- Bandar Score: {vals.get('bandar_score', 0):+.0f}

## Sinyal Bandarmologi Terdeteksi:
{signals_str}

## Data Money Flow:
- Money Flow Index (MFI): {vals.get('mfi', 0):.1f}
- Chaikin Money Flow (CMF): {vals.get('cmf', 0):.3f}
- Force Index: {vals.get('force_index', 0):,.0f}
- OBV vs SMA: {'Di atas' if vals.get('obv', 0) > vals.get('obv_sma', 0) else 'Di bawah'}

## Aktivitas Big Money:
- Total Hari Volume Besar: {big_money.get('big_vol_days_total', 0)}
- Hari Akumulasi: {big_money.get('accumulation_days', 0)}
- Hari Distribusi: {big_money.get('distribution_days', 0)}
- Akumulasi Baru-baru ini (10 bar): {big_money.get('recent_accum', 0)}
- Distribusi Baru-baru ini (10 bar): {big_money.get('recent_distrib', 0)}

## Data Teknikal Pendukung:
- Harga: Rp{tech_vals.get('price', 0):,.0f}
- RSI: {tech_vals.get('rsi', 0):.1f}
- Volume vs Avg: {vals.get('volume_last', 0) / max(vals.get('volume_avg_20', 1), 1):.1f}x

Berikan analisis **Bandarmologi** meliputi:
1. **🏦 Profil Bandar** – Apakah bandar sedang akumulasi, distribusi, atau menunggu?
2. **📊 Analisis Money Flow** – Interpretasi arus uang besar berdasarkan indikator
3. **🔍 Pola Pergerakan** – Pola yang terdeteksi (silent accumulation, dump, pump, distribusi tersembunyi)
4. **⚡ Potensi Pergerakan** – Berdasarkan pola bandar, apa yang mungkin terjadi selanjutnya?
5. **⚠️ Peringatan** – Red flags atau hal yang perlu diwaspadai

PENTING:
- Jelaskan dalam konteks pasar saham Indonesia
- Gunakan istilah bandarmologi yang umum (akumulasi, distribusi, markup, markdown)
- JANGAN berikan rekomendasi beli/jual
- Analisis ini hanya untuk edukasi

Gunakan Bahasa Indonesia yang mudah dipahami."""

    return _call(SYSTEM_ANALYST, prompt, max_tokens=2500)

