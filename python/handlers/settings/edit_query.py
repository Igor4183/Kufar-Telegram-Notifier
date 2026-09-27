from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.models import Query, Ad
from services.query_manager import QueryManager
from services.database import Database
from services.config_manager import ConfigManager
from utils.logger import Logger
from keyboards.settings import back_to_settings_keyboard
from states.settings import AddQuery
from views.settings import update_menu

router = Router()
database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database, config_manager)


@router.callback_query(F.data == "edit_query")
async def edit_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if not isinstance(callback.message, Message):
        return

    chat_id = callback.message.chat.id
    Logger.info(chat_id, "/settings -> edit_query")

    try:
        queries = query_manager.get_queries(chat_id)

        if not queries:
            await callback.message.edit_text("У вас нет настроенных поисков.")
            return

        text = "✏️ Выберите запрос для изменения:\n\n"

        for i in range(len(queries)):
            query = queries[i]
            tag = query.tag
            if tag is None:
                text += f"{i+1}. [UNDEFINDED]\n"
            else:
                text += f"{i+1}. {tag}\n"

        text += "\nВведите номер запроса:"

        await state.update_data(
            edit_mode=True,
            menu_chat_id=chat_id,
            menu_message_id=callback.message.message_id,
        )
        await state.set_state(AddQuery.waiting_for_edit)

        await callback.message.edit_text(text, reply_markup=back_to_settings_keyboard())
    except Exception as error:
        Logger.error(chat_id, f"(edit_query): {error}")
        await callback.message.answer(
            "❌ Не удалось получить список запросов. Попробуйте ещё раз."
        )


@router.message(AddQuery.waiting_for_edit)
async def process_edit(message: Message, state: FSMContext):
    if message.text is None or not message.text.isdigit():
        await message.answer("Введите номер запроса.")
        return

    number = int(message.text)

    try:
        queries = query_manager.get_queries(message.chat.id)

        if number <= 0 or number > len(queries):
            await message.answer("❌ Нет такого номера.")
            return

        query: Query = queries[number - 1]

        Logger.info(
            message.chat.id,
            f"/settings -> edit_query -> выбран запрос №{number}: {query}",
        )

        await state.update_data(query=query, query_number=number, current_menu="main")

        await state.set_state(AddQuery.editing)
        await update_menu(message.bot, state)
    except Exception as error:
        Logger.error(message.chat.id, f"(process_edit): {error}")
        await message.answer("❌ Не удалось открыть запрос для редактирования.")


@router.callback_query(F.data == "remove_query")
async def delete_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.message is None:
        return

    chat_id = callback.message.chat.id
    Logger.info(chat_id, "/settings -> remove_query")

    try:
        queries = query_manager.get_queries(chat_id)
        if len(queries) == 0:
            await callback.message.answer("У вас нет настроенных поисков.")
            return

        text = "Введите номер объявления для удаления:\n\n"

        for number, query in enumerate(queries, 1):
            if query.tag is None:
                text += f"{number}. [UNDEFINDED]\n"
            else:
                text += f"{number}. {query.tag}\n"

        await callback.message.answer(text, reply_markup=back_to_settings_keyboard())
        await state.set_state(AddQuery.waiting_for_delete)
    except Exception as error:
        Logger.error(chat_id, f"(delete_query): {error}")
        await callback.message.answer("❌ Не удалось получить список запросов.")


@router.message(AddQuery.waiting_for_delete)
async def process_delete(message: Message, state: FSMContext):
    if message.text is None or not message.text.isdigit():
        await message.answer("Введите номер.")
        return

    index = int(message.text)

    try:
        config = query_manager.get_queries(message.chat.id)
        if index <= 0 or index > len(config):
            await message.answer("Нет такого номера.")
            return
        query = query_manager.get_query(index, message.chat.id)
        Logger.info(
            message.chat.id, f"Запрос под номером {index} удалён. " + str(query)
        )
        query_manager.remove_query(message.chat.id, index)

        await state.clear()
        await message.answer("✅ Запрос удалён.")
    except Exception as error:
        Logger.error(message.chat.id, f"(process_delete): {error}")
        await message.answer("❌ Не удалось удалить запрос. Попробуйте ещё раз.")
