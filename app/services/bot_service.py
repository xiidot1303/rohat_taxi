from celery import shared_task
import requests
from config import NEWSLETTER_URL, ADMIN_USER_ID
import html
import traceback


@shared_task
def send_newsletter_api(
        bot_user_id: int, text: str = None, inline_buttons=None, keyboard_buttons=None, keyboard_remove: bool = False,
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
    API_URL = f"{NEWSLETTER_URL}/send-newsletter/"
    data = {
        "user_id": bot_user_id,
        "text": text,
        "inline_buttons": inline_buttons or [],
        "keyboard_buttons": keyboard_buttons or [],
        "keyboard_remove": keyboard_remove,
        "location": location or None
    }
    requests.post(API_URL, json=data)


def send_exception_to_admin(heading: str, exc: Exception, **kwargs):
    message = heading + "\n"
    for key, value in kwargs.items():
        message += f"<pre>{key}: {html.escape(str(value))}</pre>\n"
    
    tb_list = traceback.format_exception(
        None, exc, exc.__traceback__)
    tb_string = "".join(tb_list)

    error_message = f"<pre>{html.escape(tb_string)}</pre>"

    send_newsletter_api.delay(
        bot_user_id=ADMIN_USER_ID,
        text=message
    )

    send_newsletter_api.delay(
        bot_user_id=ADMIN_USER_ID,
        text=error_message,
    )