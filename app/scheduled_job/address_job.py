from __future__ import annotations

import logging

from asgiref.sync import async_to_sync

from app.services.address_service import (
    bulk_get_or_create_streets,
    filter_cities,
    get_or_create_city,
)
from app.services.scat_service import get_services_api, get_streets_api

logger = logging.getLogger(__name__)


async def update_streets_async() -> int:
    updated_count = 0

    for city in await filter_cities():
        try:
            streets = await get_streets_api(city_id=city.city_id)
            updated_count += await bulk_get_or_create_streets(streets, city)
        except Exception:
            logger.exception(
                "Failed to update SCAT streets for city_id=%s",
                city.city_id,
            )

    return updated_count


async def update_cities_async() -> int:
    services = await get_services_api()
    updated_count = 0

    for service in services:
        try:
            city_id = service["city_id"]
            service_id = service["id"]
            title = service["name"]
        except KeyError:
            logger.warning(
                "Skipping SCAT service without city data: %s",
                service,
            )
            continue

        await get_or_create_city(title, city_id, service_id)
        updated_count += 1

    return updated_count


def update_streets() -> int:
    return async_to_sync(update_streets_async)()


def update_cities() -> int:
    return async_to_sync(update_cities_async)()
