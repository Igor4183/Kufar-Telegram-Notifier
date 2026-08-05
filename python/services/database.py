import sqlite3
from pathlib import Path

from utils.logger import Logger


class Database:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.path = base_dir / "data" / "bot.db"

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.path)
            self.connection.row_factory = sqlite3.Row
            self._initialize()
            Logger.info(0, f"База данных подключена: {self.path}")

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка подключения к базе данных: {exc}")
            raise

    def _initialize(self):
        try:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at INTEGER NOT NULL
                )
                """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS user_limits (
                    chat_id INTEGER PRIMARY KEY,
                    max_queries INTEGER NOT NULL
                )
                """)
            self.connection.commit()

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка инициализации базы данных: {exc}")
            raise

    def execute(self, query, parameters=()):
        try:
            return self.connection.execute(query, parameters)

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка выполнения SQL-запроса: {exc}")
            raise

    def commit(self):
        try:
            self.connection.commit()

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка сохранения изменений в БД: {exc}")
            raise

    def close(self):
        try:
            self.connection.close()
            Logger.info(0, "Соединение с базой данных закрыто.")

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка закрытия базы данных: {exc}")
