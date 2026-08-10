from aiogram import Router, F
from aiogram.fsm.state import State
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from pathlib import Path
from services.database import Database
from services.config_manager import ConfigManager
from services.user_manager import UserManager
from services.query_manager import QueryManager
from services.log_manager import LogManager, LogType
from utils.logger import Logger
from keyboards.admin import admin_keyboard
from states.admin import Admin
from views.admin import update_admin_menu

router = Router()

database = Database()
config_manager = ConfigManager()
user_manager = UserManager(database)
query_manager = QueryManager(database, config_manager)
log_manager = LogManager()


async def change_admin_menu(
    callback: CallbackQuery, state: FSMContext, admin_state: State
):
    if not isinstance(callback.message, Message):
        return

    await state.set_state(admin_state)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    if message.chat.id != config_manager.get_admin_chat_id():
        Logger.warning(message.chat.id, "Попытка доступа к админ-панели")
        return
    Logger.info(message.chat.id, "/admin")

    await state.set_state(Admin.main)
    await message.answer("🛠 Панель администратора", reply_markup=admin_keyboard())


@router.callback_query(Admin.main, F.data == "admin_users")
async def admin_users(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_users")

    await callback.answer()
    await change_admin_menu(
        callback,
        state,
        Admin.users,
    )


@router.callback_query(Admin.main, F.data == "admin_queries")
async def admin_queries(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_queries")

    await callback.answer()
    await change_admin_menu(
        callback,
        state,
        Admin.queries,
    )


@router.callback_query(Admin.main, F.data == "admin_limits")
async def admin_limits(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_limits")

    await callback.answer()
    await change_admin_menu(
        callback,
        state,
        Admin.limits,
    )


@router.callback_query(Admin.limits, F.data == "admin_change_max_queries")
async def admin_change_max_queries(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_change_max_queries")

    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    await state.set_state(Admin.waiting_for_limits)
    await callback.message.edit_text(
        "Введите лимиты в формате:\n\n"
        "<code>chat_id max_queries</code>\n\n"
        "Например:\n"
        "<code>111111111 3</code>\n"
        "<code>123456789 5</code>\n\n"
        "Можно указать несколько пользователей.",
        parse_mode="HTML",
    )


@router.message(Admin.waiting_for_limits)
async def process_query_limits(message: Message, state: FSMContext):
    if message.text is None:
        await message.answer("❌ Нужно отправить текстовое сообщение.")
        return

    lines = message.text.strip().splitlines()
    limits = []
    for line_number, line in enumerate(lines, 1):
        parts = line.split()

        if len(parts) != 2:
            await message.answer(
                f"❌ Ошибка в строке {line_number}:\n"
                f"<code>{line}</code>\n\n"
                "Формат: <code>chat_id max_queries</code>",
                parse_mode="HTML",
            )
            return

        chat_id, max_queries = parts
        try:
            chat_id, max_queries = int(chat_id), int(max_queries)
        except ValueError:
            await message.answer(
                f"❌ В строке {line_number} лимит и id чата должены быть числом."
            )
            return

        if max_queries < 0 or chat_id < 0:
            await message.answer(
                f"❌ В строке {line_number} лимит и id чата не может быть отрицательным."
            )
            return

        limits.append((chat_id, max_queries))
    for chat_id, max_queries in limits:
        try:
            query_manager.set_max_queries(chat_id, max_queries)
        except Exception as exc:
            Logger.error(
                message.chat.id,
                f"Ошибка при изменении лимита: "
                f"chat_id={chat_id}, max_queries={max_queries}: {exc}",
            )
        Logger.info(
            message.chat.id,
            f"/admin -> изменён лимит запросов: " f"{chat_id} = {max_queries}",
        )

    await state.set_state(Admin.main)
    await message.answer(
        f"✅ Лимиты успешно обновлены: {len(limits)}",
        reply_markup=admin_keyboard(),
    )


@router.callback_query(Admin.main, F.data == "admin_configuration")
async def admin_configuration(callback: CallbackQuery):
    Logger.info(callback.from_user.id, "/admin -> admin_configuration")
    await callback.answer()

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "kufar-configuration.json"
    )

    try:
        if not config_path.exists():
            Logger.error(
                callback.from_user.id, f"Не найден файл конфигурации: {config_path}"
            )
            await callback.message.answer("❌ Файл конфигурации не найден.")  # type: ignore
            return
        document = FSInputFile(config_path)
        await callback.message.answer_document(  # type: ignore
            document=document,
            caption="📋 Текущая конфигурация",
        )
        Logger.info(callback.from_user.id, "Конфигурация отправлена администратору")
    except Exception as exc:
        Logger.error(
            callback.from_user.id,
            f"Ошибка при отправке конфигурации: " f"[{type(exc).__name__}] {exc}",
        )
        await callback.message.answer("❌ Не удалось отправить конфигурацию.")  # type: ignore


@router.callback_query(Admin.main, F.data == "admin_logs")
async def admin_logs(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_logs")
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    await state.set_state(Admin.logs)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )


@router.callback_query(Admin.logs, F.data == "admin_logs_python")
async def admin_logs_python(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_logs -> python")
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    await state.set_state(Admin.log_format)
    await state.update_data(log_type=LogType.PYTHON.value)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )


@router.callback_query(Admin.logs, F.data == "admin_logs_cpp")
async def admin_logs_cpp(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> admin_logs -> cpp")
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    await state.set_state(Admin.log_format)
    await state.update_data(log_type=LogType.CPP.value)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )


@router.callback_query(Admin.log_format, F.data == "admin_log_latest")
async def admin_log_latest(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    log_type_value = data.get("log_type")
    if log_type_value is None:
        Logger.error(callback.from_user.id, "Не выбран тип логов")
        await callback.message.answer("❌ Тип логов не выбран.")
        return

    log_type = LogType(log_type_value)
    Logger.info(callback.from_user.id, f"/admin -> последний {log_type.value} лог")

    try:
        log = log_manager.get_latest_log(log_type)
        if log is None:
            await callback.message.answer("❌ Логов пока нет.")
            return
        await callback.message.answer_document(
            FSInputFile(log), caption=f"📜 {log.name}"
        )
        Logger.info(
            callback.from_user.id,
            f"Отправлен последний {log_type.value} лог: {log.name}",
        )
    except Exception as exc:
        Logger.error(
            callback.from_user.id,
            "Ошибка отправки последнего лога " f"[{type(exc).__name__}]: {exc}",
        )
        await callback.message.answer("❌ Не удалось отправить лог.")


@router.callback_query(Admin.log_format, F.data == "admin_log_last_5")
async def admin_log_last_5(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    data = await state.get_data()
    log_type_value = data.get("log_type")

    if log_type_value is None:
        await callback.message.answer("❌ Тип логов не выбран.")
        return

    log_type = LogType(log_type_value)
    Logger.info(callback.from_user.id, f"/admin -> последние 5 {log_type.value} логов")

    try:
        logs = log_manager.get_last_logs(log_type, 5)
        if not logs:
            await callback.message.answer("❌ Логов пока нет.")
            return
        archive_path = log_manager.create_archive(log_type, logs)
        await callback.message.answer_document(
            FSInputFile(archive_path), caption=f"📦 Последние {len(logs)} логов"
        )
    except Exception as exc:
        Logger.error(
            callback.from_user.id,
            "Ошибка отправки последних 5 логов " f"[{type(exc).__name__}]: {exc}",
        )
        await callback.message.answer("❌ Не удалось отправить логи.")


@router.callback_query(Admin.log_format, F.data == "admin_log_today")
async def admin_log_today(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    log_type_value = data.get("log_type")
    if log_type_value is None:
        await callback.message.answer("❌ Тип логов не выбран.")
        return

    log_type = LogType(log_type_value)
    Logger.info(callback.from_user.id, f"/admin -> логи за сегодня ({log_type.value})")

    try:
        logs = log_manager.get_today_logs(log_type)
        if not logs:
            await callback.message.answer("❌ За сегодня логов нет.")
            return
        archive_path = log_manager.create_archive(log_type, logs)
        await callback.message.answer_document(
            FSInputFile(archive_path), caption=f"📦 Последние {len(logs)} логов"
        )
        Logger.info(callback.from_user.id, f"Отправлено логов за сегодня: {len(logs)}")
    except Exception as exc:
        Logger.error(
            callback.from_user.id,
            "Ошибка отправки логов за сегодня " f"[{type(exc).__name__}]: {exc}",
        )
        await callback.message.answer("❌ Не удалось отправить логи.")


@router.callback_query(Admin.log_format, F.data == "admin_log_all")
async def admin_log_all(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    log_type_value = data.get("log_type")
    if log_type_value is None:
        await callback.message.answer("❌ Тип логов не выбран.")
        return

    log_type = LogType(log_type_value)
    Logger.info(callback.from_user.id, f"/admin -> все {log_type.value} логи")
    archive_path = None
    try:
        logs = log_manager.get_logs(log_type)
        if not logs:
            await callback.message.answer("❌ Логов пока нет.")
            return
        archive_path = log_manager.create_archive(log_type, logs)
        await callback.message.answer_document(
            FSInputFile(archive_path),
            caption=(f"📦 Все {log_type.value} логи\n" f"Файлов: {len(logs)}"),
        )
        Logger.info(
            callback.from_user.id,
            f"Отправлен архив {archive_path}, " f"файлов: {len(logs)}",
        )
    except Exception as exc:
        Logger.error(
            callback.from_user.id,
            "Ошибка отправки всех логов " f"[{type(exc).__name__}]: {exc}",
        )
        await callback.message.answer("❌ Не удалось подготовить архив логов.")
    finally:
        if archive_path is not None:
            try:
                archive_path.unlink(missing_ok=True)
            except Exception as exc:
                Logger.warning(
                    callback.from_user.id, f"Не удалось удалить временный архив: {exc}"
                )


@router.callback_query(
    StateFilter(Admin.users, Admin.queries, Admin.limits, Admin.logs),
    F.data == "admin_back",
)
async def admin_back(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> back")
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    await state.set_state(Admin.main)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )


@router.callback_query(Admin.log_format, F.data == "admin_logs")
async def admin_log_format_back(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/admin -> log_format -> back")
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    await state.set_state(Admin.logs)
    await state.update_data(log_type=None)
    await update_admin_menu(
        callback.message,
        state,
        user_manager,
        query_manager,
        config_manager,
        log_manager,
    )
