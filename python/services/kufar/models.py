from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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
class CalculatorPrice:
    currency: str
    price: str
    price_per_meter: str | None


@dataclass
class PaidServices:
    halva: bool
    highlight: bool
    polepos: bool
    ribbons: Any


@dataclass
class ShowParameters:
    show_call: bool
    show_chat: bool
    show_import_link: bool
    show_web_shop_link: bool


@dataclass
class PaginationPage:
    label: str
    num: int
    token: str | None


@dataclass
class Pagination:
    pages: list[PaginationPage] = field(default_factory=list)


@dataclass
class Ad:
    account_id: str
    ad_id: str
    list_id: int
    message_id: str
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
    calculator: list[CalculatorPrice]

    category: str

    company_ad: bool
    account_parameters: list[AccountParameter]
    ad_parameters: list[AdParameter]

    images: list[Image]

    is_mine: bool
    phone_hidden: bool
    feedback_info: Any
    paid_services: PaidServices
    show_parameters: ShowParameters

    raw_data: dict[str, Any]

    @property
    def id(self) -> str:
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
class KufarSearchResponse:
    ads: list[Ad]
    page_type: str
    pagination: Pagination
    total: int
    raw_data: dict[str, Any]
