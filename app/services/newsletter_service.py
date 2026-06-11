from bot.services import get_user_by_phone
from bot.services import string_service
from bot import Strings
from app.services.order_service import (
    get_order_by_uuid_without_404,
    get_order_by_order_id_without_404,
)
import json
from app.services.bot_service import send_newsletter_api
from app.services import scat_service
from asgiref.sync import async_to_sync, sync_to_async
from app.utils import *
from config import WEBAPP_URL


def send_cheque(phone, order_id, uuid):
    if user := get_user_by_phone(phone):
        order_obj = get_order_by_order_id_without_404(order_id)
        order: dict = async_to_sync(scat_service.order_info)(uuid)
        src = order_obj.src_street if order_obj else ""
        dst = order_obj.dst_street if order_obj else ""
        starttime = order.get("start_time", "")
        endtime = datetime.now().strftime("%H:%M")
        executor_id = order.get("driver_id")
        amount = order.get("amount", "")
        street = order_obj.src_street if order_obj else ""
        house = order_obj.src_house if order_obj else ""
        dststreet = order_obj.dst_street if order_obj else ""
        dsthouse = order_obj.dst_house if order_obj else ""

        # get car info
        autonum = order.get("car_number", "")
        color = order.get("car_color", "")
        brand = order.get("car_brand", "")
        model = order.get("car_model", "")

        text = string_service.cheque_info(
            user.user_id,
            src,
            dst,
            starttime,
            endtime,
            amount,
            street,
            house,
            dststreet,
            dsthouse,
            autonum,
            color,
            brand,
            model,
        )
        markup = []
        if order_obj:
            markup = [
                [
                    {
                        "text": Strings(user_id=user.user_id).main_menu,
                        "callback_data": "main_menu",
                    }
                ]
            ]

        markup.append(
            [
                {
                    "text": Strings(user_id=user.user_id).leave_feedback,
                    "web_app": {
                        "url": f"{WEBAPP_URL}/feedback/{order_id}/{user.get_lang_display()}"
                    },
                }
            ]
        )
        send_newsletter_api(user.user_id, text, inline_buttons=markup)
        return True
    else:
        return False


def send_order_status(phone, data):
    status_code = int(data["status_code"])
    if user := get_user_by_phone(phone):
        order = get_order_by_order_id_without_404(data["id"])
        markup = None
        keyboard_remove = False
        if status_code == 80:
            text = Strings(user_id=user.user_id).your_order_is_in_moderation

        elif status_code == 95:
            text = Strings(user_id=user.user_id).your_order_is_cancelled
            markup = [
                [
                    {
                        "text": Strings(user_id=user.user_id).main_menu,
                        "callback_data": "main_menu",
                    }
                ]
            ]
        elif status_code == 10:
            text = string_service.car_info_string(
                user.user_id,
                data["remaining"],
                data["car_phone"],
                data["car_firstname"],
                data["brand"],
                data["model"],
                data["color"],
                data["autonum"],
            )
        elif status_code == 11:
            text = Strings(user_id=user.user_id).driver_is_here
        elif status_code == 4:
            text = Strings(user_id=user.user_id).order_is_in_execution
            keyboard_remove = True

        if not order:
            markup = None
        send_newsletter_api(
            user.user_id, text, inline_buttons=markup, keyboard_remove=keyboard_remove
        )
        return True
    else:
        return False
