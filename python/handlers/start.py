from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.logger import Logger
from services.database import Database
from services.user_manager import UserManager

router = Router()
database = Database()
user_manager = UserManager(database)


@router.message(Command("start"))
async def start_command(message: Message):
    Logger(message.chat.id, "/start")  # type: ignore
    user_manager.get_or_create_user(
        message.chat.id, message.from_user.username  # type: ignore
    )
    await message.answer(
        """
<b>Kufar Telegram Notifier<\b>

Бот для автоматического поиска новых объявлений на Kufar и отправки уведомлений в Telegram.

Для управления поисковыми запросами используйте команду /settings

После изменения настроек требуется некоторое время, чтобы они были применены. Новые параметры начинают использоваться во время следующего цикла поиска.

Узнать доступные команды можно с помощью команды /help

Приятного использования!
""",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def help_command(message: Message):
    Logger(message.chat.id, "/help")  # type: ignore
    await message.answer("""
Доступные команды:

/start - запуск
/settings - настройки уведомлений
/feedback - обратная связь
/help - помощь
""")
