from django.db.models import Q
from bot.bot import *
from transliterate import translit

def get_inline_query(update, context):
    text = update.inline_query.query
    text_ru = translit(text, 'ru')
    try:
        text_en = translit(text, reversed=True)
    except:
        text_en = text
    text_en = regexing_en(text_en)
    text_ru = regexing_ru(text_ru)
    bot_user = get_object_by_user_id(update.inline_query.from_user.id)
    streets = filter_streets_by_title_regex(bot_user.city, text_en, text_ru, text)[:100]
    article = [
        inlinequeryresultarticle(
            obj.title, 
            description=address_description_for_query_string(update, obj.city.title),
            title_id=obj.pk
            ) 
            for obj in streets
    ]
    if not article:
        article = [
            inlinequeryresultarticle(get_word('not found', chat_id=update.inline_query.from_user.id))
        ]
    
    update_inline_query_answer(update, article)


def regexing_en(text):
    list_couples = [
        'ao', 'xh', 'ie', 'qk', 'cs', 'jy'
    ]

    for i in list_couples:
        text = text.replace(i[0], f'({i[0]}|{i[1]})')
        text = text.replace(i[1], f'({i[0]}|{i[1]})')
        text = text.replace(f'{i[0]}|({i[0]}|{i[1]})', f'{i[0]}|{i[1]}')

    return text

def regexing_ru(text):
    list_couples = [
        'ао', 'её', 'ыи', 'юу', 'щш', ['л', 'ль']
    ]

    for i in list_couples:
        text = text.replace(i[0], f'({i[0]}|{i[1]})')
        text = text.replace(i[1], f'({i[0]}|{i[1]})')
        text = text.replace(f'{i[0]}|({i[0]}|{i[1]})', f'{i[0]}|{i[1]}')

    return text