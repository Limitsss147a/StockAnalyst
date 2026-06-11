"""Logo utilities for IDX companies – base64 data-URL encoding."""

import base64
import os
from pathlib import Path

LOGO_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"

# Domain mapping for top Indonesian companies
TICKER_DOMAINS = {
    "BBCA.JK": "bca.co.id",
    "BBRI.JK": "bri.co.id",
    "BMRI.JK": "bankmandiri.co.id",
    "BBNI.JK": "bni.co.id",
    "TLKM.JK": "telkom.co.id",
    "ASII.JK": "astra.co.id",
    "UNVR.JK": "unilever.co.id",
    "HMSP.JK": "sampoerna.com",
    "ICBP.JK": "icbp.indofood.com",
    "KLBF.JK": "kalbe.co.id",
    "SMGR.JK": "semenindonesia.com",
    "INDF.JK": "indofood.com",
    "GGRM.JK": "gudanggaramtbk.com",
    "ADRO.JK": "adaro.com",
    "PTBA.JK": "ptba.co.id",
    "ANTM.JK": "antam.com",
    "INCO.JK": "vale.com",
    "EXCL.JK": "xl.co.id",
    "ISAT.JK": "indosatooredoo.com",
    "TOWR.JK": "saranapratama.com",
    "TBIG.JK": "tbig.co.id",
    "PGAS.JK": "pgn.co.id",
    "AKRA.JK": "akra.co.id",
    "BSDE.JK": "bfrmdeveloper.com",
    "CTRA.JK": "ciputra.com",
    "GOTO.JK": "gotocompany.com",
    "BUKA.JK": "bukalapak.com",
    "EMTK.JK": "emtek.co.id",
    "SIDO.JK": "sidomunculdigital.com",
    "JSMR.JK": "jasamarga.com",
    "MAPI.JK": "map.co.id",
    "ERAA.JK": "erajayadigital.com",
    "BRPT.JK": "barito-pacific.com",
    "TPIA.JK": "chandraasniraya.com",
    "ITMG.JK": "itmg.co.id",
    "MEDC.JK": "medcoenergi.com",
    "SMRA.JK": "summararecon.com",
    "AUTO.JK": "component.astra.co.id",
    "MDKA.JK": "merdekagold.com",
    "ACES.JK": "acehardware.co.id",
}


def get_logo_path(ticker: str) -> Path | None:
    """Get local logo file path for a ticker."""
    if not LOGO_DIR.exists():
        return None
    for ext in (".png", ".svg", ".jpg", ".ico"):
        path = LOGO_DIR / f"{ticker.replace('.JK', '')}{ext}"
        if path.exists():
            return path
    return None


def get_logo_base64(ticker: str) -> str | None:
    """Get base64 data URL for a ticker logo."""
    path = get_logo_path(ticker)
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
        ext = path.suffix.lower()
        mime = {
            ".png": "image/png",
            ".svg": "image/svg+xml",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".ico": "image/x-icon",
        }.get(ext, "image/png")
        b64 = base64.b64encode(data).decode()
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None


def get_logo_html(ticker: str, size: int = 40) -> str:
    """Get HTML img tag for a ticker logo, or a colored placeholder."""
    b64 = get_logo_base64(ticker)
    if b64:
        return f'<img src="{b64}" width="{size}" height="{size}" style="border-radius:8px;object-fit:contain;" />'

    # Fallback: colored circle with first letter
    label = ticker.replace(".JK", "")[:2]
    # Generate a consistent color from ticker name
    hue = sum(ord(c) for c in ticker) % 360
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:8px;'
        f'background:hsl({hue},60%,40%);display:flex;align-items:center;'
        f'justify-content:center;font-weight:700;font-size:{size//3}px;'
        f'color:white;font-family:Inter,sans-serif;">{label}</div>'
    )
