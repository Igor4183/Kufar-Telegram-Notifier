import asyncio
import aiohttp
import heapq
import time

from aiogram import Bot
from services.models import Query
from services.database import Database
from services.config_manager import ConfigManager
from services.query_manager import QueryManager
from services.kufar import KufarService, UrlBuilder
from services.notification import NotificationService
from utils.logger import Logger


class Scheduler:
    def __init__(self, bot: Bot, session: aiohttp.ClientSession):
        self.database = Database()
        self.config_manager = ConfigManager()
        self.query_manager = QueryManager(self.database, self.config_manager)
        self.kufar_service = KufarService(session)
        self.notification_service = NotificationService(bot)

        self.queries: dict[int, Query] = {}
        self.queue: list[tuple[float, int]] = []
        self.next_runs: dict[int, float] = {}

        self.wakeup_event = asyncio.Event()
        self.running = False

    def update_queries(self):
        queries = self.query_manager.get_queries(None)
        query_ids = {query.query_id for query in queries if query.enabled}

        for query in queries:
            if not query.enabled:
                self.next_runs.pop(query.query_id, None)
                continue
            self.queries[query.query_id] = query
            if query.query_id not in self.next_runs:
                self.next_runs[query.query_id] = time.monotonic()

        for query_id in list(self.queries):
            if query_id not in query_ids:
                self.queries.pop(query_id)
                self.next_runs.pop(query_id, None)

        self.queue = [
            (next_run, query_id)
            for query_id, next_run in self.next_runs.items()
            if query_id in self.queries
        ]

        heapq.heapify(self.queue)

    async def run(self):
        self.running = True
        self.update_queries()

        while self.running:
            self.update_queries()
            if not self.queue:
                self.wakeup_event.clear()

                try:
                    await asyncio.wait_for(
                        self.wakeup_event.wait(),
                        timeout=1,
                    )
                except asyncio.TimeoutError:
                    pass
                continue

            next_run, query_id = self.queue[0]
            wait_time = next_run - time.monotonic()

            if wait_time > 0:
                self.wakeup_event.clear()
                try:
                    await asyncio.wait_for(
                        self.wakeup_event.wait(),
                        timeout=min(wait_time, 1),
                    )
                except asyncio.TimeoutError:
                    pass
                continue

            heapq.heappop(self.queue)
            query = self.queries.get(query_id)
            if query is None or not query.enabled:
                continue  # query всегда включён из-за update_query

            start_time = time.monotonic()
            try:
                ads = await asyncio.wait_for(
                    self.kufar_service.getAds(query),
                    timeout=self.config_manager.kufar_timeout,
                )
                if ads == []:
                    Logger.warning(
                        query.chat_id,
                        f"Kufar returned empty response [query_id: {query_id}] [url: {UrlBuilder(self.config_manager).build_url(query)}]",
                    )
                if ads:
                    await self.notification_service.send(query, ads)
            except asyncio.TimeoutError:
                Logger.warning(query.chat_id, f"Таймаут query_id={query.query_id}")
            except Exception as error:
                Logger.error(
                    query.chat_id,
                    f"Ошибка обработки query_id={query.query_id}: {error}",
                )
            finally:
                elapsed = time.monotonic() - start_time
                if elapsed < self.config_manager.kufar_min_execution_time:
                    await asyncio.sleep(
                        self.config_manager.kufar_min_execution_time - elapsed
                    )

            self.next_runs[query_id] = time.monotonic() + query.delay
            heapq.heappush(
                self.queue,
                (self.next_runs[query_id], query_id),
            )

    def stop(self):
        self.running = False
        self.wakeup_event.set()
