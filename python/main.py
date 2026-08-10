import asyncio

from aiogram import Bot, Dispatcher
from handlers import start, settings, feedback, admin
from services.database import Database
from services.config_manager import ConfigManager
from services.user_manager import UserManager
from services.query_manager import QueryManager
from utils.logger import Logger

config_manager = ConfigManager()


async def main():
    bot = Bot(config_manager.get_bot_token())
    dp = Dispatcher()
    database = Database()
    user_manager = UserManager(database)
    query_manager = QueryManager(database, config_manager)

    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
