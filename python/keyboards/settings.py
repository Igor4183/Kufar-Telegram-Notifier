from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить", callback_data="add_query")
    builder.button(text="✏️ Изменить", callback_data="edit_query")
    builder.button(
        text="🔔 Управление уведомлениями", callback_data="notification_settings"
    )
    builder.button(text="🗑 Удалить", callback_data="remove_query")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def back_to_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_settings")
    return builder.as_markup()


def notification_settings_keyboard(queries):
    builder = InlineKeyboardBuilder()

    for query in queries:
        status = "🔔" if query.enabled else "🔕"
        tag = query.tag if query.tag is not None else "[UNDEFINED]"

        builder.button(
            text=f"{status} {tag}",
            callback_data=f"notification_toggle:{query.query_id}",
        )

    builder.button(text="🔙 Назад", callback_data="back_to_settings")
    builder.adjust(1)

    return builder.as_markup()
