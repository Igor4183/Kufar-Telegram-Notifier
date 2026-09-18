import asyncio

from aiogram import Bot
from aiogram.types import InputMediaPhoto
from services.models import Ad, Query
from services.notification import NotificationFormatter
from services.cache_manager import CacheManager


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_manager = CacheManager()
        self.notification_formatter = NotificationFormatter()

    async def send(self, query: Query, ads: list[Ad] | None) -> None:
        if ads is None:
            return

        for ad in ads:
            if self.cache_manager.is_ad_cached(ad.id):
                continue
            text = self.notification_formatter.format_ad(ad, query)
            if not ad.images:
                await self.bot.send_message(
                    chat_id=query.chat_id, text=text, parse_mode="HTML"
                )
                return
            media = [
                InputMediaPhoto(media=ad.images[0].url, caption=text, parse_mode="HTML")
            ]
            for image in ad.images[1:]:
                media.append(InputMediaPhoto(media=image.url))
            await self.bot.send_media_group(chat_id=chat_id, media=media)  # type: ignore
