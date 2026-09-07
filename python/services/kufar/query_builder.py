from typing import Any
from services.managers.models import Query


def _add_parameter(params: dict[str, Any], name: str, value: Any) -> None:
    if value is not None:
        params[name] = value


def _add_boolean_parameter(
    params: dict[str, Any], name: str, value: bool | None
) -> None:
    if value is True:
        params[name] = "1"


def _build_price(query: Query, default_max_price: int) -> str | None:
    if query.price_min is None and query.price_max is None:
        return None

    minimum = 0 if query.price_min is None else query.price_min * 100
    maximum = default_max_price if query.price_max is None else query.price_max * 100

    return f"r:{minimum},{maximum}"


def _build_sort(query: Query) -> str | None:
    if query.sort_type == 1:
        return "prc.d"

    if query.sort_type == 2:
        return "prc.a"

    return None


def build_search_params(query: Query, default_max_price: int) -> dict[str, Any]:
    params: dict[str, Any] = {}

    _add_parameter(params, "query", query.tag)
    _add_parameter(params, "lang", query.language)
    _add_parameter(params, "size", query.limit)
    _add_parameter(params, "prc", _build_price(query, default_max_price))
    _add_parameter(params, "cur", query.currency)
    _add_parameter(params, "cat", query.sub_category)
    _add_parameter(params, "prn", query.category)

    _add_boolean_parameter(params, "ot", query.only_title_search)
    _add_boolean_parameter(params, "dle", query.kufar_delivery_required)
    _add_boolean_parameter(params, "sde", query.kufar_payment_required)
    _add_boolean_parameter(params, "hlv", query.kufar_halva_required)
    _add_boolean_parameter(params, "oph", query.only_with_photos)
    _add_boolean_parameter(params, "ovi", query.only_with_videos)
    _add_boolean_parameter(params, "pse", query.only_with_exchange_available)

    _add_parameter(params, "sort", _build_sort(query))
    _add_parameter(params, "cnd", query.condition)
    _add_parameter(params, "cmp", query.seller_type)
    _add_parameter(params, "rgn", query.region)

    if query.areas:
        params["ar"] = f"v.or:{','.join(map(str, query.areas))}"

    return params
