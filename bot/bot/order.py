from __future__ import annotations

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler

from app.models import Order, FavoriteAddress
from app.services.address_service import get_street_by_pk
from app.services.scat_service import (
    calculate_order_pre_cost_api,
    cancel_order_api,
    create_order_api,
)
from bot.bot import CustomContext, main_menu
from bot.resources.conversationList import *
from bot.services import get_object_by_update
from bot.services.string_service import (
    order_details_before_confirmation_string,
    select_point_a_string,
    select_point_b_string,
)
from bot.utils import (
    remove_inline_keyboards_from_last_msg,
    set_last_msg_and_markup,
    get_address_by_coordinates as _get_address_by_coordinates
)
from bot.utils.bot_functions import *
from bot.utils.keyboards import *
from app.utils import *
from asgiref.sync import sync_to_async


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
    # list of favorite addresses of user
    bot_user = await get_object_by_update(update)
    favorite_addresses_list = await sync_to_async(list)(
        FavoriteAddress.objects.filter(bot_user=bot_user).values_list("address", "lat", "lon")
        )
    address_markup = await selecting_address_keyboard(context=context, favorite_addresses_list=favorite_addresses_list)

    await bot_send_message(
        update,
        context,
        context.words.select_point_a,
        location_request_markup,
    )
    message = await bot_send_message(
        update,
        context,
        await select_point_a_string(context=context),
        address_markup,
    )
    await delete_callback_query_message(update)
    await set_last_msg_and_markup(context, message, address_markup)
    # empty src
    context.user_data.update(
        {
            "src": None,
            "src_street": "",
            "src_house": "",
            "src_lat": None,
            "src_lon": None,
        }
    )
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
    # list of favorite addresses of user
    bot_user = await get_object_by_update(update)
    favorite_addresses_list = await sync_to_async(list)(
        FavoriteAddress.objects.filter(bot_user=bot_user).values_list("address", "lat", "lon")
        )

    markup = await selecting_address_with_skip_keyboard(
        context=context, 
        favorite_addresses_list=favorite_addresses_list,
        add_skip_button=False if context.user_data.get("is_intercity") else True
    )

    message = await update_message_reply_text(update, text, markup)
    await delete_callback_query_message(update)
    await set_last_msg_and_markup(context, message, markup)
    # set empty dst
    context.user_data.update(
        {
            "dst": None,
            "dst_street": "",
            "dst_house": "",
            "dst_lat": None,
            "dst_lon": None,
        }
    )
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


async def _to_the_get_pre_order_date(update: Update, context: CustomContext):
    markup = await next_days_list_keyboard(context)
    text = context.words.select_pre_order_date
    message = await update.effective_message.reply_html(text, reply_markup=markup)
    await set_last_msg_and_markup(context, message, markup)
    await delete_callback_query_message(update)
    return GET_PRE_ORDER_DATE


async def _to_the_get_pre_order_time(update: Update, context: CustomContext):
    text = context.words.type_pre_order_time
    markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=context.words.back,
            callback_data="back"
        )
    ]])
    if query := update.callback_query:
        message = await query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
    else:
        message = await update.effective_message.reply_html(text, reply_markup=markup)
    await set_last_msg_and_markup(context, message)
    return GET_PRE_ORDER_TIME


async def _to_the_select_passangers_count(update: Update, context: CustomContext):
    markup = await select_passengers_count_keyboard(context)
    text = context.words.select_passengers_count
    if update.callback_query:
        message = await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode="HTML")
    else:
        message = await update.effective_message.reply_html(text, reply_markup=markup)
    await set_last_msg_and_markup(context, message, markup)
    return SELECT_PASSENGERS_COUNT


async def _to_the_confirm_order(update: Update, context: CustomContext):
    await bot_send_chat_action(update, context)
    data = context.user_data
    bot_user = await get_object_by_update(update)
    pre_order_datetime_iso = context.user_data.get("pre_order_datetime_iso")
    if pre_order_datetime_iso:
        pre_order_datetime: datetime = datetime.fromisoformat(pre_order_datetime_iso)
    else:
        pre_order_datetime = None

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
        pre_order_datetime
    )
    text = await order_details_before_confirmation_string(
        data.get("src_street", ""),
        data.get("src_house", ""),
        data.get("dst_street", ""),
        data.get("dst_house", ""),
        price,
        distance,
        pre_order_datetime=pre_order_datetime,
        passengers_count=data.get("passengers_count"),
        context=context,
    )
    markup = await confirm_order_keyboard(context=context, pre_order_datetime=pre_order_datetime)
    message = await update_message_reply_text(update, text, markup)
    context.user_data["token"] = token
    await set_last_msg_and_markup(context, message, markup)
    await delete_callback_query_message(update)
    return CONFIRM_ORDER


