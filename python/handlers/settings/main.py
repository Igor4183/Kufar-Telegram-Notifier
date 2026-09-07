from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database import Database
from services.managers import ConfigManager, QueryManager, UserManager
from keyboards.settings import settings_keyboard
from states.settings import AddQuery
from utils.logger import Logger
from views.settings import get_settings_text

router = Router()

database = Database()
config_manager = ConfigManager()
query_manager = QueryManager(database)
user_manager = UserManager(database, config_manager)


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
