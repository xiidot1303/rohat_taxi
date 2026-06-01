from bot import *
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    TypeHandler,
    ConversationHandler
)

from bot.resources.conversationList import *

from bot.bot import (
    main, login, settings
)

exceptions_for_filter_text = (~filters.COMMAND) & (~filters.Text(Strings.main_menu))

login_handler = ConversationHandler(
    entry_points=[CommandHandler("start", main.start)],
    states={
        SELECT_LANG: [MessageHandler(filters.Text(Strings.uz_ru), login.select_lang)],
        GET_NAME: [MessageHandler(filters.TEXT & exceptions_for_filter_text, login.get_name)],
        GET_CONTACT: [MessageHandler((filters.TEXT | filters.CONTACT) & exceptions_for_filter_text, login.get_contact)],
        GET_CITY: [MessageHandler(filters.TEXT & exceptions_for_filter_text, login.get_city)],
    },
    fallbacks=[
        CommandHandler("start", login.start),
    ],
    name="login",
    persistent=True,

)


settings_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Strings.settings), main.settings)],
    states={
        ALL_SETTINGS: [MessageHandler(filters.TEXT & exceptions_for_filter_text, settings.all_settings)],
        LANG_SETTINGS: [
            CallbackQueryHandler(settings.lang_settings)
        ],
        PHONE_SETTINGS: [MessageHandler(filters.ALL & exceptions_for_filter_text, settings.phone_settings)],
        NAME_SETTINGS: [MessageHandler(filters.TEXT & exceptions_for_filter_text, settings.name_settings)],
        CITY_SETTINGS: [MessageHandler(filters.TEXT & exceptions_for_filter_text, settings.city_settings)],
    },
    fallbacks=[
        CommandHandler("start", settings.start),
        MessageHandler(filters.Text(Strings.main_menu), settings.start),
        CallbackQueryHandler(settings.start, pattern="main_menu")
    ],
    name="settings",
    persistent=True,
  
)

handlers = [
    login_handler,
    settings_handler,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]