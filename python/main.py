import asyncio

from aiogram import Bot, Dispatcher
from handlers import start, settings
from services.config_manager import ConfigManager

config_manager = ConfigManager()


async def main():
    bot = Bot(config_manager.get_bot_token())
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(settings.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
