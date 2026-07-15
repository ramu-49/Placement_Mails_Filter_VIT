"""
Phase 4: Send alerts to Telegram.

Uses your bot token + chat ID to push a message to your phone via the
Telegram Bot API. No sandbox, no expiry, no per-user manual activation
beyond the one-time /start each person sends their own bot.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str) -> bool:
    """
    Sends a text message to your Telegram chat.
    Returns True if it succeeded, False otherwise (and prints why).
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. "
            "Check your .env file."
        )
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",  # lets us use <b>bold</b> etc. if we want later
    }

    response = requests.post(url, data=payload, timeout=10)

    if response.status_code == 200:
        return True
    else:
        print(f"Telegram send failed: {response.status_code} - {response.text}")
        return False


if __name__ == "__main__":
    # Quick manual test - sends one message to confirm everything is wired up
    success = send_telegram_message(
        "✅ Test alert from your Placement Agent. If you see this, the "
        "Telegram connection works!"
    )
    if success:
        print("Message sent successfully. Check your Telegram.")
    else:
        print("Message failed to send. See error above.")