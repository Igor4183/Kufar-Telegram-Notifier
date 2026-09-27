from services.database import Database
from services.config_manager import ConfigManager
from services.path_manager import PathManager
from utils.logger import Logger
from services.models import Query
import json
import fcntl


class QueryManager:
    def __init__(self, database: Database, config_manager: ConfigManager):
        self.path = PathManager().queries_path
        self.database = database
        self.config_manager = config_manager

    def _load_queries(self) -> list:
        with open(self.path, "r", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            config = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)
            return config

    def _save_queries(self, config) -> None:
        with open(self.path, "r+", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.seek(0)
            file.truncate()
            json.dump(config, file, ensure_ascii=False, indent=4)
            file.flush()
            fcntl.flock(file, fcntl.LOCK_UN)

    def get_all_query_limits(self) -> list[tuple[int, int]]:
        return self.database.execute(
            "SELECT chat_id, max_queries FROM user_limits"
        ).fetchall()

    def get_max_queries(self, chat_id: int) -> int:
        cursor = self.database.execute(
            """
            SELECT max_queries
            FROM user_limits
            WHERE chat_id = ?
            """,
            (chat_id,),
        )
        result = cursor.fetchone()
        if result is None:
            return self.config_manager.default_max_queries
        return result["max_queries"]

    def set_max_queries(self, chat_id: int, max_queries: int) -> None:
        self.database.execute(
            """
            INSERT INTO user_limits (chat_id, max_queries)
            VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET max_queries = excluded.max_queries
            """,
            (chat_id, max_queries),
        )
        self.database.commit()

    # добавляет запрос согласно dict, где уже храниться chat_id
    def add_query(self, query: Query) -> None:
        queries = self._load_queries()
        queries.append(self._query_to_dict(query))
        self._save_queries(queries)

    # ищет n-ый запрос пользователя начиная с 1
    def get_query(self, number: int, chat_id: int | None = None) -> Query | None:
        config = self._load_queries()
        current_number = 1

        for query in config:
            query_chat_id = query.get("chat-id", None)

            if chat_id is not None and query_chat_id != chat_id:
                continue

            if current_number == number:
                return self._build_query(query)

            current_number += 1

        Logger.error(chat_id, "query_manager: Query number out of range")
        return None

    def _build_query(self, query: dict) -> Query:
        price = query.get("price", {})

        return Query(
            chat_id=query["chat-id"],
            tag=query.get("tag"),
            query_id=query.get("query-id", 0),
            delay=query.get("delay", self.config_manager.default_delay),
            limit=query.get("limit", self.config_manager.default_limit),
            start_time=query.get("start-time"),
            only_title_search=query.get("only-title-search", False),
            price_min=price.get("min"),
            price_max=price.get("max"),
            language=query.get("language"),
            currency=query.get("currency"),
            condition=query.get("condition"),
            seller_type=query.get("seller-type"),
            kufar_delivery_required=query.get("kufar-delivery-required", False),
            kufar_payment_required=query.get("kufar-payment-required", False),
            kufar_halva_required=query.get("kufar-halva-required", False),
            only_with_photos=query.get("only-with-photos", False),
            only_with_videos=query.get("only-with-videos", False),
            only_with_exchange_available=query.get(
                "only-with-exchange-available", False
            ),
            sort_type=query.get("sort-type"),
            category=query.get("category"),
            sub_category=query.get("sub-category"),
            region=query.get("region"),
            areas=query.get("areas"),
            url=query.get("url"),
            enabled=query.get("enabled", True),
        )

    def _query_to_dict(self, query: Query) -> dict:
        result = {
            "query-id": query.query_id,
            "chat-id": query.chat_id,
            "tag": query.tag,
            "limit": query.limit,
            "start-time": query.start_time,
            "delay": query.delay,
            "only-title-search": query.only_title_search,
            "language": query.language,
            "currency": query.currency,
            "condition": query.condition,
            "seller-type": query.seller_type,
            "kufar-delivery-required": query.kufar_delivery_required,
            "kufar-payment-required": query.kufar_payment_required,
            "kufar-halva-required": query.kufar_halva_required,
            "only-with-photos": query.only_with_photos,
            "only-with-videos": query.only_with_videos,
            "only-with-exchange-available": query.only_with_exchange_available,
            "sort-type": query.sort_type,
            "category": query.category,
            "sub-category": query.sub_category,
            "region": query.region,
            "areas": query.areas,
            "url": query.url,
            "enabled": query.enabled,
        }

        if query.price_min is not None or query.price_max is not None:
            result["price"] = {
                "min": query.price_min,
                "max": query.price_max,
            }

        return result

    def get_queries(
        self, chat_id: int | None
    ) -> list[
        Query
    ]:  # Возвращает список запросов пользователя, если указан chat_id, иначе - весь список
        result = []
        config = self._load_queries()
        for query in config:
            if chat_id is None:
                result.append(self._build_query(query))
            elif chat_id == query["chat-id"]:
                result.append(self._build_query(query))
        return result

    # изменяет n-ый запрос пользователя начиная с 1
    def update_query(self, chat_id: int, number: int, query: Query) -> bool:
        queries = self._load_queries()
        current_number = 1

        for index, current_query in enumerate(queries):
            query_chat_id = current_query.get("chat-id", None)
            if query_chat_id != chat_id:
                continue

            if current_number == number:
                queries[index] = self._query_to_dict(query)
                self._save_queries(queries)
                return True

            current_number += 1

        Logger.error(chat_id, "query_manager: Query number out of range")
        return False

    def remove_query(
        self, chat_id: int, index: int
    ) -> bool:  # удаляет n-ый запрос пользователя начиная с 1
        queries = self._load_queries()
        current_number = 1

        for query_index, query in enumerate(queries):
            query_chat_id = query.get("chat-id", None)
            if query_chat_id != chat_id:
                continue

            if current_number == index:
                queries.pop(query_index)
                self._save_queries(queries)
                return True

            current_number += 1

        Logger.error(chat_id, "query_manager: Query number out of range")
        return False

    def can_add_query(self, chat_id: int) -> bool:
        queries_count = len(self.get_queries(chat_id))
        max_queries = self.get_max_queries(chat_id)
        return queries_count < max_queries

    def get_next_query_id(self) -> int:
        queries = self.get_queries(None)
        if not queries:
            return 1
        max_query_id = max(query.query_id for query in queries)
        return max_query_id + 1

    def set_query_enabled(self, chat_id: int, query_id: int, enabled: bool) -> bool:
        queries = self._load_queries()
        for query in queries:
            if query.get("chat-id") != chat_id:
                continue
            if query.get("query-id") != query_id:
                continue

            query["enabled"] = enabled
            self._save_queries(queries)
            return True

        Logger.error(chat_id, f"query_manager: Query not found: query_id={query_id}")
        return False
