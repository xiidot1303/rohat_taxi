from bot.bot import *
from app.models import Feedback


async def leave_feedback(update: Update, context: CustomContext):
    text = context.words.write_your_feedback
    markup = await build_keyboard(context, [], 1, back_button=False)
    await update.effective_message.reply_html(text, reply_markup=markup)
    return GET_FEEDBACK


async def get_feedback(update: Update, context: CustomContext):
    feedback_text = update.effective_message.text
    if len(feedback_text) > 2500:
        await update.effective_message.reply_html(context.words.feedback_too_long)
        return GET_FEEDBACK
    
    bot_user = await get_object_by_update(update)
    await Feedback.objects.acreate(
        bot_user = bot_user,
        message = feedback_text
    )

    text = context.words.your_feedback_accepted
    await update.effective_message.reply_html(text)
    await main_menu(update, context)
    return ConversationHandler.END


async def start(update: Update, context: CustomContext):
    await main_menu(update, context)
    return ConversationHandler.END