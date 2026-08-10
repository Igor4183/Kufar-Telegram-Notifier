import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from services.database import Database
from utils.logger import Logger
from keyboards.settings import back_to_settings_keyboard
from states.settings import AddQuery
from views.settings import update_menu

router = Router()
database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database, config_manager)


@router.callback_query(F.data == "add_query")
async def add_query(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        return

    chat_id = callback.message.chat.id
    Logger.info(chat_id, "/settings -> add_query")

    try:
        if not query_manager.can_add_query(chat_id):
            max_queries = query_manager.get_max_queries(chat_id)
            await callback.answer(
                f"❌ Достигнут лимит запросов: {max_queries}",
                show_alert=True,
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
        await callback.answer(
            "❌ Не удалось начать создание запроса.",
            show_alert=True,
        )


@router.message(AddQuery.waiting_for_tag)
async def process_query(message: Message, state: FSMContext):
    Logger.info(message.chat.id, f"(waiting_for_tag) введён tag: {message.text}")

    try:
        query = {"tag": message.text}
        menu = await message.answer("Создаю меню...")
        await state.update_data(
            query=query,
            current_menu="main",
            menu_chat_id=menu.chat.id,
            menu_message_id=menu.message_id,
        )
        await state.set_state(AddQuery.editing)
        await update_menu(message.bot, state)
    except Exception as error:
        Logger.error(message.chat.id, f"(process_query): {error}")
        await state.clear()
        await message.answer("❌ Не удалось создать меню запроса. Попробуйте ещё раз.")


@router.message(AddQuery.waiting_for_value)
async def waiting_for_value(message: Message, state: FSMContext):
    Logger.info(
        message.chat.id, f"(waiting_for_value) введено значение: {message.text}"
    )

    try:
        data = await state.get_data()
        field = data["editing_field"]
        query = data["query"]
        if field == "tag":
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
async def save_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query = data["query"]
        chat_id = callback.from_user.id
        edit_mode = data.get("edit_mode", False)

        if edit_mode:
            query_number = data["query_number"]
            config_manager.update_query(str(chat_id), query_number, query)
            Logger.info(chat_id, f"Изменён запрос №{query_number}: '{query['tag']}'")

        else:
            query["start-time"] = int(time.time())
            query["limit"] = (
                5  # что-то тут надо придумать с лимитом, чтобы у меня комп не лёг и можно было бы его настраивать.
            )
            query["chat-id"] = str(callback.from_user.id)
            config_manager.add_query(str(chat_id), query)
            Logger.info(
                callback.from_user.id, f"Добавлен новый запрос '{query['tag']}'"
            )

        await state.clear()
        if isinstance(callback.message, Message):
            await callback.message.edit_text("✅ Запрос успешно сохранён.")

    except Exception as error:
        Logger.error(callback.from_user.id, f"(save_query): {error}")
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "❌ Не удалось сохранить запрос. Попробуйте ещё раз."
            )
