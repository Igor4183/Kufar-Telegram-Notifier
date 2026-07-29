import time

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.config_manager import ConfigManager
from utils.logger import Logger
from keyboards.settings import settings_keyboard
from states.settings import AddQuery
from views.add_query import update_menu

router = Router()
config_manager = ConfigManager()


@router.message(Command("settings"))
async def settings_command(message: Message):
    Logger.info(message.chat.id, "/settings")
    queries = config_manager.get_queries(str(message.chat.id))

    if len(queries) == 0:
        await message.answer("У вас нет настроенных поисков.")
    else:
        text = "Ваши поисковые запросы:\n\n"
        cnt = 0
        for query in queries:
            cnt += 1
            if "tag" in query:
                text += f"{cnt}. {query["tag"]}\n"
            else:
                text += f"{cnt}. [UNDEFINED]\n"
        await message.answer(text, reply_markup=settings_keyboard())


@router.callback_query(F.data == "remove_query")
async def delete_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message is None:
        return
    Logger.info(callback.message.chat.id, "/settings -> remove_query")
    queries = config_manager.get_queries(str(callback.message.chat.id))
    if len(queries) == 0:
        await callback.message.answer("У вас нет настроенных поисков.")
    else:
        text = "Введите номер объявления для удаления:\n\n"
        cnt = 0
        for query in queries:
            cnt += 1
            if "tag" in query:
                text += f"{cnt}. {query["tag"]}\n"
            else:
                text += f"{cnt}. [UNDEFINED]\n"
        await callback.message.answer(text)
        await state.set_state(AddQuery.waiting_for_delete)


@router.message(AddQuery.waiting_for_delete)
async def process_delete(message: Message, state: FSMContext):
    if message.text is None or not message.text.isdigit():
        await message.answer("Введите номер.")
        return

    index = int(message.text)
    config = config_manager.get_queries(str(message.chat.id))
    if index <= 0 or index > len(config):
        await message.answer("Нет такого номера.")
        return

    Logger.info(
        message.chat.id,
        f"Запрос под номером {index} удалён. "
        + str(config_manager.get_query(str(message.chat.id), index)),
    )
    config_manager.remove_query(str(message.chat.id), index)
    await state.clear()
    await message.answer("✅ Запрос удалён.")


@router.callback_query(F.data == "add_query")
async def add_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message is None:
        return
    Logger.info(callback.message.chat.id, "/settings -> add_query")
    await state.set_state(AddQuery.waiting_for_tag)
    await callback.message.answer("Введите поисковый запрос.")


@router.message(AddQuery.waiting_for_tag)
async def process_query(message: Message, state: FSMContext):
    Logger.info(message.chat.id, f"(waiting_for_tag)введён tag: {message.text}")
    query = {"tag": message.text}
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
    # Logger place
    data = await state.get_data()
    field = data["editing_field"]
    query = data["query"]

    if field == "tag":
        query["tag"] = message.text

    await state.update_data(query=query)
    await state.set_state(AddQuery.editing)
    await update_menu(message.bot, state)


@router.callback_query(AddQuery.editing, F.data == "edit_query")
async def edit_query(callback: CallbackQuery, state: FSMContext):
    # Logger place
    if not isinstance(callback.message, Message):
        return

    if callback.message is None:
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
async def save_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["start-time"] = int(time.time())
    query["limit"] = (
        3  # что-то тут надо придумать с лимитом, чтобы у меня комп не лёг и можно было бы его настраивать.
    )
    query["chat-id"] = str(callback.from_user.id)  # data["menu_chat_id"]
    config_manager.add_query(str(callback.from_user.id), query)
    Logger.info(callback.from_user.id, f"Добавлен новый запрос '{query['tag']}'")
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text("✅ Запрос успешно сохранён.")


@router.callback_query(AddQuery.editing, F.data == "other_menu")
async def other_menu(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    await state.update_data(current_menu="other")
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    await state.update_data(current_menu="main")
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_title")
async def toggle_only_title(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-title-search"] = not query.get("only-title-search", False)
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_photos")
async def toggle_only_with_photos(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-with-photos"] = not query.get("only-with-photos", False)
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_videos")
async def toggle_only_with_videos(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["only-with-videos"] = not query.get("only-with-videos", False)
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_condition")
async def toggle_condition(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["condition"] = (query.get("condition", 0) + 1) % 3
    if query["condition"] == 0:
        query.pop("condition")
    await state.update_data(query=query)
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "toggle_seller_type")
async def toggle_seller_type(callback: CallbackQuery, state: FSMContext):
    # Logger place
    await callback.answer()
    data = await state.get_data()
    query = data["query"]
    query["seller-type"] = (query.get("seller-type", 2) + 1) % 3
    if query["seller-type"] == 2:
        query.pop("seller-type")
    await state.update_data(query=query)
    await update_menu(callback.bot, state)
