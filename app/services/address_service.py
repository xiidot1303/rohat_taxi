from __future__ import annotations

from typing import Iterable

from django.db.models import Q, QuerySet
from django.shortcuts import aget_object_or_404

from app.models import City, Street
from app.utils import *


async def get_or_create_city(title: str, city_id: int) -> City:
    city, _ = await City.objects.aget_or_create(
        city_id=city_id,
        defaults={"title": title},
    )

    if city.title != title:
        city.title = title
        await city.asave(update_fields=["title"])

    return city


async def filter_cities() -> list[City]:
    return [city async for city in City.objects.all()]


async def cities_all() -> list[City]:
    return await filter_cities()


async def get_or_create_street(title: str, city: City) -> Street:
    street, _ = await Street.objects.aget_or_create(
        title=title,
        title_normalized=transliterate(title),
        city=city,
    )
    return street


async def bulk_get_or_create_streets(
    titles: Iterable[str],
    city: City,
) -> int:
    created_or_found = 0
    seen_titles: set[str] = set()

    for title in titles:
        normalized_title = str(title).strip()
        if not normalized_title or normalized_title in seen_titles:
            continue

        await get_or_create_street(normalized_title, city)
        seen_titles.add(normalized_title)
        created_or_found += 1

    return created_or_found


async def get_street_by_pk(pk: int) -> Street:
    return await aget_object_or_404(Street, pk=pk)


def build_streets_title_query(
    city: City | None,
    text_en: str,
    text_ru: str,
    text: str,
) -> QuerySet[Street]:
    streets = (
        Street.objects.filter(city=city)
        if city
        else Street.objects.all()
    )
    return streets.filter(
        Q(title__iregex=text_en)
        | Q(title__iregex=text_ru)
        | Q(title__icontains=text)
    )


async def filter_streets_by_title_regex(
    city: City | None,
    text_en: str,
    text_ru: str,
    text: str,
) -> list[Street]:
    query = build_streets_title_query(city, text_en, text_ru, text)
    return [street async for street in query]


async def get_city_by_title(title: str) -> City | None:
    return await City.objects.filter(title=title).afirst()
