from __future__ import annotations

from telegram import Update

from bot import CustomContext
from bot.resources.strings import Strings
from bot.models import Bot_user
from bot.resources.colors import colors_dict


def _words(
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
    chat_id: int | None = None,
):
    if context is not None and hasattr(context, "words"):
        return context.words

    if chat_id is None and update is not None:
        if update.effective_chat:
            chat_id = update.effective_chat.id
        elif update.inline_query:
            chat_id = update.inline_query.from_user.id

    return Strings(chat_id)


def _format_seconds(seconds, words) -> str:
    if not seconds:
        return ""

    seconds = int(seconds)
    return (
        f"{seconds // 60} {words.min} "
        f"{seconds % 60} {words.sek}"
    )



def get_color(color, chat_id):
    user = Bot_user.objects.get(user_id=chat_id)

    if user.lang == 0:
        result = colors_dict[color] if color in colors_dict else color
    else:
        result = color
    return result
    


def cheque_info(
    chat_id,
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
    model
):
    words = _words(chat_id=chat_id)

    return (
        f"<b>{words.finish_text}</b>\n\n"
        f"<i>{words.point_a}:</i> {src}\n"
        f"<i>{words.point_b}:</i> {dst}\n"
        f"<i>{words.amount}:</i> {amount}\n"
        # f"{words.driver_info}:\n"
        f"<i>{words.car}:</i> "
        f"{get_color(color, chat_id=chat_id)} {brand} {model} | {autonum}\n"
    )


def car_info_string(
    chat_id,
    remaining,
    car_phone,
    car_firstname,
    brand,
    model,
    color,
    autonum,
):
    words = _words(chat_id=chat_id)
    return (
        f"<i>{words.car}</i>: {color} {brand} {model} | {autonum}\n"
        f"<i>{words.arrival_time}</i>: {remaining} {words.minute}\n"
        f"<i>{words.driver}</i>: {car_firstname}, {car_phone}"
    )


async def select_point_a_string(
    update: Update | None = None,
    context: CustomContext | None = None,
) -> str:
    words = _words(update=update, context=context)
    return words.select_address_or_location


async def select_point_b_string(
    street,
    house="",
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
) -> str:
    words = _words(update=update, context=context)
    return (
        f"{words.point_a}: {street} {house}\n\n"
        f"{words.select_point_b}\n"
        f"{words.select_address_or_location}"
    )


async def address_description_for_query_string(update: Update, city) -> str:
    words = _words(update=update)
    return f"{words.city}: {city}"


async def order_details_before_confirmation_string(
    point_a,
    house_a,
    point_b,
    house_b,
    price,
    distance,
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
) -> str:
    words = _words(update=update, context=context)
    point_a_address = f"{point_a} {house_a or ''}".strip()
    point_b_address = f"{point_b} {house_b or ''}".strip()
    point_b_line = (
        f"\n{words.point_b}: {point_b_address}"
        if point_b_address
        else ""
    )

    return (
        f"{words.point_a}: {point_a_address}"
        f"{point_b_line}\n"
        f"{words.price}: {price}\n"
        f"{words.distance}: {distance} {words.meter}\n\n"
        f"{words.confirm_order}"
    )


async def order_history_details_string(
    update,
    src,
    dst,
    starttime,
    endtime,
    amount,
    distance,
    standtime,
    waittime,
    street,
    house,
    dststreet,
    dsthouse,
    autonum,
    color,
    brand,
    model,
    lastname,
    firstname,
    phone,
    taximeter_data,
):
    words = _words(update=update)
    baggage = taximeter_data.get("margin", "") if taximeter_data else ""

    return (
        f"🕙 <b>{endtime.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        f"<i>{words.point_a}:</i> {src}\n"
        f"<i>{words.point_b}:</i> {dst}\n"
        f"<i>{words.amount}:</i> {amount}\n"
        f"<i>{words.baggage}:</i> {baggage}\n"
        f"<i>{words.distance}:</i> {distance} {words.meter}\n"
        f"<i>{words.standtime}:</i> {_format_seconds(standtime, words)}\n"
        f"<i>{words.waittime}:</i> {waittime}\n\n"
        f"<i>{words.driver_name}:</i> {lastname} {firstname}\n"
        f"<i>{words.phone}:</i> {phone}\n"
        f"<i>{words.car}:</i> "
        f"{get_color(color, update=update)} {brand} {model} | {autonum}\n"
    )
