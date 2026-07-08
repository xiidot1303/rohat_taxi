import logging

from asgiref.sync import async_to_sync
from app.models import ExtraService, City
from app.services.address_service import filter_cities
from app.services.scat_service import get_services_api, get_extra_services

logger = logging.getLogger(__name__)


async def update_extra_services_async() -> int:
    for city in await filter_cities():
        try:
            service_id = city.service_id
            extra_services = await get_extra_services(service_id=service_id)
            for extra_service in extra_services:
                title_uz = extra_service.get("name")
                title_ru = extra_service.get("name")
                service_id = extra_service.get("id")
                price = extra_service.get("price")

                if not all([title_uz, title_ru, service_id, price]):
                    logger.warning(
                        "Skipping SCAT extra service with missing data: %s",
                        extra_service,
                    )
                    continue

                await ExtraService.objects.aupdate_or_create(
                    service_id=service_id,
                    city=city,
                    defaults={
                        "title_uz": title_uz,
                        "title_ru": title_ru,
                        "price": price,
                    },
                )
        except Exception:
            logger.exception(
                "Failed to update SCAT extra services for city_id=%s",
                city.city_id,
            )


def update_extra_services() -> int:
    return async_to_sync(update_extra_services_async)()