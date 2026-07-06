from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Literal

import aiohttp

from config import DEBUG, SCAT_API_KEY, SCAT_API_URL
import json
from datetime import datetime
from zoneinfo import ZoneInfo

AddressKind = Literal["location", "address"]

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 0.3


class ScatServiceError(RuntimeError):
    """Raised when the SCAT API request or response is not valid."""


@dataclass(slots=True)
class ScatOrderPreCost:
    amount: Any
    distance: Any
    token: str

    def as_tuple(self) -> tuple[Any, Any, str]:
        return self.amount, self.distance, self.token


class ScatClient:
    def __init__(
        self,
        api_url: str = SCAT_API_URL,
        api_key: str = SCAT_API_KEY,
        *,
        timeout: int | float = DEFAULT_TIMEOUT_SECONDS,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        if not api_url:
            raise ScatServiceError("SCAT_API_URL is not configured")
        if not api_key:
            raise ScatServiceError("SCAT_API_KEY is not configured")

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = session

    def _url(self, endpoint: str) -> str:
        return f"{self.api_url}/{endpoint.lstrip('/')}"

    def _base_payload(self) -> dict[str, Any]:
        return {"api_key": self.api_key}

    async def _request(
        self,
        endpoint: str,
        *,
        method: Literal["get", "post"] = "get",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request_payload = self._base_payload()
        if payload:
            request_payload.update(payload)
        async def send(session: aiohttp.ClientSession) -> dict[str, Any]:
            if method == "get":
                kwargs = {"params": request_payload}
                request = session.get
            else:
                kwargs = {"params": self._base_payload(), "data": request_payload}
                request = session.post
            async with request(self._url(endpoint), **kwargs) as response:
                response.raise_for_status()
                return await self._decode_response(response)

        if self.session is not None:
            return await send(self.session)

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            return await send(session)

    @staticmethod
    async def _decode_response(
        response: aiohttp.ClientResponse,
    ) -> dict[str, Any]:
        try:
            data = await response.json(content_type=None)
        except (aiohttp.ContentTypeError, ValueError) as exc:
            await response.text()
            raise ScatServiceError("SCAT API returned invalid JSON") from exc

        if not isinstance(data, dict):
            raise ScatServiceError("SCAT API returned an unexpected payload")
        return data

    @staticmethod
    def _response_body(data: dict[str, Any]) -> dict[str, Any]:
        body = data.get("response")
        if not isinstance(body, dict):
            error = data.get("error")
            if isinstance(error, dict) and error.get("message"):
                raise ScatServiceError(str(error["message"]))
            raise ScatServiceError("SCAT API response is missing response body")
        return body

    async def services(self) -> Any:
        response = await self._request("services")
        return self._response_body(response).get("services", [])

    async def streets(self, city_id: int | str) -> Any:
        response = await self._request("streets", payload={"city_id": city_id})
        return self._response_body(response).get("streets", [])

    async def calculate_order_pre_cost(
        self,
        *,
        phone: str,
        src: AddressKind | None,
        dst: AddressKind | None,
        src_street: str | None = None,
        src_house: str | None = None,
        dst_street: str | None = None,
        dst_house: str | None = None,
        src_lat: float | str | None = None,
        src_lon: float | str | None = None,
        dst_lat: float | str | None = None,
        dst_lon: float | str | None = None,
        service_id: int | str | None = None,
        pre_order_datetime: datetime | None = None,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    ) -> ScatOrderPreCost:
        payload: dict[str, Any] = {"phone": phone}
        payload["way_points"] = json.dumps(self._way_points_payload(
            src, dst, src_street, src_house, dst_street, 
            dst_house, src_lat, src_lon, dst_lat, dst_lon,
        ), ensure_ascii=False)

        if service_id is not None:
            payload["service_id"] = service_id
        
        if pre_order_datetime:
            # convert to UTC time zone
            dt_utc = pre_order_datetime.astimezone(ZoneInfo("UTC"))
            payload["pre_order_time_utc"] = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
        last_error: Exception | None = None
        for attempt in range(1, retry_attempts + 1):
            try:
                response = await self._request(
                    "order/pre_cost",
                    payload=payload,
                )
                body = self._response_body(response)
                return ScatOrderPreCost(
                    amount=body["amount"],
                    distance=body["distance"],
                    token=body["token"],
                )
            except (
                KeyError,
                ScatServiceError,
                aiohttp.ClientError,
                asyncio.TimeoutError,
            ) as exc:
                last_error = exc
                if attempt == retry_attempts:
                    break
                await asyncio.sleep(DEFAULT_RETRY_DELAY_SECONDS * attempt)

        raise ScatServiceError(
            "Could not calculate SCAT order pre-cost"
        ) from last_error

    @staticmethod
    def _way_points_payload(
        src: AddressKind | None,
        dst: AddressKind | None,
        src_street: str | None = None,
        src_house: str | None = None,
        dst_street: str | None = None,
        dst_house: str | None = None,
        src_lat: float | str | None = None,
        src_lon: float | str | None = None,
        dst_lat: float | str | None = None,
        dst_lon: float | str | None = None,
    ):
        way_points = []

        if src == "location":
            if src_lat is None or src_lon is None:
                raise ValueError("src_lat and src_lon are required for location")
            way_points.append({"latitude": float(src_lat), "longitude": float(src_lon)})
        elif src == "address":
            if not src_street:
                raise ValueError(
                    "src_street are required for address",
                )
            way_points.append({"name": src_street, "street": src_street, "house": src_house})

        if dst == "location":
            if dst_lat is None or dst_lon is None:
                raise ValueError("dst_lat and dst_lon are required for location")
            way_points.append({"latitude": float(dst_lat), "longitude": float(dst_lon)})
        elif dst == "address":
            if not dst_street:
                raise ValueError(
                    "dst_street are required for address",
                )
            way_points.append({"name": dst_street, "street": dst_street, "house": dst_house})

        if way_points:
            return way_points
        else:
            raise ValueError(f"Unsupported src, dst type: {src}, {dst}")

    async def region_by_coordinates(
        self,
        lat: float | str,
        lon: float | str,
    ) -> Any | None:
        response = await self._request(
            "region_by_coord",
            payload={"lat": lat, "lon": lon},
        )
        if response.get("status") != "DONE":
            return None
        return self._response_body(response).get("id")

    async def create_order(
        self, token: str, service_id: int, comment: str = ""
    ) -> tuple[bool, str | None]:
        response = await self._request(
            "order",
            method="post",
            payload={
                "token": token,
                "moderation_required": "no",
                "comment": self._order_comment(comment),
                "service_id": service_id,
            },
        )

        if response.get("status") == "DONE":
            return True, self._response_body(response).get("uuid")

        if response.get("status") == "ERROR":
            error = response.get("error") or {}
            return False, error.get("message", "SCAT API returned an error")

        return False, "Unexpected SCAT API status"

    @staticmethod
    def _order_comment(comment: str = "") -> str:
        if DEBUG:
            return f"TEST Гайрат акага\n\n{comment}"
        return comment

    async def cancel_order(self, uuid: str) -> bool:
        response = await self._request(
            "cancel_order",
            method="post",
            payload={"uuid": uuid},
        )
        return response.get("status") == "DONE"

    async def client_bonus_count(self, phone: str) -> Any:
        response = await self._request(
            "client/bonus/count",
            payload={"phone": phone},
        )
        return self._response_body(response).get("bonus", 0)

    async def order_info(self, uuid: str) -> Any:
        response = await self._request(
            "order",
            payload={"uuid": uuid},
        )
        return self._response_body(response)
    
    async def get_driver_coordinates(self, driver_id: str | int) -> Any:
        response = await self._request(
            "drivers",
            payload={"code": driver_id}
        )
        r_body = self._response_body(response)
        return r_body.get("lat"), r_body.get("lon")


def get_scat_client() -> ScatClient:
    return ScatClient()


async def get_services_api() -> Any:
    return await get_scat_client().services()


async def get_streets_api(city_id: int | str) -> Any:
    return await get_scat_client().streets(city_id)


async def calculate_order_pre_cost_api(
    phone: str,
    src: AddressKind | None,
    dst: AddressKind | None,
    src_street: str | None = None,
    src_house: str | None = None,
    dst_street: str | None = None,
    dst_house: str | None = None,
    src_lat: float | str | None = None,
    src_lon: float | str | None = None,
    dst_lon: float | str | None = None,
    dst_lat: float | str | None = None,
    service_id: int | str | None = None,
    pre_order_datetime: datetime | None = None
) -> tuple[Any, Any, str]:
    pre_cost = await get_scat_client().calculate_order_pre_cost(
        phone=phone,
        src=src,
        dst=dst,
        src_street=src_street,
        src_house=src_house,
        dst_street=dst_street,
        dst_house=dst_house,
        src_lat=src_lat,
        src_lon=src_lon,
        dst_lat=dst_lat,
        dst_lon=dst_lon,
        service_id=service_id,
        pre_order_datetime=pre_order_datetime
    )
    return pre_cost.as_tuple()


async def region_by_coordinates_api(
    lat: float | str,
    lon: float | str,
) -> Any | None:
    return await get_scat_client().region_by_coordinates(lat, lon)


async def create_order_api(token: str, service_id: int, passengers_count: int | None = None) -> tuple[bool, str | None]:
    comment = ""
    if passengers_count is not None:
        comment += "Количество пассажиров: {}\n".format(passengers_count)
    return await get_scat_client().create_order(token, service_id, comment=comment)


async def cancel_order_api(uuid: str) -> bool:
    return await get_scat_client().cancel_order(uuid)


async def client_bonus_count(phone: str) -> Any:
    return await get_scat_client().client_bonus_count(phone)


async def order_info(uuid: str) -> Any:
    """
    Get SCAT order information.

    Returns a dict with fields:
    - status (int): order status code.
    - message (str): status message.
    - driver_id (str | None): driver call sign.
    - start_time (str | None): start datetime in "%Y-%m-%d %H:%M:%S".
    - remaining_time (int | None): minutes until vehicle arrival.
    - amount (float | None): order cost.
    - rate_id (int | None): tariff identifier.
    - car_brand (str | None)
    - car_model (str | None)
    - car_color (str | None)
    - car_number (str | None)
    """
    return await get_scat_client().order_info(uuid)


async def get_driver_coordinates(driver_id: str | int) -> tuple[int, int]:
    return await get_scat_client().get_driver_coordinates(driver_id)
