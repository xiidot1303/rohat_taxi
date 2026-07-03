from bot.bot import *
from app.services.address_service import search_streets_by_title_similarity
from app.services.order_service import filter_completed_orders_by_user_id


async def get_inline_query(update: Update, context: CustomContext):
    text = update.inline_query.query or ""

    bot_user = await get_object_by_user_id(update.effective_user.id)
    streets = await search_streets_by_title_similarity(await bot_user.get_city, text)
    completed_orders = await filter_completed_orders_by_user_id(update.effective_user.id)

    order_articles = []
    async for order in completed_orders:
        if not order.address:
            continue
        if text and text.lower() not in order.address.lower():
            continue

        order_articles.append(
            await inlinequeryresultarticle(
                order.address,
                description=f"{context.words.order_time}: {order.end_time.strftime('%d.%m.%Y %H:%M')}",
                message_content=f"address_from_order-{order.pk}",
            )
        )

    street_articles = [
        await inlinequeryresultarticle(
            obj.title,
            description=await address_description_for_query_string(update, (await obj.get_city).title),
            title_id=obj.pk,
        )
        async for obj in streets[:100]
    ]

    article = order_articles + street_articles

    if not article:
        article = [
            await inlinequeryresultarticle(context.words.not_found)
        ]

    await update_inline_query_answer(update, article)

