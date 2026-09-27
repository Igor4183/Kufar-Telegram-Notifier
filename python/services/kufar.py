import aiohttp
import json

from datetime import datetime
from typing import Any
from yarl import URL

from services.models import Query, Ad, Image, AccountParameter, AdParameter
from services.config_manager import ConfigManager
from services.path_manager import PathManager
from utils.logger import Logger


class KufarService:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.config_manager = ConfigManager()
        self.path_manager = PathManager()
        self.url_builder = UrlBuilder(self.config_manager)
        self.ad_parser = AdParser()

    async def getAds(self, query: Query) -> list[Ad] | None:
        params = None
        url = self.config_manager.kufar_api

        if query.url is not None:
            url += query.url
        else:
            params = self.url_builder.build_search_params(query)
        self.path_manager.kufar_jsons.mkdir(parents=True, exist_ok=True)

        async with self.session.get(
            url,
            params=params,
            timeout=self.config_manager.kufar_timeout,
        ) as response:
            response.raise_for_status()
            data: dict[str, Any] = await response.json()

            json_id = get_next_kufar_json_id()
            json_path = self.path_manager.kufar_jsons / f"{json_id}.json"

            with json_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            if "error" in data:
                Logger.warning(
                    None,
                    f"kufar api return error page [{json_id}.json], [query_id: {query.query_id}]",
                )
            Logger.info(None, f"saved {json_id}.json")

            return self.ad_parser.get_ads(data, json_id)


class UrlBuilder:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def build_url(self, query: Query) -> str:
        params = self.build_search_params(query)
        return str(URL(self.config_manager.kufar_api).with_query(params))

    def _add_parameter(
        self, params: dict[str, Any], parameter: str, value: Any
    ) -> None:
        if value is not None:
            params[parameter] = value

    def _add_boolean_parameter(
        self, params: dict[str, Any], parameter: str, value: bool | None
    ) -> None:
        if value is True:
            params[parameter] = "1"

    def _build_price(self, query: Query, default_max_price: int) -> str | None:
        if query.price_min is None and query.price_max is None:
            return None

        minimum = 0 if query.price_min is None else query.price_min * 100
        maximum = (
            default_max_price if query.price_max is None else query.price_max * 100
        )

        return f"r:{minimum},{maximum}"

    def _build_sort(self, query: Query) -> str | None:
        if query.sort_type == 1:
            return "prc.d"

        if query.sort_type == 2:
            return "prc.a"

        return None

    def build_search_params(self, query: Query) -> dict[str, Any]:
        params: dict[str, Any] = {}

        self._add_parameter(params, "query", query.tag)
        self._add_parameter(params, "lang", query.language)
        self._add_parameter(params, "size", query.limit)
        self._add_parameter(
            params,
            "prc",
            self._build_price(
                query,
                self.config_manager.kufar_default_max_price,
            ),
        )
        self._add_parameter(params, "cur", query.currency)
        self._add_parameter(params, "cat", query.sub_category)
        self._add_parameter(params, "prn", query.category)

        self._add_boolean_parameter(params, "ot", query.only_title_search)
        self._add_boolean_parameter(params, "dle", query.kufar_delivery_required)
        self._add_boolean_parameter(params, "sde", query.kufar_payment_required)
        self._add_boolean_parameter(params, "hlv", query.kufar_halva_required)
        self._add_boolean_parameter(params, "oph", query.only_with_photos)
        self._add_boolean_parameter(params, "ovi", query.only_with_videos)
        self._add_boolean_parameter(params, "pse", query.only_with_exchange_available)

        self._add_parameter(params, "sort", self._build_sort(query))
        self._add_parameter(params, "cnd", query.condition)
        self._add_parameter(params, "cmp", query.seller_type)
        self._add_parameter(params, "rgn", query.region)

        if query.areas:
            params["ar"] = f"v.or:{','.join(map(str, query.areas))}"

        return params


class AdParser:
    def get_ads(self, data: dict[str, Any], json_id: int) -> list[Ad]:
        return [self._parse_ad(ad, json_id) for ad in data["ads"]]

    def _parse_ad(self, data: dict[str, Any], json_id: int) -> Ad:
        return Ad(
            account_id=data.get("account_id", -1),
            ad_id=data.get("ad_id", -1),
            json_id=json_id,
            ad_link=data.get("ad_link"),
            type=data.get("type"),
            subject=data.get("subject"),
            body=data.get("body"),
            body_short=data.get("body_short"),
            list_time=self._parse_datetime(data.get("list_time", 0)),
            price_byn=data.get("price_byn"),
            price_usd=data.get("price_usd"),
            currency=data.get("currency"),
            remuneration_type=data.get("remuneration_type"),
            category=data.get("category"),
            company_ad=data.get("company_ad"),
            images=[self._parse_image(image) for image in data.get("images", [])],
            account_parameters=[
                self._parse_account_parameter(parameter)
                for parameter in data.get("account_parameters", [])
            ],
            ad_parameters=[
                self._parse_ad_parameter(parameter)
                for parameter in data.get("ad_parameters", [])
            ],
            is_mine=data.get("is_mine"),
            phone_hidden=data.get("phone_hidden"),
        )

    def _parse_account_parameter(self, data: dict[str, Any]) -> AccountParameter:
        return AccountParameter(
            label=data["pl"],
            value_label=data["vl"],
            parameter=data["p"],
            value=data["v"],
            parameter_url=data["pu"],
        )

    def _parse_ad_parameter(self, data: dict[str, Any]) -> AdParameter:
        return AdParameter(
            label=data["pl"],
            value_label=data["vl"],
            parameter=data["p"],
            value=data["v"],
            parameter_url=data["pu"],
        )

    def _parse_image(self, data: dict[str, Any]) -> Image:
        return Image(
            id=data["id"],
            media_storage=data["media_storage"],
            path=data["path"],
            yams_storage=data["yams_storage"],
        )

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_next_kufar_json_id() -> int:
    path_manager = PathManager()
    path_manager.kufar_jsons.mkdir(parents=True, exist_ok=True)

    json_ids = [
        int(path.stem)
        for path in path_manager.kufar_jsons.glob("*.json")
        if path.stem.isdigit()
    ]

    return max(json_ids, default=0) + 1
