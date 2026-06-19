import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def is_telegram_configured():
    """Check if Telegram bot credentials are set."""
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

def send_telegram_message(message: str, parse_mode="HTML"):
    """
    Send a message via Telegram Bot.
    Returns (success: bool, error_msg: str)
    """
    if not is_telegram_configured():
        return False, "Telegram token atau Chat ID belum dikonfigurasi di file .env"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Sukses dikirim"
        else:
            err = response.json().get("description", "Unknown error")
            return False, f"Gagal mengirim pesan: {err}"
    except Exception as e:
        return False, f"Error koneksi ke Telegram: {str(e)}"
