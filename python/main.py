import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from handlers import start, settings, feedback, admin
from services.config_manager import ConfigManager
from utils.logger import Logger
from services.scheduler import Scheduler


async def main():
    config_manager = ConfigManager()

    bot = Bot(config_manager.bot_token)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)

    async with aiohttp.ClientSession() as session:
        scheduler = Scheduler(bot, session)
        scheduler_task = asyncio.create_task(scheduler.run())
        try:
            await dp.start_polling(bot)
        finally:
            scheduler.stop()
            scheduler_task.cancel()

            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    asyncio.run(main())
