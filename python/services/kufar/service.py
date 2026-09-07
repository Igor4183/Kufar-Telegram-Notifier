import aiohttp
from datetime import datetime

from services.managers import ConfigManager

from services.managers.models import Query
from .models import (
    AccountParameter,
    Ad,
    AdParameter,
    CalculatorPrice,
    Image,
    KufarSearchResponse,
    PaidServices,
    Pagination,
    PaginationPage,
    ShowParameters,
)
from .query_builder import build_search_params


class KufarService:
    def __init__(self, session: aiohttp.ClientSession, config_manager: ConfigManager):
        self.session = session
        self.base_url = config_manager.get_kufar_api()
        self.timeout = config_manager.get_kufar_timeout()
        self.default_max_price = config_manager.get_kufar_default_max_price()

    async def get_ads(self, query: Query) -> KufarSearchResponse:
        params = build_search_params(query, self.default_max_price)

        async with self.session.get(
            self.base_url, params=params, timeout=self.timeout  # type: ignore
        ) as response:
            response.raise_for_status()
            data = await response.json()

        return self._parse_response(data)

    @classmethod
    def _parse_response(cls, data: dict) -> KufarSearchResponse:
        return KufarSearchResponse(
            ads=[cls._parse_ad(ad) for ad in data.get("ads", [])],
            page_type=data.get("page_type", ""),
            pagination=cls._parse_pagination(data.get("pagination", {})),
            total=int(data.get("total", 0)),
            raw_data=data,
        )

    @classmethod
    def _parse_ad(cls, data: dict) -> Ad:
        return Ad(
            account_id=str(data.get("account_id", "")),
            ad_id=str(data["ad_id"]),
            list_id=int(data.get("list_id", data["ad_id"])),
            message_id=str(data.get("message_id", "")),
            ad_link=str(data.get("ad_link", "")),
            type=str(data.get("type", "")),
            subject=str(data.get("subject", "")),
            body=data.get("body"),
            body_short=data.get("body_short"),
            list_time=cls._parse_datetime(data["list_time"]),
            price_byn=str(data.get("price_byn", "")),
            price_usd=str(data.get("price_usd", "")),
            currency=str(data.get("currency", "")),
            remuneration_type=str(data.get("remuneration_type", "")),
            calculator=cls._parse_calculator(data.get("calculator", [])),
            category=str(data.get("category", "")),
            company_ad=bool(data.get("company_ad", False)),
            account_parameters=cls._parse_account_parameters(
                data.get("account_parameters", [])
            ),
            ad_parameters=cls._parse_ad_parameters(data.get("ad_parameters", [])),
            images=cls._parse_images(data.get("images", [])),
            is_mine=bool(data.get("is_mine", False)),
            phone_hidden=bool(data.get("phone_hidden", False)),
            feedback_info=data.get("feedback_info"),
            paid_services=cls._parse_paid_services(data.get("paid_services", {})),
            show_parameters=cls._parse_show_parameters(data.get("show_parameters", {})),
            raw_data=data,
        )

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _parse_images(images: list[dict]) -> list[Image]:
        return [
            Image(
                id=str(image.get("id", "")),
                media_storage=str(image.get("media_storage", "")),
                path=str(image.get("path", "")),
                yams_storage=bool(image.get("yams_storage", False)),
            )
            for image in images
        ]

    @staticmethod
    def _parse_calculator(calculator: list[dict]) -> list[CalculatorPrice]:
        return [
            CalculatorPrice(
                currency=str(item.get("currency", "")),
                price=str(item.get("price", "")),
                price_per_meter=(
                    str(item["price_per_meter"])
                    if item.get("price_per_meter") is not None
                    else None
                ),
            )
            for item in calculator
        ]

    @staticmethod
    def _parse_account_parameters(parameters: list[dict]) -> list[AccountParameter]:
        return [
            AccountParameter(
                label=item.get("pl"),
                value_label=item.get("vl"),
                parameter=str(item.get("p", "")),
                value=item.get("v"),
                parameter_url=item.get("pu"),
            )
            for item in parameters
        ]

    @staticmethod
    def _parse_ad_parameters(parameters: list[dict]) -> list[AdParameter]:
        return [
            AdParameter(
                label=item.get("pl"),
                value_label=item.get("vl"),
                parameter=str(item.get("p", "")),
                value=item.get("v"),
                parameter_url=item.get("pu"),
            )
            for item in parameters
        ]

    @staticmethod
    def _parse_paid_services(data: dict) -> PaidServices:
        return PaidServices(
            halva=bool(data.get("halva", False)),
            highlight=bool(data.get("highlight", False)),
            polepos=bool(data.get("polepos", False)),
            ribbons=data.get("ribbons"),
        )

    @staticmethod
    def _parse_show_parameters(data: dict) -> ShowParameters:
        return ShowParameters(
            show_call=bool(data.get("show_call", False)),
            show_chat=bool(data.get("show_chat", False)),
            show_import_link=bool(data.get("show_import_link", False)),
            show_web_shop_link=bool(data.get("show_web_shop_link", False)),
        )

    @staticmethod
    def _parse_pagination(data: dict) -> Pagination:
        return Pagination(
            pages=[
                PaginationPage(
                    label=str(page.get("label", "")),
                    num=int(page.get("num", 0)),
                    token=page.get("token"),
                )
                for page in data.get("pages", [])
            ]
        )
