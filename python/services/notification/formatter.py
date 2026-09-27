from html import escape

from services.models import Ad, Query


class NotificationFormatter:
    @staticmethod
    def format_ad(ad: Ad, query: Query) -> str:
        date = ad.list_time.strftime("%a %b %d %H:%M:%S %Y")
        seller = ad.get_account_parameter("name")
        seller_name = seller.value if seller is not None else "Не указан"
        price = int(ad.price_byn) / 100 if ad.price_byn is not None else 0

        text = (
            f"<b>{escape(ad.title) if ad.title is not None else "[UNDEFINDED]"}</b>\n\n"
        )
        text += f"<b>{price:.2f} BYN</b>\n"
        text += f"{escape(str(seller_name))}\n"
        text += f"{date}\n"
        text += f"{'Телефон скрыт' if ad.phone_hidden else 'Телефон не скрыт'}\n"
        text += f"Количество фотографий в объявлении: {len(ad.images)}\n"

        if ad.body:
            description = " ".join(ad.body.split())
            if len(description) > 350:
                description = description[:350].rstrip() + "…"
            text += f"\n{escape(description)}\n"

        text += f'\n🔗 <a href="{ad.link}">Открыть объявление на Kufar</a>\n'

        if query.tag:
            tag = query.tag.lower().replace(" ", "_")
            text += f"\n#{escape(tag)}"

        return text
