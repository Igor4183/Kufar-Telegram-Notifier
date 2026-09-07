from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.database import Database
from services.managers import ConfigManager, UserManager
from utils.logger import Logger

router = Router()

database = Database()
config_manager = ConfigManager()
user_manager = UserManager(database, config_manager)


@router.message(Command("start"))
async def start_command(message: Message):
    Logger.info(message.chat.id, "/start")
    user_manager.get_or_create_user(message.chat.id, message.from_user.username)  # type: ignore
    await message.answer(
        """
<b>Kufar Telegram Notifier</b>

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
    Logger.info(message.chat.id, "/help")  # type: ignore
    await message.answer("""
Доступные команды:

/start - запуск
/settings - настройки уведомлений
/feedback - обратная связь
/help - помощь
""")
