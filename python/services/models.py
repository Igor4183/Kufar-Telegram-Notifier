from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Ad:
    account_id: str
    ad_id: int
    json_id: int
    ad_link: str
    type: str
    subject: str
    body: str | None
    body_short: str | None
    list_time: datetime
    price_byn: str
    price_usd: str
    currency: str
    remuneration_type: str
    category: str
    company_ad: bool
    images: list[Image]
    account_parameters: list[AccountParameter]
    ad_parameters: list[AdParameter]
    is_mine: bool
    phone_hidden: bool

    @property
    def id(self) -> int:
        return self.ad_id

    @property
    def title(self) -> str:
        return self.subject

    @property
    def link(self) -> str:
        return self.ad_link

    def get_parameter(self, parameter: str) -> AdParameter | None:
        for item in self.ad_parameters:
            if item.parameter == parameter:
                return item

        return None

    def get_account_parameter(self, parameter: str) -> AccountParameter | None:
        for item in self.account_parameters:
            if item.parameter == parameter:
                return item


@dataclass
class AccountParameter:
    label: str | None
    value_label: str | list[str] | None
    parameter: str
    value: Any
    parameter_url: str | None


@dataclass
class AdParameter:
    label: str | None
    value_label: str | list[str] | None
    parameter: str
    value: Any
    parameter_url: str | None


@dataclass
class Image:
    id: str
    media_storage: str
    path: str
    yams_storage: bool

    @property
    def url(self) -> str:
        if self.yams_storage:
            return (
                "https://yams.kufar.by/api/v1/kufar-ads/images/"
                f"{self.id[:2]}/{self.id}.jpg?rule=pictures"
            )
        return f"https://{self.media_storage}1.kufar.by/v1/gallery/{self.path}"


@dataclass
class Query:
    chat_id: int
    tag: str | None = None
    query_id: int = -1
    delay: int = 0
    limit: int | None = None
    start_time: int | None = None
    only_title_search: bool = False
    price_min: int | None = None
    price_max: int | None = None
    language: str | None = None
    currency: str | None = None
    condition: int | None = None
    seller_type: int | None = None
    kufar_delivery_required: bool = False
    kufar_payment_required: bool = False
    kufar_halva_required: bool = False
    only_with_photos: bool = False
    only_with_videos: bool = False
    only_with_exchange_available: bool = False
    sort_type: int | None = None
    category: int | None = None
    sub_category: int | None = None
    region: int | None = None
    areas: list[int] | None = None
    url: str | None = None
    enabled: bool = True
