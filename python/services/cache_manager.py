import sqlite3

from time import time
from services.models import Ad
from services.database import Database


class CacheManager:
    def __init__(self):
        self.database = Database()

    def is_ad_cached(self, chat_id: int, ad_id: int) -> bool:
        cursor = self.database.execute(
            """
            SELECT 1
            FROM cached_data
            WHERE chat_id = ? AND ad_id = ?
            LIMIT 1
            """,
            (chat_id, ad_id),
        )
        return cursor.fetchone() is not None

    def save_ad(self, ad: Ad, query_id: int) -> None:
        self.database.execute(
            """
            INSERT OR IGNORE INTO cached_ads (
                ad_id,
                kufar_api_json_id,
                query_id,
                subject,
                list_time,
                price_byn,
                ad_link,
                category,
                company,
                phone_hidden,
                first_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ad.ad_id,
                ad.json_id,
                query_id,
                ad.subject,
                int(ad.list_time.timestamp()),
                int(ad.price_byn) if ad.price_byn else None,
                ad.ad_link,
                int(ad.category) if ad.category else None,
                int(ad.company_ad) if ad.company_ad is not None else None,
                int(ad.phone_hidden) if ad.phone_hidden is not None else None,
                int(time()),
            ),
        )
        self.database.commit()

    def save_cached_data(self, chat_id: int, ad_id: int) -> None:
        self.database.execute(
            """
            INSERT OR IGNORE INTO cached_data (chat_id, ad_id)
            VALUES (?, ?)
            """,
            (chat_id, ad_id),
        )

        self.database.commit()

    def get_cached_data(self) -> list[dict]:
        cursor = self.database.execute("""
            SELECT
                cd.chat_id,
                ca.ad_id,
                ca.subject,
                ca.list_time,
                ca.price_byn,
                ca.ad_link,
                ca.category,
                ca.company,
                ca.phone_hidden,
                ca.first_seen
            FROM cached_data cd
            JOIN cached_ads ca ON ca.ad_id = cd.ad_id
            ORDER BY ca.first_seen DESC
            """)

        return [dict(row) for row in cursor.fetchall()]
