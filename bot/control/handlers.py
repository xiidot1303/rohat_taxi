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
    main, login, settings, order, search, 
    rating, driver_location, feedback
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
            CallbackQueryHandler(order.start, pattern="back"),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_a),
            MessageHandler(filters.LOCATION, order.get_point_a),
            ],
        GET_POINT_A_HOUSE: [
            CallbackQueryHandler(order.to_the_get_point_a, pattern="back"),
            CallbackQueryHandler(order.get_point_a_house, pattern="skip"),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_a_house)
            ],
        GET_PRE_ORDER_DATE: [
            CallbackQueryHandler(order.get_pre_order_date, pattern="^pre_order_date"),
            CallbackQueryHandler(order.to_the_get_point_a, pattern="back")
        ],
        GET_PRE_ORDER_TIME: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_pre_order_time),
            CallbackQueryHandler(order._to_the_get_pre_order_date, pattern="back")
        ],
        GET_POINT_B: [
            CallbackQueryHandler(order.to_the_get_point_a, pattern="back"),
            CallbackQueryHandler(order._to_the_confirm_order, pattern="skip"),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_b),
            MessageHandler(filters.LOCATION, order.get_point_b),
            ],
        GET_POINT_B_HOUSE: [
            CallbackQueryHandler(order._to_the_get_point_b, pattern="back"),
            CallbackQueryHandler(order.get_point_b_house, pattern="skip"),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.get_point_b_house)
            ],
        CONFIRM_ORDER: [
            CallbackQueryHandler(order._to_the_order_process, pattern="confirm"),
            CallbackQueryHandler(order.to_the_get_point_a, pattern="change_point_a"),
            CallbackQueryHandler(order._to_the_get_point_b, pattern="change_point_b"),
            CallbackQueryHandler(order._to_the_get_pre_order_date, pattern="change_pre_order_time"),
            ],
        ORDER_PROCESS: [
            CallbackQueryHandler(order.order_process),
            MessageHandler(filters.TEXT & exceptions_for_filter_text, order.order_process)
        ],
    },
    fallbacks=[
        CommandHandler("start", order.start),
        MessageHandler(filters.Text(Strings.main_menu), order.start),
        CallbackQueryHandler(order.start, pattern="main_menu")
    ],
    name='order',
    persistent=True,
)

feedback_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Strings.leave_feedback), feedback.leave_feedback)],
    states={
        GET_FEEDBACK: [
            MessageHandler(filters.TEXT & exceptions_for_filter_text, feedback.get_feedback)
        ]
    },
    fallbacks=[
        CommandHandler("start", feedback.start),
        MessageHandler(filters.Text(Strings.main_menu), feedback.start)
    ],
    name='feedback',
    persistent=True,
)

get_rating_handler = CallbackQueryHandler(rating.get_rating, pattern="^rating")
continue_rating_handler = CallbackQueryHandler(rating.continue_rating, pattern="^continue_rating")
select_rating_reason_handler = CallbackQueryHandler(rating.select_rating_reason, pattern="^select_rating_reason")
driver_location_handler = CallbackQueryHandler(driver_location.get_driver_location, pattern="^get_driver_location")

handlers = [
    login_handler,
    settings_handler,
    order_handler,
    get_rating_handler,
    continue_rating_handler,
    select_rating_reason_handler,
    driver_location_handler,
    feedback_handler,
    InlineQueryHandler(search.get_inline_query),
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]