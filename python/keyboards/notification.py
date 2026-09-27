from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def notification_keyboard(ad_link: str, query_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🔗 Открыть объявление", url=ad_link)
    builder.button(
        text="🔕 Отключить уведомления", callback_data=f"disable_query:{query_id}"
    )

    builder.adjust(2)
    return builder.as_markup()


# Нигде не подключена и наверное не будет.
