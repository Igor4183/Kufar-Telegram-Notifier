from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить", callback_data="add_query")
    builder.button(text="🗑 Удалить", callback_data="remove_query")
    builder.adjust(2)
    return builder.as_markup()
