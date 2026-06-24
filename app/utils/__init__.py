from datetime import datetime, date, timedelta, time
from typing import Optional
import requests
import json
import aiohttp


async def get_user_ip(request):
    x_forwarded_for = await request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = await request.META.get('REMOTE_ADDR')
    return ip


async def datetime_now():
    now = datetime.now()
    return now


async def time_now():
    now = datetime.now()
    return now.time()


async def today():
    today = date.today()
    return today


def parse_time(text: str) -> Optional[time]:
    """
    Parse a string like '9:45', '09:45', '21:50' into a datetime.time object.

    Returns None if the input is not a valid HH:MM time string.
    """
    if not text or not isinstance(text, str):
        return None

    text = text.strip()
    parts = text.split(":")

    if len(parts) != 2:
        return None

    hour_str, minute_str = parts

    if not hour_str.isdigit() or not minute_str.isdigit():
        return None

    hour = int(hour_str)
    minute = int(minute_str)

    if not (0 <= hour <= 23):
        return None
    if not (0 <= minute <= 59):
        return None

    return time(hour=hour, minute=minute)


async def send_request(
    url,
    data=None,
    headers=None,
    type='get',
    *,
    method=None,
    session=None,
    timeout=30,
) -> dict:
    if isinstance(headers, str) and method is None and type == 'get':
        method = headers
        headers = None

    request_method = (method or type).lower()

    async def request(client_session):
        if request_method == 'get':
            response_context = client_session.get(
                url, headers=headers, params=data)
        else:
            response_context = client_session.post(
                url, headers=headers, json=data)

        async with response_context as response:
            response: aiohttp.ClientResponse
            response.raise_for_status()
            try:
                return await response.json(content_type=None)
            except (aiohttp.ContentTypeError, ValueError):
                response_text = await response.text()
                return json.loads(response_text)

    if session is not None:
        return await request(session)

    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as client_session:
        return await request(client_session)


class DictToClass:
    def __init__(self, dictionary=None):
        if dictionary is not None:
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    # If the value is a dictionary, recursively create an instance of the class
                    setattr(self, key, DictToClass(value))
                elif isinstance(value, list):
                    # If the value is a list, process each item in the list
                    setattr(self, key, [DictToClass(item) if isinstance(
                        item, dict) else item for item in value])
                else:
                    # Otherwise, set the attribute to the value
                    setattr(self, key, value)

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            # If the value is a dictionary, convert it to an instance of DictToClass
            super().__setattr__(key, DictToClass(value))
        elif isinstance(value, list):
            # If the value is a list, convert any dictionaries in the list to DictToClass
            super().__setattr__(key, [DictToClass(item) if isinstance(
                item, dict) else item for item in value])
        else:
            # Otherwise, just set the attribute
            super().__setattr__(key, value)

    def __getattr__(self, key):
        # If the attribute doesn't exist, automatically create a DictToClass instance
        # This allows you to add nested attributes dynamically
        self.__setattr__(key, DictToClass())
        return self.__dict__[key]

    @property
    async def to_dict(self):
        # This method converts the class instance back into a dictionary
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictToClass):
                # If the value is another instance of DictToClass, recursively call to_dict
                result[key] = await value.to_dict
            elif isinstance(value, list):
                # If the value is a list, ensure each element is converted back to a dictionary if necessary
                result[key] = [
                    await item.to_dict if isinstance(item, DictToClass) else item for item in value
                ]
            else:
                # Otherwise, just add the key-value pair to the result dictionary
                result[key] = value
        return result

    def __repr__(self):
        # This will allow a readable representation of the object when printed
        return f"{self.__class__.__name__}({self.__dict__})"


CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
    'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'j',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 's',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sh',
    'ъ': '', 'ы': 'i', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',
}

def transliterate(text: str) -> str:
    return ''.join(CYRILLIC_TO_LATIN.get(c, c) for c in text.lower())
