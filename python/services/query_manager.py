from services.database import Database


class QueryManager:
    def __init__(self, database: Database):
        self.database = database

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
            return 10  # дефолтное значение максимального количества запросов
        return result["max_queries"]

    def set_max_queries(self, chat_id: int, max_queries: int):
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

    def can_add_query(self, chat_id: int, queries_count: int) -> bool:
        max_queries = self.get_max_queries(chat_id)
        if max_queries is None:
            return False
        return queries_count < max_queries
