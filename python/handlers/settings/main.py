from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.settings import settings_keyboard
from states.settings import AddQuery
from utils.logger import Logger
from views.settings import get_settings_text

router = Router()


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

    try:
        text = get_settings_text(callback.message.chat.id)
        await state.clear()
        await callback.message.edit_text(text, reply_markup=settings_keyboard())
    except Exception as error:
        Logger.error(callback.from_user.id, f"(back_to_settings): {error}")
        await callback.message.answer(
            "❌ Не удалось открыть настройки. Попробуйте ещё раз."
        )
