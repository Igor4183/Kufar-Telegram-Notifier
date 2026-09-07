import time

from services.managers import ConfigManager
from services.database import Database


class UserManager:
    def __init__(self, database: Database, config_manager: ConfigManager):
        self.database = database
        self.config_manager = config_manager

    def get_user(self, chat_id: int):
        cursor = self.database.execute(
            """
            SELECT chat_id, username, created_at
            FROM users
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        return cursor.fetchone()

    def create_user(self, chat_id: int, username: str | None):
        self.database.execute(
            """
            INSERT INTO users (chat_id, username, created_at)
            VALUES (?, ?, ?)
            """,
            (chat_id, username, int(time.time())),
        )

        self.database.commit()

    def get_or_create_user(self, chat_id: int, username: str | None):
        user = self.get_user(chat_id)

        if user is None:
            self.create_user(chat_id, username)
            user = self.get_user(chat_id)

        return user

    def get_all_users(self) -> list:
        return self.database.execute(
            "SELECT chat_id, username FROM users ORDER BY created_at"
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
            return self.config_manager.get_default_max_queries()

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

    def get_query_count(self, chat_id: int) -> int:
        result = self.database.execute(
            """
            SELECT COUNT(*) AS count
            FROM queries
            WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()

        return result["count"]

    def can_add_query(self, chat_id: int) -> bool:
        return self.get_query_count(chat_id) < self.get_max_queries(chat_id)

    def get_priority(self, chat_id: int) -> int:
        return 0

    def get_all_query_limits(self) -> list[tuple[int, int]]:
        return self.database.execute(
            "SELECT chat_id, max_queries FROM user_limits ORDER BY chat_id"
        ).fetchall()
