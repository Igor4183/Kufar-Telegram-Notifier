from typing import Any

DEFAULT_MAX_PRICE = 1_000_000_000


def _add_parameter(params: dict[str, Any], parameter: str, value: Any) -> None:
    if value is not None:
        params[parameter] = value


def _add_boolean_parameter(
    params: dict[str, Any], parameter: str, value: bool | None
) -> None:
    if value is True:
        # Старый C++ код отправлял std::to_string(bool) -> "1".
        params[parameter] = "1"


def _join_price(price: dict[str, Any] | None) -> str | None:
    if price is None:
        return None

    price_min = price.get("min")
    price_max = price.get("max")

    if price_min is None and price_max is None:
        return None

    if price_min is None:
        min_price = 0
    else:
        min_price = int(price_min) * 100

    if price_max is None:
        max_price = DEFAULT_MAX_PRICE
    else:
        max_price = int(price_max) * 100

    return f"r:{min_price},{max_price}"


def _get_sort_type(sort_type: int | None) -> str | None:
    if sort_type == 1:
        return "prc.d"
    if sort_type == 2:
        return "prc.a"

    return None


def build_search_params(query: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {}

    _add_parameter(params, "query", query.get("tag"))
    _add_parameter(params, "lang", query.get("language"))
    _add_parameter(params, "size", query.get("limit"))
    _add_parameter(params, "prc", _join_price(query.get("price")))
    _add_parameter(params, "cur", query.get("currency"))
    _add_parameter(params, "cat", query.get("sub-category"))
    _add_parameter(params, "prn", query.get("category"))

    _add_boolean_parameter(params, "ot", query.get("only-title-search"))
    _add_boolean_parameter(params, "dle", query.get("kufar-delivery-required"))
    _add_boolean_parameter(params, "sde", query.get("kufar-payment-required"))
    _add_boolean_parameter(params, "hlv", query.get("kufar-halva-required"))
    _add_boolean_parameter(params, "oph", query.get("only-with-photos"))
    _add_boolean_parameter(params, "ovi", query.get("only-with-videos"))
    _add_boolean_parameter(params, "pse", query.get("only-with-exchange-available"))

    _add_parameter(params, "sort", _get_sort_type(query.get("sort-type")))
    _add_parameter(params, "cnd", query.get("condition"))
    _add_parameter(params, "cmp", query.get("seller-type"))
    _add_parameter(params, "rgn", query.get("region"))

    areas = query.get("areas")

    if areas:
        params["ar"] = f"v.or:{','.join(map(str, areas))}"

    return params
