from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_keyboard(query: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Изменить заголовок", callback_data="edit_tag")
    builder.button(text="Прочее", callback_data="other_menu")
    # builder.button(text="📍 Регион", callback_data="field_region")
    # builder.button(text="📦 Лимит", callback_data="field_limit")
    # builder.button(text="Только заголовок", callback_data="field_only_title")
    builder.button(text="💾 Сохранить", callback_data="save_query")
    builder.button(text="❌ Отмена", callback_data="cancel_query")

    builder.adjust(1, 1, 2)
    return builder.as_markup()


def other_keyboard(query: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    enabled = query.get("only-title-search", False)
    text = "✅ Поиск только в заголовках" if enabled else "❌ Поиск только в заголовках"
    builder.button(text=text, callback_data="toggle_only_title")

    enabled = query.get("only-with-photos", False)
    text = "✅ только с фото" if enabled else "❌ только с фото"
    builder.button(text=text, callback_data="toggle_only_with_photos")

    enabled = query.get("only-with-videos", False)
    text = "✅ только с видео" if enabled else "❌ только с видео"
    builder.button(text=text, callback_data="toggle_only_with_videos")

    enabled = query.get("condition", 0)  # 0 - disable, 1 - used, 2 - new
    if enabled == 0:
        text = "Cостояние: не указано"
    elif enabled == 1:
        text = "Состояние: б/у"
    else:
        text = "Состояние: новое"
    builder.button(text=text, callback_data="toggle_condition")

    enabled = query.get(
        "seller-type", 2
    )  # 0 - individualPerson, 1 - company, 2 - disable
    if enabled == 0:
        text = "Тип продовца: частное лицо"
    elif enabled == 1:
        text = "Тип продовца: компания"
    else:
        text = "Тип продовца: не указано"
    builder.button(text=text, callback_data="toggle_seller_type")

    builder.button(text="🔙 Назад", callback_data="back")

    builder.adjust(1, 1, 1, 1, 1, 1)
    return builder.as_markup()
