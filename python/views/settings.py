from html import escape

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from utils.logger import Logger
from keyboards.add_query import main_keyboard, other_keyboard
from services.database import Database
from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from services.filters_manager import FiltersManager

database = Database()
config_manager = ConfigManager()
filters_manager = FiltersManager()
query_manager = QueryManager(database, config_manager)


async def update_menu(bot: Bot | None, state: FSMContext):
    if bot is None:
        Logger.error(None, "(update_menu) bot is None")
        return
    data = await state.get_data()
    query, current_menu = data["query"], data["current_menu"]

    # текст сообщения
    if current_menu == "main":
        text = get_query_text(query)
    else:
        text = "⚙️ Прочие параметры:"

    # клавиатура
    if current_menu == "main":
        keyboard = main_keyboard(query)
    else:
        keyboard = other_keyboard(query)

    await bot.edit_message_text(
        text=text,
        chat_id=data["menu_chat_id"],
        message_id=data["menu_message_id"],
        reply_markup=keyboard,
        parse_mode="HTML",
    )


def get_settings_text(chat_id: int) -> str:
    queries = config_manager.get_queries(str(chat_id))
    max_queries = query_manager.get_max_queries(chat_id)

    text = f"Поисковые запросы: {len(queries)}/{max_queries}\n"
    if len(queries) == 0:
        text += "У вас нет настроенных поисков."
    else:
        text += "Ваши поисковые запросы:\n\n"
        for number, query in enumerate(queries, 1):
            if "tag" in query:
                text += f"{number}. {query['tag']}\n"
            else:
                text += f"{number}. [UNDEFINED]\n"
    return text


def get_query_text(query: dict) -> str:
    text = "⚙️ <b>Настройка запроса</b>\n\n"

    if "tag" in query:
        text += f"🔎 <b>Поиск:</b> {escape(str(query['tag']))}\n"

    if "price" in query:
        price = query["price"]
        if "min" in price and "max" in price:
            text += f"💰 <b>Цена:</b> {price['min']} – {price['max']} {query.get('currency', '')}\n"
        elif "min" in price:
            text += f"💰 <b>Цена:</b> от {price['min']} {query.get('currency', '')}\n"
        elif "max" in price:
            text += f"💰 <b>Цена:</b> до {price['max']} {query.get('currency', '')}\n"

    if "language" in query:
        text += f"🌐 <b>Язык:</b> {query['language']}\n"

    if "condition" in query:
        condition = filters_manager.get_item_condition_by_id(query["condition"])
        if condition is not None:
            text += f"📦 <b>Состояние:</b> {condition['name']}\n"

    if "seller-type" in query:
        seller_type = filters_manager.get_seller_type_by_id(query["seller-type"])
        if seller_type is not None:
            text += f"👤 <b>Продавец:</b> {seller_type['name']}\n"

    if "category" in query:
        category = filters_manager.get_category_by_id(query["category"])
        if category is not None:
            text += f"📂 <b>Категория:</b> {category['name']}\n"
            if "sub-category" in query:
                subcategory = filters_manager.get_subcategory_by_id(
                    query["category"],
                    query["sub-category"],
                )
                if subcategory is not None:
                    text += f"└ <b>Подкатегория:</b> {subcategory['name']}\n"

    if "region" in query:
        region = filters_manager.get_region_by_id(query["region"])
        if region is not None:
            text += f"📍 <b>Регион:</b> {region['name']}\n"

    if "areas" in query:
        area_names = []
        for area_id in query["areas"]:
            area = filters_manager.get_area_by_id(area_id)
            if area is not None:
                area_names.append(area["name"])
        if area_names:
            text += f"└ <b>Районы:</b> {', '.join(area_names)}\n"

    options = [
        ("only-title-search", "🔤 Искать только в заголовке"),
        ("kufar-delivery-required", "🚚 Требуется доставка Kufar"),
        ("kufar-payment-required", "💳 Требуется оплата Kufar"),
        ("kufar-halva-required", "💳 Требуется оплата Халвой"),
        ("only-with-photos", "📷 Только с фото"),
        ("only-with-videos", "🎥 Только с видео"),
        ("only-with-exchange-available", "🔄 Только с возможностью обмена"),
    ]
    enabled_options = [name for field, name in options if query.get(field) is True]
    if enabled_options:
        text += "\n<b>Дополнительно:</b>\n"
        for option in enabled_options:
            text += f"• {option}\n"

    developer_fields = []
    if "limit" in query:
        developer_fields.append(f"limit: {query['limit']}")

    if "start-time" in query:
        developer_fields.append(f"start-time: {query['start-time']}")

    if "chat-id" in query:
        developer_fields.append(f"chat-id: {query['chat-id']}")

    known_fields = {
        "tag",
        "only-title-search",
        "price",
        "language",
        "limit",
        "currency",
        "condition",
        "seller-type",
        "kufar-delivery-required",
        "kufar-payment-required",
        "kufar-halva-required",
        "only-with-photos",
        "only-with-videos",
        "only-with-exchange-available",
        "sort-type",
        "category",
        "sub-category",
        "region",
        "areas",
        "start-time",
        "chat-id",
    }

    unknown_fields = {
        key: value for key, value in query.items() if key not in known_fields
    }
    if unknown_fields:
        developer_fields.append(f"unknown fields: {unknown_fields}")

    if developer_fields:
        text += "\n<b>Для разработчика:</b>\n<tg-spoiler>"
        for field in developer_fields:
            text += f"{field}\n"
        text += "</tg-spoiler>"

    return text
