import asyncio
import aiohttp

from aiogram import Bot, Dispatcher

from handlers import start, settings, feedback, admin
from services.database import Database
from services.kufar.service import KufarService
from services.managers import ConfigManager, UserManager, QueryManager
from services.notification import TelegramService, NotificationService
from services.processing import Scheduler, AdProcessor

config_manager = ConfigManager()
database = Database()
user_manager = UserManager(database, config_manager)
query_manager = QueryManager(database)


async def main():
    bot = Bot(config_manager.get_bot_token())
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(feedback.router)
    dp.include_router(admin.router)

    ad_processor = AdProcessor(database)
    telegram_service = TelegramService(bot)
    notification_service = NotificationService(telegram_service, ad_processor)

    async with aiohttp.ClientSession() as session:
        kufar_service = KufarService(session, config_manager)
        scheduler = Scheduler(
            query_manager,
            user_manager,
            kufar_service,
            ad_processor,
            notification_service,
        )

        scheduler_task = asyncio.create_task(scheduler.run())

        try:
            await dp.start_polling(bot, scheduler=scheduler)
        finally:
            scheduler.stop()
            await scheduler_task


if __name__ == "__main__":
    asyncio.run(main())
