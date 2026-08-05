from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from keyboards.admin import (
    admin_keyboard,
    admin_limits_keyboard,
    admin_logs_keyboard,
    admin_log_format_keyboard,
    admin_back_keyboard,
)
from services.query_manager import QueryManager
from services.config_manager import ConfigManager
from services.user_manager import UserManager
from services.log_manager import LogManager, LogType
from states.admin import Admin


async def update_admin_menu(
    message: Message,
    state: FSMContext,
    user_manager: UserManager,
    query_manager: QueryManager,
    config_manager: ConfigManager,
    log_manager: LogManager,
):
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
                    text += f"{number}. @{username} " f"<code>{chat_id}</code>\n"
                else:
                    text += f"{number}. " f"<code>{chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_back_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.queries.state:
        queries = config_manager.get_queries(None)
        text = f"🔎 Количество запросов: {len(queries)}\n\n"

        if not queries:
            text += "Запросов пока нет. :("
        else:
            for number, query in enumerate(queries, 1):
                tag = query.get("tag", "[UNDEFINED]")
                chat_id = query.get("chat-id", "[UNDEFINED]")
                text += f"{number}. {tag} " f"<code>{chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_back_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.limits.state:
        max_limits = query_manager.get_all_query_limits()
        text = f"🔎 Количество установленных лимитов: {len(max_limits)}\n\n"

        if not max_limits:
            text += "Лимиты пока не установлены."
        else:
            for number, max_limit in enumerate(max_limits, 1):
                chat_id, max_queries = max_limit
                text += f"{number}. {max_queries} " f"<code>{chat_id}</code>\n"

        await message.edit_text(
            text, reply_markup=admin_limits_keyboard(), parse_mode="HTML"
        )
        return

    if current_state == Admin.logs.state:
        await message.edit_text(
            "📜 Логи\n\n" "Выберите тип логов:", reply_markup=admin_logs_keyboard()
        )
        return

    if current_state == Admin.log_format.state:
        log_type_value = data.get("log_type")

        if log_type_value is None:
            await state.update_data(menu="logs")
            await message.edit_text(
                "📜 Логи\n\n" "Выберите тип логов:",
                reply_markup=admin_logs_keyboard(),
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
