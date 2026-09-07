import fcntl
import json
import time

from services.database import Database
from services.managers.models import Query
from services.path_manager import PathManager

path_manager = PathManager()

JSON_FIELDS = {
    "only-title-search",
    "price",
    "language",
    "currency",
    "condition",
    "seller-type",
    "kufar-delivery-required",
    "kufar-payment-required",
    "kufar-halva-required",
    "only-with-photos",
    "only-with-videos",
    "only-with-exchange-available",
    "sort-type",
    "category",
    "sub-category",
    "region",
    "areas",
}


class QueryManager:
    def __init__(self, database: Database):
        self.database = database
        self.path = path_manager.queries_path

    def _load_config(self) -> list[dict]:
        with open(self.path, "r", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            queries = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)

        if not isinstance(queries, list):
            raise ValueError("queries.json должен содержать массив запросов")

        return queries

    def _save_config(self, queries: list[dict]):
        with open(self.path, "r+", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_EX)

            file.seek(0)
            file.truncate()

            json.dump(queries, file, ensure_ascii=False, indent=4)

            file.flush()
            fcntl.flock(file, fcntl.LOCK_UN)

    def _get_query_config(self, query_id: int) -> dict:
        queries = self._load_config()

        found = None

        for query in queries:
            if "query_id" not in query:
                raise ValueError("В queries.json найден запрос без query_id")

            current_id = int(query["query_id"])

            if current_id == query_id:
                if found is not None:
                    raise ValueError(
                        f"query_id={query_id} встречается в queries.json несколько раз"
                    )

                found = query

        if found is None:
            raise KeyError(
                f"Для query_id={query_id} отсутствует конфигурация в queries.json"
            )

        return found

    def _build_query(self, row, config: dict) -> Query:
        price = config.get("price", {})

        return Query(
            query_id=row["query_id"],
            chat_id=row["chat_id"],
            tag=row["tag"],
            limit=row["limit"],
            start_time=row["start_time"],
            delay=row["delay"],
            only_title_search=config.get("only-title-search"),
            price_min=price.get("min"),
            price_max=price.get("max"),
            language=config.get("language"),
            currency=config.get("currency"),
            condition=config.get("condition"),
            seller_type=config.get("seller-type"),
            kufar_delivery_required=config.get("kufar-delivery-required"),
            kufar_payment_required=config.get("kufar-payment-required"),
            kufar_halva_required=config.get("kufar-halva-required"),
            only_with_photos=config.get("only-with-photos"),
            only_with_videos=config.get("only-with-videos"),
            only_with_exchange_available=config.get("only-with-exchange-available"),
            sort_type=config.get("sort-type"),
            category=config.get("category"),
            sub_category=config.get("sub-category"),
            region=config.get("region"),
            areas=config.get("areas"),
            enabled=bool(row["enabled"]),
        )

    def get_query(self, query_id: int) -> Query:
        row = self.database.execute(
            """
            SELECT query_id, chat_id, tag, "limit", start_time, delay, enabled
            FROM queries
            WHERE query_id = ?
            """,
            (query_id,),
        ).fetchone()

        if row is None:
            raise KeyError(f"Запрос query_id={query_id} отсутствует в базе данных")

        config = self._get_query_config(query_id)

        return self._build_query(row, config)

    def get_queries(self, chat_id: int | None = None) -> list[Query]:
        if chat_id is None:
            rows = self.database.execute("""
                SELECT query_id, chat_id, tag, "limit", start_time, delay, enabled
                FROM queries
                ORDER BY query_id
                """).fetchall()
        else:
            rows = self.database.execute(
                """
                SELECT query_id, chat_id, tag, "limit", start_time, delay, enabled
                FROM queries
                WHERE chat_id = ?
                ORDER BY query_id
                """,
                (chat_id,),
            ).fetchall()

        return [self.get_query(row["query_id"]) for row in rows]

    def create_query(
        self,
        chat_id: int,
        tag: str,
        query_config: dict,
        limit: int,
        start_time: int,
        delay: int,
    ) -> Query:
        created_at = int(time.time())

        cursor = self.database.execute(
            """
            INSERT INTO queries (
                chat_id,
                tag,
                "limit",
                start_time,
                delay,
                enabled,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 1, ?)
            """,
            (chat_id, tag, limit, start_time, delay, created_at),
        )

        query_id = cursor.lastrowid

        if query_id is None:
            self.database.rollback()
            raise RuntimeError("Не удалось получить query_id после создания запроса")

        config = self._filter_query_config(query_config)  # type: ignore
        config["query_id"] = query_id

        try:
            queries = self._load_config()
            queries.append(config)
            self._save_config(queries)
            self.database.commit()
        except Exception:
            self.database.rollback()
            raise

        return self.get_query(query_id)

    def _add_query_config(self, query_id: int, query: Query):
        queries = self._load_config()

        if any(int(item.get("query_id")) == query_id for item in queries):  # type: ignore
            raise ValueError(f"query_id={query_id} уже существует в queries.json")

        config = self._query_to_config(query)
        config["query_id"] = query_id

        queries.append(config)
        self._save_config(queries)

    def _query_to_config(self, query: Query) -> dict:
        config = {}

        if query.only_title_search is not None:
            config["only-title-search"] = query.only_title_search

        if query.price_min is not None or query.price_max is not None:
            config["price"] = {
                "min": query.price_min,
                "max": query.price_max,
            }

        if query.language is not None:
            config["language"] = query.language

        if query.currency is not None:
            config["currency"] = query.currency

        if query.condition is not None:
            config["condition"] = query.condition

        if query.seller_type is not None:
            config["seller-type"] = query.seller_type

        if query.kufar_delivery_required is not None:
            config["kufar-delivery-required"] = query.kufar_delivery_required

        if query.kufar_payment_required is not None:
            config["kufar-payment-required"] = query.kufar_payment_required

        if query.kufar_halva_required is not None:
            config["kufar-halva-required"] = query.kufar_halva_required

        if query.only_with_photos is not None:
            config["only-with-photos"] = query.only_with_photos

        if query.only_with_videos is not None:
            config["only-with-videos"] = query.only_with_videos

        if query.only_with_exchange_available is not None:
            config["only-with-exchange-available"] = query.only_with_exchange_available

        if query.sort_type is not None:
            config["sort-type"] = query.sort_type

        if query.category is not None:
            config["category"] = query.category

        if query.sub_category is not None:
            config["sub-category"] = query.sub_category

        if query.region is not None:
            config["region"] = query.region

        if query.areas is not None:
            config["areas"] = query.areas

        return config

    def delete_query(self, query_id: int):
        self._get_query_config(query_id)

        self.database.execute(
            "DELETE FROM queries WHERE query_id = ?",
            (query_id,),
        )

        self.database.commit()

        queries = self._load_config()
        queries = [query for query in queries if int(query["query_id"]) != query_id]

        self._save_config(queries)

    def set_enabled(self, query_id: int, enabled: bool):
        self._get_query_config(query_id)

        self.database.execute(
            """
            UPDATE queries
            SET enabled = ?
            WHERE query_id = ?
            """,
            (int(enabled), query_id),
        )

        self.database.commit()

    def get_query_config(self, query_id: int) -> dict:
        return self._get_query_config(query_id)

    def _filter_query_config(self, query_config: dict) -> dict:
        return {key: value for key, value in query_config.items() if key in JSON_FIELDS}

    def update_query(self, query_id: int, query_config: dict) -> Query:
        self._get_query_config(query_id)

        queries = self._load_config()
        filtered_config = self._filter_query_config(query_config)

        for index, config in enumerate(queries):
            if int(config["query_id"]) == query_id:
                queries[index] = {"query_id": query_id, **filtered_config}
                self._save_config(queries)
                return self.get_query(query_id)

        raise KeyError(
            f"Для query_id={query_id} отсутствует конфигурация в queries.json"
        )
