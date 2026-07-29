from aiogram import Bot
from aiogram.fsm.context import FSMContext
from utils.logger import Logger
from keyboards.add_query import main_keyboard, other_keyboard


async def update_menu(bot: Bot | None, state: FSMContext):
    if bot is None:
        Logger.error(None, "(update_menu) bot is None")
        return
    data = await state.get_data()
    query, current_menu = data["query"], data["current_menu"]

    # текст сообщения
    if current_menu == "main":
        text = "⚙️ Настройка запроса\n\n"
        for key, value in query.items():
            text += f"{key}: {value}\n"
        text += "\nВыберите поле."
    else:
        text = "⚙️ Прочие параметры:"

    # клавиатура
    if current_menu == "main":
        keyboard = main_keyboard(query)
    else:
        keyboard = other_keyboard(query)

    await bot.edit_message_text(
        text=text,
        chat_id=data["menu_chat_id"],
        message_id=data["menu_message_id"],
        reply_markup=keyboard,
    )
