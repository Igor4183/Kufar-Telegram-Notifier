from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Пользователи", callback_data="admin_users")
    builder.button(text="🔎 Запросы", callback_data="admin_queries")
    builder.button(text="⚙️ Лимиты", callback_data="admin_limits")
    builder.button(text="📋 Конфигурация", callback_data="admin_configuration")
    builder.button(text="📜 Логи", callback_data="admin_logs")
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()


def admin_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 назад", callback_data="admin_back")
    return builder.as_markup()


def admin_limits_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⚙️ изменить/добавить лимит", callback_data="admin_change_max_queries"
    )
    builder.button(text="🔙 назад", callback_data="admin_back")
    builder.adjust(1, 1)
    return builder.as_markup()


def admin_logs_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🐍 Python", callback_data="admin_logs_python")
    builder.button(text="⚙️ C++", callback_data="admin_logs_cpp")
    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(2, 1)
    return builder.as_markup()


def admin_log_format_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Отправить последний лог", callback_data="admin_log_latest")
    builder.button(
        text="📚 Отправить последние 5 логов", callback_data="admin_log_last_5"
    )
    builder.button(text="📅 Отправить логи за сегодня", callback_data="admin_log_today")
    builder.button(text="📦 Отправить все логи", callback_data="admin_log_all")
    builder.button(text="🔙 Назад", callback_data="admin_logs")
    builder.adjust(1)
    return builder.as_markup()
