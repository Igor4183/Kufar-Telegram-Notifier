from dataclasses import dataclass


@dataclass
class Query:
    query_id: int
    chat_id: int
    tag: str
    limit: int
    start_time: int
    delay: int
    only_title_search: bool | None = None
    price_min: int | None = None
    price_max: int | None = None
    language: str | None = None
    currency: str | None = None
    condition: int | None = None
    seller_type: int | None = None
    kufar_delivery_required: bool | None = None
    kufar_payment_required: bool | None = None
    kufar_halva_required: bool | None = None
    only_with_photos: bool | None = None
    only_with_videos: bool | None = None
    only_with_exchange_available: bool | None = None
    sort_type: int | None = None
    category: int | None = None
    sub_category: int | None = None
    region: int | None = None
    areas: list[int] | None = None
    enabled: bool = True
