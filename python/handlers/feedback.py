import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyParameters, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.feedback import feedback_keyboard
from services.config_manager import ConfigManager
from states.feedback import Feedback
from utils.logger import Logger

router = Router()
config_manager = ConfigManager()


@router.message(Command("feedback"))
async def feedback_command(message: Message, state: FSMContext):
    Logger.info(message.chat.id, "/feedback")
    await state.set_state(Feedback.waiting_for_message)
    await message.answer(
        "Напишите сообщение, которое хотите отправить разработчику.",
        reply_markup=feedback_keyboard(),
    )


@router.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    Logger.info(
        callback.from_user.id,
        "/feedback -> создание обращения отменено",
    )
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text("❌ Отправка обращения отменена.")


@router.message(Feedback.waiting_for_message)
async def process_feedback(message: Message, state: FSMContext):
    if message.text is None:
        await message.answer(
            "Пожалуйста, отправьте текстовое сообщение. Попробуйте ещё раз."
        )
        return

    support_chat_id = config_manager.get_support_chat_id()
    username = message.from_user.username  # type: ignore
    first_name = message.from_user.first_name  # type: ignore

    if username:
        user_tag = f"@{username}"
    else:
        user_tag = first_name

    text = (
        "📩 Новое обращение\n\n"
        f"👤 Пользователь: {user_tag}\n"
        f"🆔 Chat ID: {message.chat.id}\n"
        f"🆔 Message ID: {message.message_id}\n\n"
        f"💬 Сообщение:\n{message.text}"
    )

    await message.bot.send_message(chat_id=support_chat_id, text=text)  # type: ignore

    Logger.info(message.chat.id, f"/feedback -> отправлено обращение:\n {message.text}")

    await state.clear()
    await message.answer("✅ Сообщение отправлено разработчику.")


@router.message(F.reply_to_message)
async def reply_to_feedback(message: Message):

    support_chat_id = config_manager.get_support_chat_id()

    if message.chat.id != support_chat_id:
        return

    if message.reply_to_message is None:
        return

    if message.reply_to_message.text is None:
        Logger.warning(
            message.chat.id, "(support chat) Пустое сообщение в ответе на /feedback"
        )
        await message.answer("❌ Это не сообщение обратной связи.")
        return

    feedback_text = "" + message.reply_to_message.text

    if not feedback_text.startswith("📩 Новое обращение"):
        Logger.warning(message.chat.id, "(support chat) Reply на рандомное сообшение")
        await message.answer("❌ Это не сообщение обратной связи.")
        return

    match = re.search(r"🆔 Chat ID: (-?\d+)\n🆔 Message ID: (\d+)", feedback_text)

    if match is None:
        Logger.error(
            message.chat.id, "(support chat)Не удалось определить пользователя"
        )
        await message.answer("❌ Не удалось определить пользователя.")
        return

    chat_id = int(match.group(1))
    user_message_id = int(match.group(2))

    if message.text is None:
        Logger.warning(
            message.chat.id, "(support chat) Ответ должен быть текстовым сообщением."
        )
        await message.answer("❌ Ответ должен быть текстовым сообщением.")
        return

    try:
        await message.bot.send_message(  # type: ignore
            chat_id=chat_id,
            text=message.text,
            reply_parameters=ReplyParameters(message_id=user_message_id),
        )
        username_match = re.search(r"👤 Пользователь: (.+)", feedback_text)
        if username_match:
            username = username_match.group(1)
            await message.answer(f"✅ Ответ отправлен {username}")
        else:
            await message.answer(f"✅ Ответ отправлен пользователю {chat_id}")

        Logger.info(
            message.chat.id, f"Ответ отправлен пользователю {chat_id}: {message.text}"
        )

    except Exception as exc:
        Logger.error(
            message.chat.id, f"Ошибка отправки ответа пользователю {chat_id}: {exc}"
        )
        await message.answer("❌ Не удалось отправить ответ пользователю.")
