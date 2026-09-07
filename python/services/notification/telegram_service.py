from aiogram import Bot
from aiogram.types import InputMediaPhoto

from services.kufar.models import Ad
from services.managers.models import Query
from services.notification.formatter import NotificationFormatter


class TelegramService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_ad(self, chat_id: int, ad: Ad, query: Query):
        text = NotificationFormatter.format_ad(ad, query)

        if not ad.images:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            return

        media = [
            InputMediaPhoto(media=ad.images[0].url, caption=text, parse_mode="HTML")
        ]

        for image in ad.images[1:]:
            media.append(InputMediaPhoto(media=image.url))

        await self.bot.send_media_group(chat_id=chat_id, media=media)  # type: ignore
