from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Literal

import aiohttp

from config import DEBUG, SCAT_API_KEY, SCAT_API_URL

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
            request = session.get if method == "get" else session.post
            kwargs = {"params" if method == "get" else "json": request_payload}
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
            raise ScatServiceError(
                "SCAT API response is missing response body")
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
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    ) -> ScatOrderPreCost:
        payload: dict[str, Any] = {"phone": phone}
        payload.update(self._location_payload(
            "src", src, src_street, src_house, src_lat, src_lon))
        payload.update(self._location_payload(
            "dst", dst, dst_street, dst_house, dst_lat, dst_lon))

        if service_id is not None:
            payload["service_id"] = service_id

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
            "Could not calculate SCAT order pre-cost") from last_error

    @staticmethod
    def _location_payload(
        prefix: Literal["src", "dst"],
        kind: AddressKind | None,
        street: str | None,
        house: str | None,
        lat: float | str | None,
        lon: float | str | None,
    ) -> dict[str, Any]:
        if not kind:
            return {}

        if kind == "location":
            if lat is None or lon is None:
                raise ValueError(
                    f"{prefix}_lat and {prefix}_lon are required for location")
            return {f"{prefix}_lat": lat, f"{prefix}_lon": lon}

        if kind == "address":
            if not street or not house:
                raise ValueError(
                    f"{prefix}_street and {prefix}_house "
                    "are required for address",
                )
            return {f"{prefix}_street": street, f"{prefix}_house": house}

        raise ValueError(f"Unsupported {prefix} type: {kind}")

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
        self,
        phone: str,
        token: str,
    ) -> tuple[bool, str | None]:
        response = await self._request(
            "order",
            method="post",
            payload={
                "phone": phone,
                "token": token,
                "moderation_required": "no",
                "comment": self._order_comment(),
            },
        )

        if response.get("status") == "DONE":
            return True, self._response_body(response).get("uuid")

        if response.get("status") == "ERROR":
            error = response.get("error") or {}
            return False, error.get("message", "SCAT API returned an error")

        return False, "Unexpected SCAT API status"

    @staticmethod
    def _order_comment() -> str:
        if str(DEBUG).lower() in {"1", "true", "yes", "on"}:
            return "TEST Гайрат акага"
        return "From Telegram Bot"

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
    )
    return pre_cost.as_tuple()


async def region_by_coordinates_api(
    lat: float | str,
    lon: float | str,
) -> Any | None:
    return await get_scat_client().region_by_coordinates(lat, lon)


async def create_order_api(phone: str, token: str) -> tuple[bool, str | None]:
    return await get_scat_client().create_order(phone, token)


async def cancel_order_api(uuid: str) -> bool:
    return await get_scat_client().cancel_order(uuid)


async def client_bonus_count(phone: str) -> Any:
    return await get_scat_client().client_bonus_count(phone)
