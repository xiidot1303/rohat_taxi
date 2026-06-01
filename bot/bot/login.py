import re
from app.models import City
from bot.bot import *
from bot.models import Bot_user


async def _get_city_titles():
    return [city.title async for city in City.objects.order_by("title")]


async def _get_city_by_title(city_title):
    async for city in City.objects.filter(title=city_title)[:1]:
        return city
    return None


def _normalize_phone_number(phone_number):
    digits = re.sub(r"\D", "", phone_number or "")
    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("8") and len(digits) == 9:
        return f"+998{digits}"
    if len(digits) == 9:
        return f"+998{digits}"
    if digits.startswith("998") and len(digits) > 12:
        digits = digits[:12]
        return f"+{digits}"
    return None


async def _to_the_select_lang(update: Update, context: CustomContext):
    await update_message_reply_text(
        update,
        context.words.hello,
        reply_markup=await select_lang_keyboard(),
    )
    return SELECT_LANG


async def _to_the_get_name(update: Update, context: CustomContext):
    await update_message_reply_text(
        update=update,
        text=context.words.type_name,
        reply_markup=await reply_keyboard_markup([[context.words.back]]),
    )
    return GET_NAME


async def _to_the_get_contact(update: Update, context: CustomContext):
    i_contact = KeyboardButton(
        text=context.words.leave_number,
        request_contact=True,
    )
    await update_message_reply_text(
        update,
        context.words.send_number,
        reply_markup=await reply_keyboard_markup(
            [[i_contact], [context.words.back]]
        ),
    )
    return GET_CONTACT


async def _to_the_get_city(update: Update, context: CustomContext):
    buttons = [[city_title] for city_title in await _get_city_titles()]
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    msg = await update_message_reply_text(update, context.words.select_city, markup)
    await set_last_msg_and_markup(context, msg, markup)
    return GET_CITY


async def select_lang(update: Update, context: CustomContext):
    text = update.effective_message.text or ""
    if "UZ" in text:
        lang = 0
    elif "RU" in text:
        lang = 1
    else:
        return await _to_the_select_lang(update, context)

    await get_or_create(user_id=update.effective_chat.id)
    obj = await get_object_by_user_id(user_id=update.effective_chat.id)
    obj.lang = lang
    await obj.asave()

    return await _to_the_get_name(update, context)


async def get_name(update: Update, context: CustomContext):
    if update.effective_message.text == context.words.back:
        return await _to_the_select_lang(update, context)

    obj = await get_object_by_user_id(user_id=update.effective_chat.id)
    obj.name = update.effective_message.text
    obj.username = update.effective_chat.username
    obj.firstname = update.effective_chat.first_name
    await obj.asave()

    return await _to_the_get_contact(update, context)


async def get_contact(update: Update, context: CustomContext):
    if update.effective_message.text == context.words.back:
        return await _to_the_get_name(update, context)

    if update.effective_message.contact:
        phone_number = update.effective_message.contact.phone_number
    else:
        phone_number = update.effective_message.text

    phone_number = _normalize_phone_number(phone_number)
    if not phone_number:
        await update_message_reply_text(update, context.words.number_is_incorrect)
        return GET_CONTACT

    if await Bot_user.objects.filter(phone=phone_number).aexists():
        await update_message_reply_text(update, context.words.number_is_logged)
        return GET_CONTACT

    obj = await get_object_by_user_id(user_id=update.effective_chat.id)
    obj.phone = phone_number
    await obj.asave()
    return await _to_the_get_city(update, context)


async def get_city(update: Update, context: CustomContext):
    city_title = update.effective_message.text
    bot_user = await get_object_by_update(update)
    city = await _get_city_by_title(city_title)

    if not city:
        await update_message_reply_text(update, context.words.incorrect_city)
        return GET_CITY

    bot_user.city = city
    await bot_user.asave()
    await main_menu(update, context)
    return ConversationHandler.END


async def start(update: Update, context: CustomContext):
    return await _to_the_select_lang(update, context)