from services.kufar.models import Ad
from services.managers.models import Query
from services.notification.telegram_service import TelegramService
from services.processing.ad_processor import AdProcessor


class NotificationService:
    def __init__(self, telegram_service: TelegramService, ad_processor: AdProcessor):
        self.telegram_service = telegram_service
        self.ad_processor = ad_processor

    async def notify(self, query: Query, ads: list[Ad]):
        for ad in ads:
            try:
                await self.telegram_service.send_ad(query.chat_id, ad, query)
                self.ad_processor.mark_sent(query.query_id, ad.ad_id)
            except Exception as exc:
                self.ad_processor.mark_failed(query.query_id, ad.ad_id)
                print(f"Ошибка отправки ad_id={ad.ad_id}: {exc}")
