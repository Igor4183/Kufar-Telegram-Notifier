import asyncio
import heapq
import time

from services.kufar.service import KufarService
from services.managers.models import Query
from services.managers.query_manager import QueryManager
from services.managers.user_manager import UserManager
from services.notification.notification_service import NotificationService
from services.processing.ad_processor import AdProcessor


class Scheduler:
    def __init__(
        self,
        query_manager: QueryManager,
        user_manager: UserManager,
        kufar_service: KufarService,
        ad_processor: AdProcessor,
        notification_service: NotificationService,
    ):
        self.query_manager = query_manager
        self.user_manager = user_manager
        self.kufar_service = kufar_service
        self.ad_processor = ad_processor
        self.notification_service = notification_service
        self.queue = []
        self.queries: dict[int, Query] = {}
        self.wakeup_event = asyncio.Event()
        self.running = False

    def add_query(self, query: Query, delay: float = 0):
        if not query.enabled:
            return

        self.remove_query(query.query_id)

        priority = self.user_manager.get_priority(query.chat_id)
        next_run = time.time() + delay

        heapq.heappush(self.queue, (next_run, -priority, query.query_id))
        self.queries[query.query_id] = query
        self.wakeup_event.set()

    def remove_query(self, query_id: int):
        self.queries.pop(query_id, None)
        self.wakeup_event.set()

    def load_queries(self):
        self.queue.clear()
        self.queries.clear()

        for query in self.query_manager.get_queries():
            self.add_query(query)

    async def run(self):
        self.running = True
        self.load_queries()

        while self.running:
            if not self.queue:
                self.wakeup_event.clear()
                await self.wakeup_event.wait()
                continue

            next_run, _, query_id = self.queue[0]
            current_time = time.time()
            wait_time = next_run - current_time

            if wait_time > 0:
                self.wakeup_event.clear()

                try:
                    await asyncio.wait_for(self.wakeup_event.wait(), timeout=wait_time)
                except asyncio.TimeoutError:
                    pass

                continue

            heapq.heappop(self.queue)

            query = self.queries.get(query_id)

            if query is None or not query.enabled:
                continue

            await self._process_query(query)

            if query.query_id in self.queries and query.enabled:
                self.add_query(query, query.delay)

    async def _process_query(self, query: Query):
        try:
            result = await self.kufar_service.get_ads(query)
            new_ads = self.ad_processor.process_ads(query, result.ads)

            if new_ads:
                await self.notification_service.notify(query, new_ads)

        except Exception as exc:
            print(f"Ошибка обработки query_id={query.query_id}: {exc}")

    def stop(self):
        self.running = False
        self.wakeup_event.set()
