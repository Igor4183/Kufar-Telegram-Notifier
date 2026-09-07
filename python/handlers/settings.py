import time
from typing import Any

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database import Database
from services.managers import ConfigManager, FiltersManager, QueryManager, UserManager
from services.processing import Scheduler
from utils.logger import Logger
from keyboards.settings import settings_keyboard, back_to_settings_keyboard
from states.settings import AddQuery
from views.settings import update_menu, get_settings_text

router = Router()

database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database)
user_manager = UserManager(database, config_manager)
filters_manager = FiltersManager()


@router.message(Command("settings"))
async def settings_command(message: Message):
    Logger.info(message.chat.id, "/settings")
    text = get_settings_text(message.chat.id)
    await message.answer(text, reply_markup=settings_keyboard())


@router.callback_query(
    StateFilter(
        AddQuery.waiting_for_edit, AddQuery.waiting_for_delete, AddQuery.waiting_for_tag
    ),
    F.data == "back_to_settings",
)
async def back_to_settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if not isinstance(callback.message, Message):
        return

    Logger.info(callback.from_user.id, "/settings -> settings_keyboard -> back")
    text = get_settings_text(callback.message.chat.id)

    await state.clear()
    await callback.message.edit_text(text, reply_markup=settings_keyboard())


@router.message(AddQuery.waiting_for_edit)
async def process_edit(message: Message, state: FSMContext):
    if message.text is None or not message.text.isdigit():
        await message.answer("Введите номер запроса.")
        return

    number = int(message.text)
    queries = query_manager.get_queries(message.chat.id)

    if number <= 0 or number > len(queries):
        await message.answer("❌ Нет такого номера.")
        return

    selected_query = queries[number - 1]
    query = query_manager.get_query_config(selected_query.query_id)

    Logger.info(
        message.chat.id,
        f"/settings -> edit_query -> выбран запрос №{number}: {selected_query.tag}",
    )

    await state.update_data(
        query=query,
        query_id=selected_query.query_id,
        query_number=number,
        current_menu="main",
        edit_mode=True,
    )
    await state.set_state(AddQuery.editing)
    await update_menu(message.bot, state)


@router.callback_query(F.data == "remove_query")
async def delete_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.message is None:
        return

    chat_id = callback.message.chat.id
    Logger.info(chat_id, "/settings -> remove_query")

    queries = query_manager.get_queries(chat_id)

    if len(queries) == 0:
        await callback.message.answer("У вас нет настроенных поисков.")
        return

    text = "Введите номер объявления для удаления:\n\n"

    for number, query in enumerate(queries, 1):
        text += f"{number}. {query.tag}\n"

    await callback.message.answer(text, reply_markup=back_to_settings_keyboard())
    await state.set_state(AddQuery.waiting_for_delete)


@router.message(AddQuery.waiting_for_delete)
async def process_delete(message: Message, state: FSMContext, scheduler: Scheduler):
    if message.text is None or not message.text.isdigit():
        await message.answer("Введите номер.")
        return

    index = int(message.text)
    queries = query_manager.get_queries(message.chat.id)

    if index <= 0 or index > len(queries):
        await message.answer("Нет такого номера.")
        return

    query = queries[index - 1]

    Logger.info(
        message.chat.id, f"Запрос под номером {index} удалён. query_id={query.query_id}"
    )

    query_manager.delete_query(query.query_id)
    scheduler.remove_query(query.query_id)

    await state.clear()
    await message.answer("✅ Запрос удалён.")


@router.callback_query(F.data == "add_query")
async def add_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.message is None:
        return

    Logger.info(callback.message.chat.id, "/settings -> add_query")

    await state.update_data(edit_mode=False)
    await state.set_state(AddQuery.waiting_for_tag)
    await callback.message.answer(
        "Введите поисковый запрос.", reply_markup=back_to_settings_keyboard()
    )


