import json
import time

from services.database import Database
from services.kufar.models import Ad
from services.managers.models import Query


class AdProcessor:
    def __init__(self, database: Database):
        self.database = database

    def process_ads(self, query: Query, ads: list[Ad]) -> list[Ad]:
        new_ads = []
        current_time = int(time.time())

        for ad in ads:
            if self._is_known(query.query_id, ad.ad_id):
                continue

            self._save_ad(ad, current_time)
            self._link_ad_to_query(query.query_id, ad.ad_id, current_time)

            if int(ad.list_time.timestamp()) < query.start_time:
                self._set_status(query.query_id, ad.ad_id, "ignored")
                continue

            new_ads.append(ad)

        self.database.commit()
        return new_ads

    def _is_known(self, query_id: int, ad_id: str) -> bool:
        result = self.database.execute(
            "SELECT 1 FROM query_ads WHERE query_id = ? AND ad_id = ?",
            (query_id, ad_id),
        ).fetchone()
        return result is not None

    def _save_ad(self, ad: Ad, current_time: int):
        self.database.execute(
            """
            INSERT OR IGNORE INTO ads (ad_id, account_id, subject, body, body_short, list_time, price_byn, price_usd, currency, ad_link, type, category, company_ad, phone_hidden, is_mine, raw_data, first_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ad.ad_id,
                ad.account_id,
                ad.subject,
                ad.body,
                ad.body_short,
                int(ad.list_time.timestamp()),
                ad.price_byn,
                ad.price_usd,
                ad.currency,
                ad.ad_link,
                ad.type,
                ad.category,
                int(ad.company_ad),
                int(ad.phone_hidden),
                int(ad.is_mine),
                json.dumps(ad.raw_data, ensure_ascii=False),
                current_time,
            ),
        )

    def _link_ad_to_query(self, query_id: int, ad_id: str, current_time: int):
        self.database.execute(
            "INSERT INTO query_ads (query_id, ad_id, first_seen_at, status) VALUES (?, ?, ?, 'new')",
            (query_id, ad_id, current_time),
        )

    def _set_status(self, query_id: int, ad_id: str, status: str):
        self.database.execute(
            "UPDATE query_ads SET status = ? WHERE query_id = ? AND ad_id = ?",
            (status, query_id, ad_id),
        )

    def mark_sent(self, query_id: int, ad_id: str):
        self.database.execute(
            "UPDATE query_ads SET status = 'sent', sent_at = ? WHERE query_id = ? AND ad_id = ?",
            (int(time.time()), query_id, ad_id),
        )
        self.database.commit()

    def mark_failed(self, query_id: int, ad_id: str):
        self.database.execute(
            "UPDATE query_ads SET status = 'failed' WHERE query_id = ? AND ad_id = ?",
            (query_id, ad_id),
        )
        self.database.commit()
