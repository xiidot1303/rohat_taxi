from bot.bot import *
from app.models import *
from bot.services.redis_service import get_user_lang


async def _compleation(update: Update, cheque_id, rating, reason_id=None):
    cheque: Cheque | None = await Cheque.objects.filter(id=cheque_id).afirst()
    reason: RatingReason | None = await RatingReason.objects.filter(id=reason_id).afirst()
    await OrderRating.objects.acreate(rating=rating, cheque=cheque, reason=reason)
    _words = Strings(user_id=update.effective_user.id)

    text = _words.rating_compleation
    await update.callback_query.answer(text)

    buttons = []
    if order := await Order.objects.filter(order_id = cheque_id).afirst():
        buttons = [[
            InlineKeyboardButton(
                text=_words.main_menu,
                callback_data="main_menu"
            )
        ]]

    user_lang_code = get_user_lang(update.effective_user.id)
    user_lang = "uz" if user_lang_code == 0 else "ru"
    buttons.append([
        InlineKeyboardButton(
            text=_words.leave_feedback,
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/feedback/{cheque_id}/{user_lang}")
        )
    ])
    markup = InlineKeyboardMarkup(buttons)

    
    old_text = update.effective_message.text
    text = old_text.replace(_words.select_reason_of_rating, "")
    text = text.replace(_words.leave_your_feedback, "")
    await update.callback_query.edit_message_text(text=text, reply_markup=markup)
    await update.callback_query.answer(_words.rating_compleation)


async def get_rating(update: Update, context: CustomContext):
    query = update.callback_query
    *args, cheque_id, rating = (query.data).split("-")

    buttons = []

    buttons.append(
        [
            InlineKeyboardButton(
                text="⭐️",
                callback_data=f"rating-{cheque_id}-{str(i)}",
                style="success" if i <= int(rating) else None,
            )
            for i in range(1, 6)
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=context.words.continue_,
                callback_data=f"continue_rating-{cheque_id}-{rating}",
            )
        ]
    )
    bot_user: Bot_user = await get_object_by_update(update)
    buttons.append(
        [
            InlineKeyboardButton(
                text=context.words.leave_feedback,
                web_app=WebAppInfo(
                    url=f"{WEBAPP_URL}/feedback/{cheque_id}/{bot_user.get_lang_display()}"
                ),
            )
        ]
    )
    markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_reply_markup(markup)


async def continue_rating(update: Update, context: CustomContext):
    query = update.callback_query
    *args, cheque_id, rating = (query.data).split("-")
    # complete, if rating is bigger then 3
    if int(rating) > 3:
        return await _compleation(update, cheque_id, rating)

    user_lang_code = get_user_lang(update.effective_user.id)
    user_lang = "uz" if user_lang_code == 0 else "ru"
    # send list of rating reason to select
    buttons = [
        [
            InlineKeyboardButton(
                text=getattr(reason, f"text_{user_lang}"),
                callback_data=f"select_rating_reason-{cheque_id}-{rating}-{reason.pk}",
            )
        ]
        async for reason in RatingReason.objects.filter()
    ]

    # buttons.append([
    #     InlineKeyboardButton(
    #         text=context.words.leave_feedback,
    #         web_app=WebAppInfo(url=f"{WEBAPP_URL}/feedback/{cheque_id}/{user_lang}")
    #     )
    # ])

    markup = InlineKeyboardMarkup(buttons)
    old_text = update.effective_message.text
    text = old_text.replace(context.words.leave_your_feedback, context.words.select_reason_of_rating)
    await query.edit_message_text(text, reply_markup=markup)
    await query.answer(context.words.select_reason_of_rating, show_alert=True)


async def select_rating_reason(update: Update, context: CustomContext):
    query = update.callback_query
    *args, cheque_id, rating, reason_id = (query.data).split("-")

    await _compleation(update, cheque_id, rating, reason_id)