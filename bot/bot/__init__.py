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
from config import WEBAPP_URL


async def is_message_back(update: Update):
    if update.effective_message.text == Strings(update.effective_user.id).back:
        return True
    else:
        return False


async def main_menu(update: Update, context: CustomContext):
    bot = context.bot
    keyboard = [
        [context.words.let_order, context.words.order_history],
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
