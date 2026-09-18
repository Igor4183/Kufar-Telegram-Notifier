import asyncio
import aiohttp

from aiogram import Bot
from services.models import Query
from services.database import Database
from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from services.kufar import KufarService
from services.notification import NotificationService


class Scheduler:
    def __init__(self, bot: Bot, session: aiohttp.ClientSession):
        self.database = Database()
        self.config_manager = ConfigManager()
        self.query_manager = QueryManager(self.database, self.config_manager)
        self.kufar_service = KufarService(session)
        self.notification_service = NotificationService(bot)
        self.wakeup_event = asyncio.Event()
        self.running = False

    def update_queries(self):
        self.queries = self.query_manager.get_queries(None)

    async def run(self):
        self.running = True

        while self.running:
            self.update_queries()

            if not self.queries:
                self.wakeup_event.clear()
                await self.wakeup_event.wait()
                continue

            for query in self.queries:
                ads = await self.kufar_service.getAds(query)
                await self.notification_service.send(query, ads)

        await asyncio.sleep(10)  # заглушка

    def stop(self):
        self.wakeup_event.set()
        self.running = False
