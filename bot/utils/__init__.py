from bot.utils.bot_functions import *
from bot import CustomContext
import httpx
from config import YANDEX_GEOCODER_API_KEY

async def get_callback_query_data(update):
    data = await update.data
    *args, result = str(data).split('_')
    return result

async def get_location_coordinates(l):
    return l['latitude'], l['longitude']

async def split_text_and_text_id(msg):
    return msg.split('<>?')

async def get_last_msg_and_markup(context):
    return context.user_data['last_msg'], context.user_data['last_markup'] if 'last_markup' in context.user_data else None

async def remove_inline_keyboards_from_last_msg(update: Update, context: CustomContext):
    try:
        last_msg_id = context.user_data.get('last_msg_id')
        if last_msg_id:
            await bot_edit_message_reply_markup(update, context, last_msg_id)
        return True
    except Exception as e:
        print(e)
        return None

async def is_group(update):
    if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
        return True
    return False

async def save_and_get_photo(update, context):
    bot = context.bot
    photo_id = await bot.getFile(update.message.photo[-1].file_id)
    *args, file_name = str(photo_id.file_path).split('/')
    d_photo = await photo_id.download('files/photos/{}'.format(file_name))
    return str(d_photo).replace('files/', '')

async def set_last_msg_and_markup(context, msg=None, markup=None):
    context.user_data['last_msg_id'] = msg.message_id if msg else None
    context.user_data['last_markup'] = markup


async def get_address_by_coordinates(lat: float, lon: float) -> str | None:
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_GEOCODER_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "lang": "ru_RU",
            "results": 1,
        }
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        members = data["response"]["GeoObjectCollection"]["featureMember"]
        return members[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"] if members else None
    except Exception as e:
        return None