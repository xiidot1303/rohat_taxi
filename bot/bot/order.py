from __future__ import annotations

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler

from app.models import Order
from app.services.address_service import get_street_by_pk
from app.services.scat_service import (
    calculate_order_pre_cost_api,
    cancel_order_api,
    create_order_api,
)
from bot.bot import CustomContext, main_menu
from bot.resources.conversationList import (
    CONFIRM_ORDER,
    GET_POINT_A,
    GET_POINT_A_HOUSE,
    GET_POINT_B,
    GET_POINT_B_HOUSE,
    ORDER_PROCESS,
)
from bot.services import get_object_by_update
from bot.services.string_service import (
    order_details_before_confirmation_string,
    select_point_a_string,
    select_point_b_string,
)
from bot.utils import (
    remove_inline_keyboards_from_last_msg,
    set_last_msg_and_markup,
)
from bot.utils.bot_functions import (
    bot_delete_message,
    bot_send_and_delete_message,
    bot_send_chat_action,
    bot_send_message,
    reply_keyboard_remove,
    update_message_reply_text,
)
from bot.utils.keyboards import (
    confirm_order_keyboard,
    request_location_keyboard,
    selecting_address_house_keyboard,
    selecting_address_keyboard,
    selecting_address_with_skip_keyboard,
)


def _coordinates_text(lat, lon) -> str:
    return f"{lat}, {lon}"


def _message_text(update: Update) -> str:
    return update.effective_message.text or ""


def _split_text_and_text_id(message_text: str) -> tuple[str, str]:
    title, street_id = message_text.split("<>?", maxsplit=1)
    return title, street_id


def _message_text_and_street_id(update: Update) -> tuple[str, str]:
    return _split_text_and_text_id(_message_text(update))


def _location_coordinates(location) -> tuple[float, float]:
    return location.latitude, location.longitude


async def _create_order_record(bot_user, uuid: str, data: dict) -> Order:
    return await Order.objects.acreate(
        user=bot_user,
        uuid=uuid,
        status=1,
        src_street=data.get("src_street") or "",
        src_house=data.get("src_house") or "",
        dst_street=data.get("dst_street") or "",
        dst_house=data.get("dst_house") or "",
        src_lat=data.get("src_lat"),
        src_lon=data.get("src_lon"),
        dst_lat=data.get("dst_lat"),
        dst_lon=data.get("dst_lon"),
        service_id=data.get("service_id"),
    )


async def to_the_get_point_a(update: Update, context: CustomContext):
    location_request_markup = await request_location_keyboard(context=context)
    address_markup = await selecting_address_keyboard(context=context)

    await bot_send_message(
        update,
        context,
        context.words.select_point_a,
        location_request_markup,
    )
    message = await update_message_reply_text(
        update,
        await select_point_a_string(context=context),
        address_markup,
    )
    await set_last_msg_and_markup(context, message, address_markup)
    return GET_POINT_A


async def _to_the_get_point_a_house(update: Update, context: CustomContext):
    markup = await selecting_address_house_keyboard(context=context)
    message = await update_message_reply_text(
        update,
        context.words.type_house_number,
        markup,
    )
    await set_last_msg_and_markup(context, message, markup)
    return GET_POINT_A_HOUSE


async def _to_the_get_point_b(update: Update, context: CustomContext):
    street = context.user_data.get("src_street", "")
    house = context.user_data.get("src_house", "")
    text = await select_point_b_string(street, house, context=context)
    markup = await selecting_address_with_skip_keyboard(context=context)

    await bot_send_and_delete_message(
        update,
        context,
        text,
        reply_markup=await reply_keyboard_remove(),
    )
    message = await update_message_reply_text(update, text, markup)
    await set_last_msg_and_markup(context, message, markup)
    return GET_POINT_B


async def _to_the_get_point_b_house(update: Update, context: CustomContext):
    markup = await selecting_address_house_keyboard(context=context)
    message = await update_message_reply_text(
        update,
        context.words.type_house_number,
        markup,
    )
    await set_last_msg_and_markup(context, message, markup)
    return GET_POINT_B_HOUSE


async def _to_the_confirm_order(update: Update, context: CustomContext):
    data = context.user_data
    bot_user = await get_object_by_update(update)
    city = await bot_user.get_city
    price, distance, token = await calculate_order_pre_cost_api(
        bot_user.phone,
        data.get("src"),
        data.get("dst"),
        data.get("src_street"),
        data.get("src_house"),
        data.get("dst_street"),
        data.get("dst_house"),
        data.get("src_lat"),
        data.get("src_lon"),
        data.get("dst_lon"),
        data.get("dst_lat"),
        data.get("service_id"),
    )
    text = await order_details_before_confirmation_string(
        data.get("src_street", ""),
        data.get("src_house", ""),
        data.get("dst_street", ""),
        data.get("dst_house", ""),
        price,
        distance,
        context=context,
    )
    markup = await confirm_order_keyboard(context=context)
    message = await update_message_reply_text(update, text, markup)
    context.user_data["token"] = token
    await set_last_msg_and_markup(context, message, markup)
    return CONFIRM_ORDER


