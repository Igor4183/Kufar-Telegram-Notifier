from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("""
**Kufar Telegram Notifier**

Бот для автоматического поиска новых объявлений на Kufar и отправки уведомлений в Telegram.

Для управления поисковыми запросами используйте команду /settings:
• добавление новых поисков;
• изменение параметров поиска;
• удаление существующих поисков.

После изменения настроек требуется некоторое время, чтобы они были применены. Новые параметры начинают использоваться во время следующего цикла поиска.

Доступные команды:
/settings — настройка поисковых запросов
/help — справка по использованию бота

Приятного использования!
""")


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("""
Доступные команды:

/start - запуск
/settings - настройки уведомлений
/help - помощь
""")