async def _to_the_order_process(update: Update, context: CustomContext):
    await delete_callback_query_message(update)
    data = context.user_data
    bot_user = await get_object_by_update(update)
    status, uuid_or_message = await create_order_api(
        data.get("token"),
        data.get("service_id"),
        passengers_count=data.get("passengers_count")
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


async def get_point_a(update: Update, context: CustomContext):
    await bot_send_chat_action(update, context)
    message = update.effective_message

    if query := update.callback_query:
        await query.delete_message()
        await set_last_msg_and_markup(context, None, None)
        *args, lat, lon = str(query.data).split("-")
        src, src_lat, src_lon = "location", lat, lon
        src_street = await _get_address_by_coordinates(lat, lon) or _coordinates_text(lat, lon)
        src_house = ""

    elif message.location:
        lat, lon = _location_coordinates(message.location)
        src, src_lat, src_lon = "location", lat, lon
        src_street = await _get_address_by_coordinates(lat, lon) or _coordinates_text(lat, lon)
        src_house = ""

    else:
        try:
            if "address_from_order" in message.text:
                *args, order_id = str(message.text).split('-')
                order = await Order.objects.filter(pk=int(order_id)).afirst()
                if not order:
                    await bot_delete_message(update, context)
                    return GET_POINT_A
                src_street = order.src_street
                src_house = order.src_house
                src_lat = order.src_lat
                src_lon = order.src_lon
                src = "location" if src_lat and src_lon else "address"
            else:
                street_title, street_id = _message_text_and_street_id(update)
                street = await get_street_by_pk(int(street_id))
                src_street = street.title or street_title
                src_house = ""
                src_lat = None
                src_lon = None
                src = "address"

        except (ValueError, TypeError):
            await bot_delete_message(update, context)
            return GET_POINT_A
        

    await remove_inline_keyboards_from_last_msg(update, context)
    context.user_data.update(
        {
            "src": src,
            "src_street": src_street,
            "src_house": src_house,
            "src_lat": src_lat,
            "src_lon": src_lon,
        }
    )
    if src == "location":
        if context.user_data.get("ask_point_b"):
            return await _to_the_get_point_b(update, context)
        elif context.user_data.get("is_intercity"):
            return await _to_the_get_pre_order_date(update, context)
        else:
            return await _to_the_confirm_order(update, context)

    return await _to_the_get_point_a_house(update, context)


async def get_point_a_house(update: Update, context: CustomContext):
    if query := update.callback_query:
        await query.delete_message()
    else:
        message_text = _message_text(update)
        context.user_data["src_house"] = message_text
        await remove_inline_keyboards_from_last_msg(update, context)

    if context.user_data.get("ask_point_b"):
        return await _to_the_get_point_b(update, context)
    elif context.user_data.get("is_intercity"):
        return await _to_the_get_pre_order_date(update, context)
    else:
        return await _to_the_confirm_order(update, context)


async def get_pre_order_date(update: Update, context: CustomContext):
    query = update.callback_query
    *args, date_ordinal = str(query.data).split("-")
    context.user_data['pre_order_date_ordinal'] = int(date_ordinal)
    return await _to_the_get_pre_order_time(update, context)


async def get_pre_order_time(update: Update, context: CustomContext):
    message_text = update.effective_message.text
    pre_order_time: time | None = parse_time(message_text)

    if pre_order_time is None:
        await update.effective_message.delete()
        return

    pre_order_date_ordinal = context.user_data.get('pre_order_date_ordinal')
    pre_order_date: date = date.fromordinal(int(pre_order_date_ordinal))
    pre_order_datetime: datetime = datetime.combine(pre_order_date, pre_order_time)
    context.user_data['pre_order_datetime_iso'] = pre_order_datetime.isoformat()
    await remove_inline_keyboards_from_last_msg(update, context)
    return await _to_the_select_passangers_count(update, context)


async def get_passengers_count(update: Update, context: CustomContext):
    query = update.callback_query
    *args, passengers_count = str(query.data).split("-")
    context.user_data['passengers_count'] = int(passengers_count)

    return await _to_the_confirm_order(update, context)


async def get_point_b(update: Update, context: CustomContext):
    await bot_send_chat_action(update, context)
    message = update.effective_message
    if query := update.callback_query:
        await query.delete_message()
        await set_last_msg_and_markup(context, None, None)
        *args, lat, lon = str(query.data).split("-")
        dst, dst_lat, dst_lon = "location", lat, lon
        dst_street = await _get_address_by_coordinates(lat, lon) or _coordinates_text(lat, lon)
        dst_house = ""

    elif message.location:
        lat, lon = _location_coordinates(message.location)
        dst, dst_lat, dst_lon = "location", lat, lon
        dst_street = await _get_address_by_coordinates(lat, lon) or _coordinates_text(lat, lon)
        dst_house = ""
    else:
        try:
            if "address_from_order" in message.text:
                *args, order_id = str(message.text).split('-')
                order = await Order.objects.filter(pk=int(order_id)).afirst()
                if not order:
                    await bot_delete_message(update, context)
                    return GET_POINT_B
                dst_street = order.dst_street
                dst_house = order.dst_house
                dst_lat = order.dst_lat
                dst_lon = order.dst_lon
                dst = "location" if dst_lat and dst_lon else "address"
            else:
                street_title, street_id = _message_text_and_street_id(update)
                street = await get_street_by_pk(int(street_id))
                dst_street = street.title or street_title
                dst_house = ""
                dst_lat = None
                dst_lon = None
                dst = "address"
            
        except (ValueError, TypeError):
            await bot_delete_message(update, context)
            return GET_POINT_B

    await remove_inline_keyboards_from_last_msg(update, context)
    context.user_data.update(
        {
            "dst": dst,
            "dst_street": dst_street,
            "dst_house": "",
            "dst_lat": dst_lat,
            "dst_lon": dst_lon,
        },
    )
    if dst == "location":
        if context.user_data.get("is_intercity"):
            return await _to_the_get_pre_order_date(update, context)
        else:
            return await _to_the_confirm_order(update, context)

    return await _to_the_get_point_b_house(update, context)


async def get_point_b_house(update: Update, context: CustomContext):
    if query := update.callback_query:
        await query.delete_message()
    else:
        message_text = _message_text(update)
        context.user_data["dst_house"] = message_text
        await remove_inline_keyboards_from_last_msg(update, context)

    if context.user_data.get("is_intercity"):
        return await _to_the_get_pre_order_date(update, context)
    else:
        return await _to_the_confirm_order(update, context)


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
    if query := update.callback_query:
        await bot_delete_message(update, context, query.message.message_id)
    else:
        await remove_inline_keyboards_from_last_msg(update, context)
    await main_menu(update, context)
    return ConversationHandler.END