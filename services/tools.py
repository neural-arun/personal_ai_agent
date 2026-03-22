import os
import requests
import time
import logging
import csv
from pathlib import Path

logger = logging.getLogger(__name__)


def push(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning("Telegram credentials missing. Skipping push.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    for attempt in range(3):
        try:
            r = requests.post(url, data=payload, timeout=10)
            r.raise_for_status()
            return
        except Exception as e:
            logger.warning(f"Push attempt {attempt + 1} failed: {e}")
            time.sleep(1)


def save_user_details(
    name: str = "not provided",
    email: str = "not provided",
    phone: str = "not provided",
    linkedin: str = "not provided",
    twitter: str = "not provided",
    instagram: str = "not provided",
    notes: str = "not provided",
) -> dict:
    lines = [
        "<b>🔔 New Lead!</b>",
        f"<b>Name:</b> {name}",
        f"<b>Email:</b> {email}",
        f"<b>Phone:</b> {phone}",
        f"<b>LinkedIn:</b> {linkedin}",
        f"<b>Twitter:</b> {twitter}",
        f"<b>Instagram:</b> {instagram}",
        f"<b>Notes:</b> {notes}",
    ]

    push("\n".join(lines))
    
    # Save lead locally
    try:
        csv_file = Path("leads.csv")
        file_exists = csv_file.exists()
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Time", "Name", "Email", "Phone", "LinkedIn", "Twitter", "Instagram", "Notes"])
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), name, email, phone, linkedin, twitter, instagram, notes])
    except Exception as e:
        logger.error(f"Failed to save lead to CSV: {e}")

    logger.info(f"Lead saved: {name} | {email}")
    return {"recorded": "ok"}


def save_unknown_questions(question: str) -> dict:
    push(f"<b>❓ Unknown Question:</b>\n{question}")
    logger.info(f"Unknown question logged: {question}")
    return {"recorded": "ok"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "save_user_details",
            "description": "Save contact details when user shows interest.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "linkedin": {"type": "string"},
                    "twitter": {"type": "string"},
                    "instagram": {"type": "string"},
                    "notes": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_unknown_questions",
            "description": "Log unknown questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    },
]


TOOL_MAP = {
    "save_user_details": save_user_details,
    "save_unknown_questions": save_unknown_questions,
}