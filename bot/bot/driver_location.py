from bot.bot import *
from app.services.scat_service import order_info as get_order_info, get_driver_coordinates
from app.models import Order, Cheque


async def get_driver_location(update: Update, context: CustomContext):
    query = update.callback_query
    *args, order_id = str(query.data).split("-")
    # check that already running job with order id
    if context.job_queue.get_jobs_by_name(f"driver_coordinates-{order_id}"):
        await query.answer()
        return

    order: Order = await Order.objects.aget(id=order_id)

    order_info: dict = await get_order_info(order.uuid)
    driver_id = order_info.get("driver_id")
    
    lat, lon = await get_driver_coordinates(driver_id)

    message = await update.effective_message.reply_location(
        latitude=lat,
        longitude=lon,
        live_period=1800
    )

    context.job_queue.run_repeating(
        update_driver_coordinates,
        interval=30,
        first=30,
        chat_id=update._effective_chat.id,
        name=f"driver_coordinates-{order.pk}",
        data={
            "driver_id": driver_id,
            "message_id": message.message_id,
            "order_id": order.order_id
        }
    )

    await query.edit_message_reply_markup()


async def update_driver_coordinates(context: CustomContext):
    data: dict = context.job.data
    driver_id = data.get("driver_id")
    message_id = data.get("message_id")
    order_id = data.get("order_id")
    chat_id = context.job.chat_id

    # check order status
    cheque: Cheque = await Cheque.objects.aget(id=order_id)
    if cheque.status_code not in ["10", "11"]:
        context.job.schedule_removal()
        await context.bot.stop_message_live_location(
            chat_id=chat_id,
            message_id=message_id,
        )
        return

    lat, lon = await get_driver_coordinates(driver_id)

    try:
        await context.bot.edit_message_live_location(
            chat_id=chat_id,
            message_id=message_id,
            latitude=lat,
            longitude=lon
        )
    except:
        pass
