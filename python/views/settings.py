from html import escape

from aiogram import Bot
from aiogram.fsm.context import FSMContext

from utils.logger import Logger
from keyboards.add_query import main_keyboard, other_keyboard
from services.database import Database
from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from services.filters_manager import FiltersManager
from services.models import Query

database = Database()
config_manager = ConfigManager()
filters_manager = FiltersManager()
query_manager = QueryManager(database, config_manager)


async def update_menu(bot: Bot | None, state: FSMContext):
    if bot is None:
        Logger.error(None, "(update_menu) bot is None")
        return

    data = await state.get_data()
    query: Query = data["query"]
    current_menu = data["current_menu"]

    if current_menu == "main":
        text = get_query_text(query)
    else:
        text = "⚙️ Прочие параметры:"

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
    queries = query_manager.get_queries(chat_id)
    max_queries = query_manager.get_max_queries(chat_id)

    text = f"Поисковые запросы: {len(queries)}/{max_queries}\n"

    if len(queries) == 0:
        text += "У вас нет настроенных поисков."
    else:
        text += "Ваши поисковые запросы:\n\n"

        for number, query in enumerate(queries, 1):
            if query.tag is not None:
                text += f"{number}. {query.tag}\n"
            else:
                text += f"{number}. [UNDEFINED]\n"

    return text


def get_query_text(query: Query) -> str:
    text = "⚙️ <b>Настройка запроса</b>\n\n"

    if query.tag is not None:
        text += f"🔎 <b>Поиск:</b> {escape(query.tag)}\n"

    if query.price_min is not None and query.price_max is not None:
        text += f"💰 <b>Цена:</b> {query.price_min} – {query.price_max} {query.currency or ''}\n"
    elif query.price_min is not None:
        text += f"💰 <b>Цена:</b> от {query.price_min} {query.currency or ''}\n"
    elif query.price_max is not None:
        text += f"💰 <b>Цена:</b> до {query.price_max} {query.currency or ''}\n"

    if query.language is not None:
        text += f"🌐 <b>Язык:</b> {escape(str(query.language))}\n"

    if query.condition is not None:
        condition = filters_manager.get_item_condition_by_id(query.condition)
        if condition is not None:
            text += f"📦 <b>Состояние:</b> {condition['name']}\n"

    if query.seller_type is not None:
        seller_type = filters_manager.get_seller_type_by_id(query.seller_type)
        if seller_type is not None:
            text += f"👤 <b>Продавец:</b> {seller_type['name']}\n"

    if query.category is not None:
        category = filters_manager.get_category_by_id(query.category)
        if category is not None:
            text += f"📂 <b>Категория:</b> {category['name']}\n"

            if query.sub_category is not None:
                subcategory = filters_manager.get_subcategory_by_id(
                    query.category,
                    query.sub_category,
                )
                if subcategory is not None:
                    text += f"└ <b>Подкатегория:</b> {subcategory['name']}\n"

    if query.region is not None:
        region = filters_manager.get_region_by_id(query.region)
        if region is not None:
            text += f"📍 <b>Регион:</b> {region['name']}\n"

    if query.areas:
        area_names = []

        for area_id in query.areas:
            area = filters_manager.get_area_by_id(area_id)
            if area is not None:
                area_names.append(area["name"])

        if area_names:
            text += f"└ <b>Районы:</b> {', '.join(area_names)}\n"

    options = [
        (query.only_title_search, "🔤 Искать только в заголовке"),
        (query.kufar_delivery_required, "🚚 Требуется доставка Kufar"),
        (query.kufar_payment_required, "💳 Требуется оплата Kufar"),
        (query.kufar_halva_required, "💳 Требуется оплата Халвой"),
        (query.only_with_photos, "📷 Только с фото"),
        (query.only_with_videos, "🎥 Только с видео"),
        (
            query.only_with_exchange_available,
            "🔄 Только с возможностью обмена",
        ),
    ]

    enabled_options = [name for enabled, name in options if enabled is True]

    if enabled_options:
        text += "\n<b>Дополнительно:</b>\n"

        for option in enabled_options:
            text += f"• {option}\n"

    developer_fields = [
        f"query_id: {query.query_id}",
        f"limit: {query.limit}",
        f"start-time: {query.start_time}",
        f"delay: {query.delay}",
        f"chat-id: {query.chat_id}",
        f"enabled: {query.enabled}",
    ]

    if developer_fields:
        text += "\n<b>Для разработчика:</b>\n<tg-spoiler>"

        for field in developer_fields:
            text += f"{field}\n"

        text += "</tg-spoiler>"

    return text
