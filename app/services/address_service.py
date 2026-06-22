from __future__ import annotations

from typing import Iterable

from django.db.models import Q, QuerySet
from django.shortcuts import aget_object_or_404
from django.contrib.postgres.search import TrigramSimilarity

from app.models import City, Street
from app.utils import *
from asgiref.sync import sync_to_async


async def get_or_create_city(title: str, city_id: int, service_id) -> City:
    city, _ = await City.objects.aget_or_create(
        service_id=service_id,
        defaults={
            "title": title,
            "city_id": city_id
        },
    )
    
    return city


async def filter_cities() -> list[City]:
    return [city async for city in City.objects.all()]


async def cities_all() -> list[City]:
    return await filter_cities()


async def get_or_create_street(title: str, city: City) -> Street:
    title = str(title).strip()
    street, created = await Street.objects.aget_or_create(
        title=title,
        city=city,
        defaults={"title_normalized": transliterate(title)},
    )
    if not created and not street.title_normalized:
        street.title_normalized = transliterate(title)
        await street.asave(update_fields=["title_normalized"])

    return street


async def bulk_get_or_create_streets(
    titles: Iterable[str],
    city: City,
) -> int:
    unique_titles = {str(title).strip() for title in titles if str(title).strip()}
    if not unique_titles:
        return 0

    existing_titles = {
        title
        async for title in Street.objects.filter(
            city=city,
            title__in=unique_titles,
        ).values_list("title", flat=True)
    }
    missing_titles = unique_titles - existing_titles
    if not missing_titles:
        return 0

    await Street.objects.abulk_create(
        [
            Street(
                title=title,
                title_normalized=transliterate(title),
                city=city,
            )
            for title in missing_titles
        ],
        ignore_conflicts=True,
    )
    return len(missing_titles)


async def get_street_by_pk(pk: int) -> Street:
    return await aget_object_or_404(Street, pk=pk)


def build_streets_title_query(
    city: City | None,
    text_en: str,
    text_ru: str,
    text: str,
) -> QuerySet[Street]:
    streets = Street.objects.filter(city=city) if city else Street.objects.all()
    return streets.filter(
        Q(title__iregex=text_en) | Q(title__iregex=text_ru) | Q(title__icontains=text)
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


@sync_to_async
def search_streets_by_title_similarity(city: City, text: str) -> QuerySet[Street]:
    title_norm = transliterate(text)
    query = Street.objects.filter(city__pk=city.pk)

    result = (
        query.annotate(similarity=TrigramSimilarity("title_normalized", title_norm))
        .filter(similarity__gt=0.1)
        .order_by("-similarity")
    )
    return result