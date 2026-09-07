import time

from typing import Any

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database import Database
from services.managers import ConfigManager, QueryManager, UserManager, FiltersManager
from services.processing import Scheduler
from utils.logger import Logger
from keyboards.settings import back_to_settings_keyboard
from states.settings import AddQuery
from views.settings import update_menu

router = Router()

database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database)
user_manager = UserManager(database, config_manager)
filters_manager = FiltersManager()


@router.callback_query(F.data == "add_query")
async def add_query(callback: CallbackQuery, state: FSMContext):
    if not isinstance(callback.message, Message):
        return

    chat_id = callback.message.chat.id
    Logger.info(chat_id, "/settings -> add_query")

    try:
        if not user_manager.can_add_query(chat_id):
            max_queries = user_manager.get_max_queries(chat_id)
            await callback.answer(
                f"❌ Достигнут лимит запросов: {max_queries}", show_alert=True
            )
            return

        await callback.answer()
        await state.update_data(edit_mode=False)
        await state.set_state(AddQuery.waiting_for_tag)
        await callback.message.answer(
            "Введите поисковый запрос.", reply_markup=back_to_settings_keyboard()
        )
    except Exception as error:
        Logger.error(callback.from_user.id, f"(add_query): {error}")
        await callback.answer("❌ Не удалось начать создание запроса.", show_alert=True)


@router.message(AddQuery.waiting_for_tag)
async def process_query(message: Message, state: FSMContext):
    Logger.info(message.chat.id, f"(waiting_for_tag) введён tag: {message.text}")

    query: dict[str, Any] = {"only-title-search": False}
    query["tag"] = message.text

    menu = await message.answer("Создаю меню...")

    await state.update_data(
        query=query,
        current_menu="main",
        menu_chat_id=menu.chat.id,
        menu_message_id=menu.message_id,
    )
    await state.set_state(AddQuery.editing)
    await update_menu(message.bot, state)


@router.message(AddQuery.waiting_for_value)
async def waiting_for_value(message: Message, state: FSMContext):
    Logger.info(
        message.chat.id, f"(waiting_for_value) введено значение: {message.text}"
    )

    try:
        data = await state.get_data()
        field = data["editing_field"]
        query: dict[str, Any] = data["query"]

        if field == "tag":
            if message.text is None:
                await message.answer("❌ Поисковый запрос не может быть пустым.")
                return

            query["tag"] = message.text

        await state.update_data(query=query)
        await state.set_state(AddQuery.editing)
        await update_menu(message.bot, state)
    except Exception as error:
        Logger.error(message.chat.id, f"(waiting_for_value): {error}")
        await message.answer("❌ Не удалось изменить значение. Попробуйте ещё раз.")


@router.callback_query(AddQuery.editing, F.data == "edit_tag")
async def edit_tag(callback: CallbackQuery, state: FSMContext):
    if not isinstance(callback.message, Message):
        return

    await callback.answer()

    try:
        await state.update_data(editing_field="tag")
        await state.set_state(AddQuery.waiting_for_value)
        await callback.message.edit_text("Введите новый заголовок.")
    except Exception as error:
        Logger.error(callback.from_user.id, f"(edit_tag): {error}")


@router.callback_query(AddQuery.editing, F.data == "cancel_query")
async def cancel_query(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/settings -> создание запроса отменено")
    await callback.answer()

    try:
        await state.clear()

        if isinstance(callback.message, Message):
            await callback.message.edit_text("❌ Создание запроса отменено.")
    except Exception as error:
        Logger.error(callback.from_user.id, f"(cancel_query): {error}")


@router.callback_query(AddQuery.editing, F.data == "save_query")
async def save_query(callback: CallbackQuery, state: FSMContext, scheduler: Scheduler):
    await callback.answer()

    if not isinstance(callback.message, Message):
        return

    try:
        data = await state.get_data()
        query: dict[str, Any] = data["query"]
        chat_id = callback.from_user.id
        edit_mode = data.get("edit_mode", False)

        if edit_mode:
            query_id = data["query_id"]
            updated_query = query_manager.update_query(query_id, query)
            scheduler.add_query(updated_query)

            Logger.info(
                chat_id, f"Изменён запрос query_id={query_id}: '{updated_query.tag}'"
            )
        else:
            if not user_manager.can_add_query(chat_id):
                max_queries = user_manager.get_max_queries(chat_id)
                await callback.message.edit_text(
                    f"❌ Достигнут лимит запросов: {max_queries}"
                )
                return

            tag = query.get("tag")

            if not isinstance(tag, str) or not tag.strip():
                await callback.message.edit_text(
                    "❌ Поисковый запрос не может быть пустым."
                )
                return

            created_query = query_manager.create_query(
                chat_id, tag, query, 5, int(time.time()), 60
            )
            scheduler.add_query(created_query)

            Logger.info(
                chat_id,
                f"Добавлен новый запрос '{created_query.tag}', query_id={created_query.query_id}",
            )

        await state.clear()
        await callback.message.edit_text("✅ Запрос успешно сохранён.")

    except Exception as error:
        Logger.error(callback.from_user.id, f"(save_query): {error}")
        await callback.message.edit_text(
            "❌ Не удалось сохранить запрос. Попробуйте ещё раз."
        )
