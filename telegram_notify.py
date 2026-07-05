import os

import requests
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramNotificationError(Exception):
    pass


def _get_config():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise TelegramNotificationError("TELEGRAM_BOT_TOKEN is not set.")

    if not chat_id:
        raise TelegramNotificationError("TELEGRAM_CHAT_ID is not set.")

    return bot_token, chat_id


def format_activity_message(activity: dict) -> str:
    distance_km = activity.get("distance", 0) / 1000
    name = activity.get("name", "Unnamed activity")
    activity_type = activity.get("type", "Activity")
    start_date = activity.get("start_date_local") or activity.get("start_date", "Unknown date")
    strava_id = activity.get("id", "unknown")

    return (
        "New commute activity\n"
        f"Name: {name}\n"
        f"Type: {activity_type}\n"
        f"Date: {start_date}\n"
        f"Distance: {distance_km:.2f} km\n"
        f"Strava ID: {strava_id}"
    )


def send_telegram_message(message: str) -> bool:
    bot_token, chat_id = _get_config()

    response = requests.post(
        f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=10,
    )

    if response.status_code == 200:
        return True

    raise TelegramNotificationError(
        f"Telegram send failed: {response.status_code} - {response.text}"
    )


def send_activity_notification(activity: dict) -> bool:
    return send_telegram_message(format_activity_message(activity))
