import sqlite3
from services.path_manager import PathManager

from utils.logger import Logger

path_manager = PathManager()


class Database:
    def __init__(self):
        self.path = path_manager.database_path

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._initialize()

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
                    max_queries INTEGER NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id) ON DELETE CASCADE
                )
                """)

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    "limit" INTEGER NOT NULL,
                    start_time INTEGER NOT NULL,
                    delay INTEGER NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id) ON DELETE CASCADE
                )
                """)

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    ad_id TEXT PRIMARY KEY,
                    account_id TEXT,
                    subject TEXT,
                    body TEXT,
                    body_short TEXT,
                    list_time INTEGER NOT NULL,
                    price_byn TEXT,
                    price_usd TEXT,
                    currency TEXT,
                    ad_link TEXT,
                    type TEXT,
                    category TEXT,
                    company_ad INTEGER NOT NULL,
                    phone_hidden INTEGER NOT NULL,
                    is_mine INTEGER NOT NULL,
                    raw_data TEXT NOT NULL,
                    first_seen_at INTEGER NOT NULL
                )
                """)

            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS query_ads (
                    query_id INTEGER NOT NULL,
                    ad_id TEXT NOT NULL,
                    first_seen_at INTEGER NOT NULL,
                    sent_at INTEGER,
                    status TEXT NOT NULL DEFAULT 'new',
                    PRIMARY KEY (query_id, ad_id),
                    FOREIGN KEY (query_id) REFERENCES queries(query_id) ON DELETE CASCADE,
                    FOREIGN KEY (ad_id) REFERENCES ads(ad_id) ON DELETE CASCADE
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

    def rollback(self):
        try:
            self.connection.rollback()

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка отката изменений в БД: {exc}")
            raise

    def close(self):
        try:
            self.connection.close()
            Logger.info(0, "Соединение с базой данных закрыто.")

        except sqlite3.Error as exc:
            Logger.error(0, f"Ошибка закрытия базы данных: {exc}")
