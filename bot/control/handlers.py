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
    main, login, settings, order, search
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

order_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Strings.let_order), main.ordering)],
    states={
        GET_POINT_A: [
            CallbackQueryHandler(order.get_point_a_query),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_a),
            MessageHandler(filters.LOCATION, order.get_point_a),
            ],
        GET_POINT_A_HOUSE: [MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_a_house)],
        GET_POINT_B: [
            CallbackQueryHandler(order.get_point_b_query),
            CommandHandler("start", order.get_point_b),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_b),
            MessageHandler(filters.LOCATION, order.get_point_b),
            ],
        GET_POINT_B_HOUSE: [MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_b_house)],
        CONFIRM_ORDER: [MessageHandler(filters.TEXT & exceptions_for_filter_text, order.confirm_order)],
        ORDER_PROCESS: [
            CallbackQueryHandler(order.order_process),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.order_process)
        ],
    },
    fallbacks=[
        CommandHandler("start", order.start),
    ],
    name='order',
    persistent=True,
)

handlers = [
    login_handler,
    settings_handler,
    order_handler,
    InlineQueryHandler(search.get_inline_query),
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]