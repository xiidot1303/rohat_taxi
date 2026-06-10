from bot.bot import *
import json
import logging
import traceback
import html
from django.db import close_old_connections
from telegram.error import TimedOut
import asyncio
from bot.bot.order import to_the_get_point_a as _to_the_get_point_a


async def start(update: Update, context: CustomContext):
    if await is_group(update):
        return 

    if await is_registered(update.message.chat.id):
        await main_menu(update, context)
    else:
        hello_text = Strings.hello
        await update.effective_message.reply_html(
            hello_text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[["UZ 🇺🇿", "RU 🇷🇺"]], resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return SELECT_LANG



async def settings(update: Update, context: CustomContext):
    await make_button_settings(update, context)
    return ALL_SETTINGS

async def ordering(update: Update, context: CustomContext):
    bot_user = await get_object_by_update(update)
    if bot_user.blocked:
        await update.effective_message.reply_html(update, context.words.you_are_blocked)
        return
    context.user_data['next'] = CONFIRM_ORDER
    context.user_data['dst'] = ''
    context.user_data['dst_street'] = ''
    context.user_data['dst_house'] = ''
    context.user_data['src_house'] = ''
    return await _to_the_get_point_a(update, context)

def order_history(update, context):
    bot_user = get_user_by_update(update)
    years = filter_years_of_client_orders(bot_user)
    if years: 
        reply_markup = order_years_keyboard(update, years)
        text = get_word('select year of order', update)
        msg = bot_send_message(update, context, text, reply_markup=reply_keyboard_remove())
        bot_delete_message(update, context, msg.message_id)
        msg=bot_send_message(update, context, text, reply_markup=reply_markup)
        context.user_data['last_msg_id'] = msg.message_id
        return GET_YEAR
    else:
        text = get_word('not available orders yet', update)
        update_message_reply_text(update, text)
        main_menu(update, context)

def bonus(update, context):
    phone = get_object_by_update(update).phone
    balance = client_bonus_count(phone)
    text = get_word('your balance', update).format(balance)
    update_message_reply_text(update, text)

def leave_feedback(update, context):
    text = get_word('write your feedback', update)
    markup = reply_keyboard_markup([[get_word('main menu', update)]])
    msg = update_message_reply_text(update, text, markup)
    set_last_msg_and_markup(context, msg, markup)
    return GET_FEEDBACK






async def newsletter_update(update: NewsletterUpdate, context: CustomContext):
    bot = context.bot
    while True:
        try:
            if not (update.photo or update.video or update.document or update.location):
                # send text message
                message = await bot.send_message(
                    chat_id=update.user_id,
                    text=update.text,
                    reply_markup=update.reply_markup,
                    parse_mode=ParseMode.HTML
                )

            if update.photo:
                # send photo
                message = await bot.send_photo(
                    update.user_id,
                    update.photo,
                    caption=update.text,
                    reply_markup=update.reply_markup,
                    parse_mode=ParseMode.HTML,
                )
            if update.video:
                # send video
                message = await bot.send_video(
                    update.user_id,
                    update.video,
                    caption=update.text,
                    reply_markup=update.reply_markup,
                    parse_mode=ParseMode.HTML,
                )
            if update.document:
                # send document
                message = await bot.send_document(
                    update.user_id,
                    update.document,
                    caption=update.text,
                    reply_markup=update.reply_markup,
                    parse_mode=ParseMode.HTML,
                )
            if update.location:
                # send location
                message = await bot.send_location(
                    chat_id=update.user_id,
                    latitude=update.location.get('latitude'),
                    longitude=update.location.get('longitude')
                )
            if update.pin_message:
                await bot.pin_chat_message(chat_id=update.user_id, message_id=message.message_id)

            # set last msg id and reply markup
            if update.reply_markup:
                await set_last_msg_and_markup(context, message, update.reply_markup)
            break
        except TimedOut:
            await asyncio.sleep(0.5)
            continue


###############################################################################################
###############################################################################################
###############################################################################################
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: CustomContext):
    # restart db connection if error is "connection already closed"
    if "connection already closed" in str(context.error):
        await sync_to_async(close_old_connections)()
        return


    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    )
    error_message = f"{html.escape(tb_string)}"

    # Finally, send the message
    try:
        await context.bot.send_message(
            chat_id=206261493, text=message, parse_mode=ParseMode.HTML
        )
        for i in range(0, len(error_message), 4000):
            await context.bot.send_message(
                chat_id=206261493, text=f"<pre>{error_message[i:i+4000]}</pre>", parse_mode=ParseMode.HTML
            )
    except Exception as ex:
        print(ex)
