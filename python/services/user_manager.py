import time

from services.database import Database


class UserManager:
    def __init__(self, database: Database):
        self.database = database

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
