from bot import *
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext, ExtBot, Application
from dataclasses import dataclass
from asgiref.sync import sync_to_async
from bot.utils import *
from bot.utils.bot_functions import *
from bot.utils.keyboards import *
from bot.services import *
from bot.resources.conversationList import *
from app.resources.classes import *
from bot.services.string_service import *
from bot.services.redis_service import get_user_lang
from config import WEBAPP_URL


async def is_message_back(update: Update):
    if update.effective_message.text == Strings(update.effective_user.id).back:
        return True
    else:
        return False


async def main_menu(update: Update, context: CustomContext):
    bot = context.bot
    user_lang_code = get_user_lang(update.effective_user.id)
    user_lang = ["uz", "ru"][user_lang_code]
    order_history_webapp_url = f"{WEBAPP_URL}/order-history?bot_user_id={update.effective_user.id}&lang={user_lang}"
    order_history_button = KeyboardButton(
        text=context.words.order_history, 
        web_app=WebAppInfo(url=order_history_webapp_url)
    )
    keyboard = [
        [context.words.let_order, order_history_button],
        [context.words.leave_feedback, context.words.settings],

    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(
        update.effective_message.chat_id,
        context.words.main_menu,
        reply_markup=reply_markup
    )
    context.application.create_task(check_username(update))


async def make_button_settings(update: Update, context: CustomContext):
    await context.bot.send_message(
        update.effective_chat.id,
        context.words.settings_desc,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=await settings_keyboard(context),
            resize_keyboard=True,
        ),
    )