async def _to_the_order_process(update: Update, context: CustomContext):
    data = context.user_data
    bot_user = await get_object_by_update(update)
    status, uuid_or_message = await create_order_api(
        data.get("token"),
        data.get("service_id")
    )
    if not status:
        await update_message_reply_text(update, uuid_or_message)
        return CONFIRM_ORDER

    order = await _create_order_record(bot_user, uuid_or_message, data)
    markup = ReplyKeyboardMarkup(
        keyboard=[[context.words.cancel_order]],
        resize_keyboard=True,
    )
    message = await update_message_reply_text(
        update,
        context.words.order_in_process,
        markup,
    )
    context.user_data["order_id"] = order.id
    await set_last_msg_and_markup(context, message, markup)
    return ORDER_PROCESS


async def get_point_a_query(update: Update, context: CustomContext):
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await bot_delete_message(update, context, query.message.message_id)
        await main_menu(update, context)
        return ConversationHandler.END

    if query.data == "main_menu":
        await bot_delete_message(update, context, query.message.message_id)
        await main_menu(update, context)
        return ConversationHandler.END

    return GET_POINT_A


async def get_point_a(update: Update, context: CustomContext):
    await bot_send_chat_action(update, context)
    message = update.effective_message

    if message.location:
        lat, lon = _location_coordinates(message.location)
        await remove_inline_keyboards_from_last_msg(update, context)
        context.user_data.update(
            {
                "src": "location",
                "src_lat": lat,
                "src_lon": lon,
                "src_street": _coordinates_text(lat, lon),
                "src_house": ""
            },
        )
        if context.user_data.get("next") == GET_POINT_B:
            return await _to_the_get_point_b(update, context)
        return await _to_the_confirm_order(update, context)

    try:
        street_title, street_id = _message_text_and_street_id(update)
        street = await get_street_by_pk(int(street_id))
    except (ValueError, TypeError):
        await bot_delete_message(update, context)
        return GET_POINT_A

    await remove_inline_keyboards_from_last_msg(update, context)
    context.user_data.update(
        {
            "src": "address",
            "src_street": street.title or street_title,
            "src_house": ""
        },
    )
    return await _to_the_confirm_order(update, context)


async def get_point_a_house(update: Update, context: CustomContext):
    message_text = _message_text(update)
    if message_text == context.words.back:
        return await to_the_get_point_a(update, context)

    context.user_data["src_house"] = (
        "" if message_text == context.words.skip else message_text
    )
    if context.user_data.get("next") == GET_POINT_B:
        return await _to_the_get_point_b(update, context)
    return await _to_the_confirm_order(update, context)


async def get_point_b_query(update: Update, context: CustomContext):
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await bot_delete_message(update, context, query.message.message_id)
        context.user_data["next"] = GET_POINT_B
        return await to_the_get_point_a(update, context)

    if query.data == "main_menu":
        await bot_delete_message(update, context, query.message.message_id)
        await main_menu(update, context)
        return ConversationHandler.END

    if query.data == "skip":
        await bot_delete_message(update, context, query.message.message_id)
        context.user_data.update(
            {"dst": "", "dst_street": "", "dst_house": ""},
        )
        return await _to_the_confirm_order(update, context)

    return GET_POINT_B


async def get_point_b(update: Update, context: CustomContext):
    await bot_send_chat_action(update, context)
    message = update.effective_message

    if message.location:
        lat, lon = _location_coordinates(message.location)
        await remove_inline_keyboards_from_last_msg(update, context)
        context.user_data.update(
            {
                "dst": "location",
                "dst_lat": lat,
                "dst_lon": lon,
                "dst_street": _coordinates_text(lat, lon),
                "dst_house": "",
            },
        )
        return await _to_the_confirm_order(update, context)

    try:
        street_title, street_id = _message_text_and_street_id(update)
        street = await get_street_by_pk(int(street_id))
    except (ValueError, TypeError):
        await bot_delete_message(update, context)
        return GET_POINT_B

    await remove_inline_keyboards_from_last_msg(update, context)
    context.user_data.update(
        {
            "dst": "address",
            "dst_street": street.title or street_title,
            "dst_house": "",
        },
    )
    return await _to_the_get_point_b_house(update, context)


async def get_point_b_house(update: Update, context: CustomContext):
    message_text = _message_text(update)
    if message_text == context.words.back:
        return await _to_the_get_point_b(update, context)

    context.user_data["dst_house"] = (
        "" if message_text == context.words.skip else message_text
    )
    return await _to_the_confirm_order(update, context)


async def confirm_order(update: Update, context: CustomContext):
    message_text = _message_text(update)
    if message_text == context.words.confirm:
        return await _to_the_order_process(update, context)

    if message_text == context.words.change_point_a:
        context.user_data["next"] = CONFIRM_ORDER
        return await to_the_get_point_a(update, context)

    if message_text == context.words.change_point_b:
        return await _to_the_get_point_b(update, context)

    if message_text == context.words.main_menu:
        await main_menu(update, context)
        return ConversationHandler.END

    return CONFIRM_ORDER


async def order_process(update: Update, context: CustomContext):
    message_text = _message_text(update)
    if message_text == context.words.cancel_order:
        order_id = context.user_data.get("order_id")
        order = await Order.objects.filter(pk=order_id).afirst()
        if order and order.status in [80, 10, 11, 1, None]:
            await cancel_order_api(order.uuid)
            await main_menu(update, context)
            return ConversationHandler.END

    await bot_delete_message(update, context)
    return ORDER_PROCESS


async def start(update: Update, context: CustomContext):
    # remove inline buttons
    await remove_inline_keyboards_from_last_msg(update, context)
    await main_menu(update, context)
    return ConversationHandler.END