@router.message(AddQuery.waiting_for_tag)
async def process_query(message: Message, state: FSMContext):
    Logger.info(message.chat.id, f"(waiting_for_tag)введён tag: {message.text}")

    query: dict[str, Any] = {"only-title-search": False}
    query["tag"] = message.text

    menu = await message.answer("Создаю меню...")

    await state.update_data(
        query=query,
        current_menu="main",
        menu_chat_id=menu.chat.id,
        menu_message_id=menu.message_id,
    )
    await update_menu(message.bot, state)
    await state.set_state(AddQuery.editing)


@router.message(AddQuery.waiting_for_value)
async def waiting_for_value(message: Message, state: FSMContext):
    Logger.info(
        message.chat.id, f"(waiting_for_value) введено значение: {message.text}"
    )

    data = await state.get_data()
    field = data["editing_field"]
    query: dict[str, Any] = data["query"]

    if field == "tag":
        if message.text is None:
            await message.answer("❌ Значение не может быть пустым.")
            return

        query["tag"] = message.text

    await state.update_data(query=query)
    await state.set_state(AddQuery.editing)
    await update_menu(message.bot, state)


@router.callback_query(AddQuery.editing, F.data == "edit_tag")
async def edit_tag(callback: CallbackQuery, state: FSMContext):
    if not isinstance(callback.message, Message):
        return

    await callback.answer()
    await state.update_data(editing_field="tag")
    await state.set_state(AddQuery.waiting_for_value)
    await callback.message.edit_text("Введите новый заголовок.")


@router.callback_query(AddQuery.editing, F.data == "cancel_query")
async def cancel_query(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/settings -> создание запроса отменено")
    await callback.answer()
    await state.clear()

    if isinstance(callback.message, Message):
        await callback.message.edit_text("❌ Создание запроса отменено.")


@router.callback_query(AddQuery.editing, F.data == "save_query")
async def save_query(callback: CallbackQuery, state: FSMContext, scheduler: Scheduler):
    await callback.answer()

    if not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    query: dict[str, Any] = data["query"]
    chat_id = callback.from_user.id
    edit_mode = data.get("edit_mode", False)

    if edit_mode:
        query_id = data["query_id"]
        updated_query = query_manager.update_query(query_id, query)
        scheduler.add_query(updated_query)
    else:
        if not user_manager.can_add_query(chat_id):
            await callback.message.answer("❌ Вы достигли лимита поисковых запросов.")
            return

        tag = query.get("tag")

        if not isinstance(tag, str) or not tag:
            await callback.message.answer("❌ Поисковый запрос не может быть пустым.")
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


@router.callback_query(AddQuery.editing, F.data == "other_menu")
async def other_menu(callback: CallbackQuery, state: FSMContext):
    Logger.info(
        callback.from_user.id, "/settings -> add_query -> открыто меню 'прочее'"
    )
    await callback.answer()
    await state.update_data(current_menu="other")
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/settings -> add_query -> назад")
    await callback.answer()
    await state.update_data(current_menu="main")
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_title")
async def toggle_only_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-title-search"] = not query.get("only-title-search", False)
    Logger.info(
        callback.from_user.id,
        f"/settings -> only-title-search -> {query['only-title-search']}",
    )
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_photos")
async def toggle_only_with_photos(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-with-photos"] = not query.get("only-with-photos", False)
    Logger.info(
        callback.from_user.id,
        f"/settings -> only-with-photos -> {query['only-with-photos']}",
    )
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_videos")
async def toggle_only_with_videos(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-with-videos"] = not query.get("only-with-videos", False)
    Logger.info(
        callback.from_user.id,
        f"/settings -> only-with-videos -> {query['only-with-videos']}",
    )
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_condition")
async def toggle_condition(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["condition"] = (query.get("condition", 0) + 1) % 3

    if query["condition"] == 0:
        query.pop("condition")

    Logger.info(callback.from_user.id, f"(toggle_condition): {query.get('condition')}")
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_seller_type")
async def toggle_seller_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["seller-type"] = (query.get("seller-type", 2) + 1) % 3

    if query["seller-type"] == 2:
        query.pop("seller-type")

    Logger.info(
        callback.from_user.id, f"/settings -> seller-type -> {query.get('seller-type')}"
    )
    await state.update_data(query=query)
    await update_menu(callback.bot, state)
