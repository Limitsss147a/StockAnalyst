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
