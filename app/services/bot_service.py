from celery import shared_task
import requests
from config import WEBHOOK_URL


@shared_task
def send_newsletter_api(
        bot_user_id: int, text: str = None, inline_buttons=None, keyboard_buttons=None,
        location: dict = None
    ):
    """
    inline_buttons = [
        [{
            "text": <text of the button>,
            "url": <url> | "callback_data": <data> | "switch_inline_query": <query>
        }]
    ]
    """
    # get current host
    API_URL = f"{WEBHOOK_URL}/send-newsletter/"
    data = {
        "user_id": bot_user_id,
        "text": text,
        "inline_buttons": inline_buttons or [],
        "keyboard_buttons": keyboard_buttons or [],
        "location": location or None
    }
    requests.post(API_URL, json=data)