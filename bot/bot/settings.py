import re
from bot.bot import main_menu
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler

from app.models import City
from bot.bot import CustomContext, make_button_settings
from bot.models import Bot_user
from bot.resources.conversationList import (
    ALL_SETTINGS,
    CITY_SETTINGS,
    LANG_SETTINGS,
    NAME_SETTINGS,
    PHONE_SETTINGS,
)
from bot.services import get_object_by_update, get_object_by_user_id
from bot.services.redis_service import set_user_lang
from bot.utils.bot_functions import update_message_reply_text


def _normalize_phone_number(phone_number: str | None) -> str | None:
    digits = re.sub(r"\D", "", phone_number or "")
    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("8") and len(digits) == 9:
        return f"+998{digits}"
    if len(digits) == 9:
        return f"+998{digits}"
    if digits.startswith("998") and len(digits) > 12:
        return f"+{digits[:12]}"
    return None


def _language_buttons(
    current_lang: int,
    back_text: str,
) -> InlineKeyboardMarkup:
    uz_text = "UZ 🇺🇿   ✅" if current_lang == 0 else "UZ 🇺🇿"
    ru_text = "RU 🇷🇺    ✅" if current_lang == 1 else "RU 🇷🇺"

    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=uz_text, callback_data="set_lang_uz")],
            [InlineKeyboardButton(text=ru_text, callback_data="set_lang_ru")],
            [InlineKeyboardButton(
                text=back_text, callback_data="back_settings")],
        ],
    )


async def _city_titles() -> list[str]:
    return [city.title async for city in City.objects.order_by("title")]


async def _city_by_title(title: str) -> City | None:
    return await City.objects.filter(title=title).afirst()


async def _current_city_title(user: Bot_user) -> str:
    if not user.city_id:
        return ""

    city = await City.objects.filter(pk=user.city_id).afirst()
    return city.title if city else ""


async def _show_settings_menu(update: Update, context: CustomContext) -> int:
    await make_button_settings(update, context)
    return ALL_SETTINGS


async def all_settings(update: Update, context: CustomContext):
    message = update.effective_message
    text = message.text if message else ""

    if text == context.words.main_menu:
        return ConversationHandler.END

    if text == context.words.change_lang:
        user = await get_object_by_update(update)
        prompt = await message.reply_text(
            context.words.select_lang,
            reply_markup=ReplyKeyboardRemove(),
        )
        await prompt.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=context.words.select_lang,
            reply_markup=_language_buttons(user.lang or 0, context.words.back),
        )
        return LANG_SETTINGS

    if text == context.words.change_phone_number:
        user = await get_object_by_update(update)
        contact_button = KeyboardButton(
            text=context.words.leave_number,
            request_contact=True,
        )
        text = (
            context.words.your_phone_number.replace("[]", user.phone or "")
            + "\n\n"
            + context.words.send_new_phone_number
        )
        await update_message_reply_text(
            update,
            text,
            reply_markup=ReplyKeyboardMarkup(
                [[contact_button], [context.words.back]],
                resize_keyboard=True,
            ),
        )
        return PHONE_SETTINGS

    if text == context.words.change_name:
        user = await get_object_by_update(update)
        await update_message_reply_text(
            update,
            f"{context.words.your_name}{user.name or ''}\n\n"
            f"{context.words.send_new_name}",
            reply_markup=ReplyKeyboardMarkup(
                [[context.words.back]],
                resize_keyboard=True,
            ),
        )
        return NAME_SETTINGS

    if text == context.words.change_city:
        user = await get_object_by_update(update)
        buttons = [[city_title] for city_title in await _city_titles()]
        buttons.append([context.words.back])
        await update_message_reply_text(
            update,
            f"{context.words.current_city}"
            f"{await _current_city_title(user)}\n\n"
            f"{context.words.select_city}",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True),
        )
        return CITY_SETTINGS

    return await _show_settings_menu(update, context)


async def lang_settings(update: Update, context: CustomContext):
    query = update.callback_query
    await query.answer()

    user = await get_object_by_user_id(query.message.chat.id)
    if query.data == "back_settings":
        await query.message.delete()
        return await _show_settings_menu(update, context)

    if query.data == "set_lang_uz":
        user.lang = 0
    elif query.data == "set_lang_ru":
        user.lang = 1
    else:
        return LANG_SETTINGS

    await user.asave(update_fields=["lang"])
    set_user_lang(user.user_id, user.lang)

    await query.edit_message_text(
        context.words.select_lang,
        reply_markup=_language_buttons(user.lang or 0, context.words.back),
    )
    return LANG_SETTINGS


async def phone_settings(update: Update, context: CustomContext):
    message = update.effective_message
    if message.text == context.words.back:
        return await _show_settings_menu(update, context)

    raw_phone_number = (
        message.contact.phone_number
        if message.contact
        else message.text
    )
    phone_number = _normalize_phone_number(raw_phone_number)
    if not phone_number:
        await update_message_reply_text(
            update,
            context.words.number_is_incorrect,
        )
        return PHONE_SETTINGS

    user = await get_object_by_update(update)
    phone_exists = await Bot_user.objects.filter(
        phone=phone_number,
    ).exclude(pk=user.pk).aexists()
    if phone_exists:
        await update_message_reply_text(update, context.words.number_is_logged)
        return PHONE_SETTINGS

    user.phone = phone_number
    await user.asave(update_fields=["phone"])
    await update_message_reply_text(
        update,
        context.words.changed_your_phone_number,
    )
    return await _show_settings_menu(update, context)


async def name_settings(update: Update, context: CustomContext):
    message = update.effective_message
    if message.text == context.words.back:
        return await _show_settings_menu(update, context)

    user = await get_object_by_update(update)
    user.name = message.text
    await user.asave(update_fields=["name"])
    await update_message_reply_text(update, context.words.changed_your_name)
    return await _show_settings_menu(update, context)


async def city_settings(update: Update, context: CustomContext):
    message = update.effective_message
    if message.text == context.words.back:
        return await _show_settings_menu(update, context)

    city = await _city_by_title(message.text)
    if not city:
        await update_message_reply_text(update, context.words.incorrect_city)
        return CITY_SETTINGS

    user = await get_object_by_update(update)
    user.city = city
    await user.asave(update_fields=["city"])
    await update_message_reply_text(update, context.words.changed_your_city)
    return await _show_settings_menu(update, context)


async def start(update: Update, context: CustomContext):
    await main_menu(update, context)
    return ConversationHandler.END