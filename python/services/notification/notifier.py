import asyncio

from aiogram import Bot
from aiogram.types import InputMediaPhoto, MediaUnion
from services.models import Ad, Query
from services.notification import NotificationFormatter
from services.cache_manager import CacheManager
from utils.logger import Logger


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_manager = CacheManager()
        self.notification_formatter = NotificationFormatter()

    async def send(self, query: Query, ads: list[Ad] | None) -> None:
        if ads is None:
            return

        for ad in ads:
            if (
                self.cache_manager.is_ad_cached(query.chat_id, ad.ad_id)
                or not query.enabled
            ):  # bad practice
                continue
            text = self.notification_formatter.format_ad(ad, query)
            if not ad.images:
                await self.bot.send_message(
                    chat_id=query.chat_id, text=text, parse_mode="HTML"
                )
            else:
                media: list[MediaUnion] = [
                    InputMediaPhoto(
                        media=ad.images[0].url, caption=text, parse_mode="HTML"
                    )
                ]
                for image in ad.images[1:10]:  # first 10 pictures
                    media.append(InputMediaPhoto(media=image.url))
                await self.bot.send_media_group(chat_id=query.chat_id, media=media)

            Logger.info(query.chat_id, f"{query.tag}: [{ad.title}], [{ad.link}]")
            self.cache_manager.save_ad(ad, query.query_id)
            self.cache_manager.save_cached_data(query.chat_id, ad.ad_id)
