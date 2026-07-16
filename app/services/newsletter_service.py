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
from config import ADMIN_GROUP_ID, WEBAPP_URL
from app.models import Cheque, Order, OrderRating, OrderReview, Feedback
from celery import shared_task


def _get_bot_user_from_order_feedback(feedback):
    if feedback.user:
        return feedback.user

    if not feedback.cheque or not feedback.cheque.phonenum:
        return None

    return get_user_by_phone(feedback.cheque.phonenum)


def send_order_rating_to_admin_group(order_rating: OrderRating):
    if not ADMIN_GROUP_ID:
        return False

    bot_user = _get_bot_user_from_order_feedback(order_rating)
    text = string_service.order_rating_admin_notification(order_rating, bot_user)
    send_newsletter_api.delay(ADMIN_GROUP_ID, text)
    return True


def send_order_review_to_admin_group(order_review: OrderReview):
    if not ADMIN_GROUP_ID:
        return False

    bot_user = _get_bot_user_from_order_feedback(order_review)
    text = string_service.order_review_admin_notification(order_review, bot_user)
    send_newsletter_api.delay(ADMIN_GROUP_ID, text)
    return True


def send_feedback_to_admin_group(feedback: Feedback):
    if not ADMIN_GROUP_ID:
        return False

    bot_user = feedback.bot_user
    text = string_service.feedback_admin_notification(feedback, bot_user)
    send_newsletter_api.delay(ADMIN_GROUP_ID, text)
    return True


@shared_task
def send_cheque(phone, cheque_id: int):
    if user := get_user_by_phone(phone):
        cheque = Cheque.objects.get(id=cheque_id)
        order_obj: Order | None = get_order_by_order_id_without_404(cheque.id)
        # order: dict = async_to_sync(scat_service.order_info)(uuid)
        src = order_obj.src_street if order_obj else ""
        dst = order_obj.dst_street if order_obj else ""
        starttime = order_obj.start_time.strftime("%H:%M") if order_obj else ""
        endtime = datetime.now().strftime("%H:%M")
        # executor_id = order.get("driver_id")
        amount = cheque.amount
        street = order_obj.src_street if order_obj else ""
        house = order_obj.src_house if order_obj else ""
        dststreet = order_obj.dst_street if order_obj else ""
        dsthouse = order_obj.dst_house if order_obj else ""

        # get car info
        autonum = cheque.autonum
        color = cheque.color
        brand = cheque.brand
        model = cheque.model

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
        markup.append([
            {
                "text": "⭐️",
                "callback_data": f"rating-{cheque.id}-{str(i)}",
            }
            for i in range(1, 6)
        ])

        markup.append(
            [
                {
                    "text": Strings(user_id=user.user_id).leave_feedback,
                    "web_app": {
                        "url": f"{WEBAPP_URL}/feedback/{cheque.id}/{user.get_lang_display()}"
                    },
                }
            ]
        )
        if order_obj:
            markup.append(
                [
                    {
                        "text": Strings(user_id=user.user_id).main_menu,
                        "callback_data": "main_menu",
                    }
                ]
            )
        send_newsletter_api(user.user_id, text, inline_buttons=markup)
        return True
    else:
        return False


@shared_task
def send_order_status(phone, data):
    status_code = int(data["status_code"])
    if user := get_user_by_phone(phone):
        order = get_order_by_order_id_without_404(data["id"])
        markup = None
        keyboard_remove = False
        if status_code == 80:
            text = Strings(user_id=user.user_id).your_order_is_in_moderation

        elif status_code == 50:
            text = Strings(user_id=user.user_id).created_pre_order_order

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
        elif status_code == 10 or status_code == 51:
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
            if order:
                markup = [[
                    {
                        "text": Strings(user_id=user.user_id).get_driver_location,
                        "callback_data": f"get_driver_location-{order.pk}"
                    }
                ]]
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
