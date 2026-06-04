from django.db.models import Q
from bot.bot import *
from app.services.address_service import search_streets_by_title_similarity


async def get_inline_query(update: Update, context: CustomContext):
    text = update.inline_query.query

    bot_user = await get_object_by_user_id(update.effective_user.id)
    streets = await search_streets_by_title_similarity(await bot_user.get_city, text)
    article = [
        await inlinequeryresultarticle(
            obj.title, 
            description=await address_description_for_query_string(update, (await obj.get_city).title),
            title_id=obj.pk
            ) 
            async for obj in streets[:100]
    ]
    if not article:
        article = [
            await inlinequeryresultarticle(context.words.not_found)
        ]
    
    await update_inline_query_answer(update, article)

