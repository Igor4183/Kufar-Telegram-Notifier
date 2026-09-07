from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.admin import (
    admin_keyboard,
    admin_limits_keyboard,
    admin_logs_keyboard,
    admin_log_format_keyboard,
    admin_back_keyboard,
)
from services.database import Database
from services.managers import ConfigManager, QueryManager, UserManager
from services.log_manager import LogManager, LogType
from states.admin import Admin

database = Database()
config_manager = ConfigManager()
user_manager = UserManager(database, config_manager)
query_manager = QueryManager(database)
log_manager = LogManager()


async def update_admin_menu(message: Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == Admin.main.state:
        await message.edit_text(
            "🛠 Панель администратора", reply_markup=admin_keyboard()
        )
        return

    if current_state == Admin.users.state:
        users = user_manager.get_all_users()
        text = f"👥 Количество пользователей: {len(users)}\n\n"

        if not users:
            text += "Пользователей пока нет. :("
        else:
            for number, user in enumerate(users, 1):
                chat_id, username = user
                if username:
                    text += f"{number}. @{username} <code>{chat_id}</code>\n"
                else:
                    text += f"{number}. <code>{chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_back_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.queries.state:
        queries = query_manager.get_queries()
        text = f"🔎 Количество запросов: {len(queries)}\n\n"

        if not queries:
            text += "Запросов пока нет. :("
        else:
            for number, query in enumerate(queries, 1):
                text += f"{number}. {query.tag} <code>{query.chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_back_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.limits.state:
        max_limits = user_manager.get_all_query_limits()
        text = f"🔎 Количество установленных лимитов: {len(max_limits)}\n\n"

        if not max_limits:
            text += "Лимиты пока не установлены."
        else:
            for number, max_limit in enumerate(max_limits, 1):
                chat_id, max_queries = max_limit
                text += f"{number}. {max_queries} <code>{chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_limits_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.logs.state:
        await message.edit_text(
            "📜 Логи\n\nВыберите тип логов:", reply_markup=admin_logs_keyboard()
        )
        return

    if current_state == Admin.log_format.state:
        log_type_value = data.get("log_type")

        if log_type_value is None:
            await state.update_data(menu="logs")
            await message.edit_text(
                "📜 Логи\n\nВыберите тип логов:", reply_markup=admin_logs_keyboard()
            )
            return

        log_type = LogType(log_type_value)
        logs = log_manager.get_logs(log_type)

        if log_type == LogType.PYTHON:
            title = "🐍 Python"
        else:
            title = "⚙️ C++"

        text = f"📜 {title} логи\n\n"

        if not logs:
            text += "Логов пока нет."
        else:
            text += "Последние логи:\n\n"
            for number, log in enumerate(logs[:6], 1):
                text += f"{number}. <code>{log.name}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_log_format_keyboard(), parse_mode="HTML"
        )
