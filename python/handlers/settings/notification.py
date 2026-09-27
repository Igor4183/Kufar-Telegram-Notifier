from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from keyboards.settings import notification_settings_keyboard
from services.database import Database
from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from utils.logger import Logger

router = Router()

database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database, config_manager)


@router.callback_query(F.data.startswith("disable_query:"))
async def disable_query(callback: CallbackQuery):
    if callback.data is None:
        return

    try:
        query_id = int(callback.data.split(":", 1)[1])
    except ValueError:
        await callback.answer("❌ Некорректный запрос.")
        return

    success = query_manager.set_query_enabled(callback.from_user.id, query_id, False)

    if not success:
        await callback.answer("❌ Не удалось отключить уведомления.")
        return
    Logger.info(callback.from_user.id, f"Отключены уведомления для query_id={query_id}")
    await callback.answer("🔕 Уведомления отключены.")


@router.callback_query(F.data == "notification_settings")
async def notification_settings(callback: CallbackQuery):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    queries = query_manager.get_queries(callback.from_user.id)
    text = "🔔 <b>Управление уведомлениями</b>\n\n"
    if not queries:
        text += "У вас нет поисковых запросов."
    else:
        text += "Выберите запрос, чтобы включить или выключить уведомления.\n\nНастройка уведомлений может работать не сразу."

    await callback.message.edit_text(
        text,
        reply_markup=notification_settings_keyboard(queries),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("notification_toggle:"))
async def notification_toggle(callback: CallbackQuery):
    if callback.data is None:
        return

    try:
        query_id = int(callback.data.split(":", 1)[1])
    except ValueError:
        await callback.answer("❌ Некорректный запрос.")
        return

    queries = query_manager.get_queries(callback.from_user.id)
    query = next((query for query in queries if query.query_id == query_id), None)

    if query is None:
        await callback.answer("❌ Запрос не найден.")
        return
    enabled = not query.enabled

    if not query_manager.set_query_enabled(callback.from_user.id, query_id, enabled):
        await callback.answer("❌ Не удалось изменить состояние.")
        return

    await callback.answer(
        "🔔 Уведомления включены." if enabled else "🔕 Уведомления отключены."
    )
    queries = query_manager.get_queries(callback.from_user.id)
    if not isinstance(callback.message, Message):
        return

    await callback.message.edit_reply_markup(
        reply_markup=notification_settings_keyboard(queries)
    )
