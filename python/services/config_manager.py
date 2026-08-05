from pathlib import Path

import json
import fcntl


class ConfigManager:

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        self.path = project_root / "data" / "kufar-configuration.json"

    def get_bot_token(self):
        config = self.load()
        return config["telegram"]["bot-token"]

    def get_support_chat_id(self) -> int:
        config = self.load()
        return int(config["telegram"]["support-chat-id"])

    def get_admin_chat_id(self) -> int:
        config = self.load()
        return int(config["telegram"]["chat-id"])

    def load(self):
        with open(self.path, "r", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            config = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)
            return config

    def save(self, config):
        with open(self.path, "r+", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_EX)

            file.seek(0)
            file.truncate()

            json.dump(config, file, ensure_ascii=False, indent=4)
            file.flush()
            fcntl.flock(file, fcntl.LOCK_UN)

    def get_queries(self, chat_id: str | None) -> list:
        config = self.load()
        result = []
        for query in config["queries"]:
            if chat_id is None:
                result.append(query)
            elif "chat-id" not in query:
                if config["telegram"]["chat-id"] == chat_id:
                    result.append(query)
            elif query["chat-id"] == chat_id:
                result.append(query)
        return result

    def add_query(self, chat_id: str, query: dict):
        config = self.load()
        if "queries" not in config:
            config["queries"] = []
        config["queries"].append(query)
        self.save(config)

    def remove_query(self, chat_id: str, number: int):  # number — 1-index
        config = self.load()
        current_number = 0
        for index, query in enumerate(config["queries"]):
            owner = query.get("chat-id", config["telegram"]["chat-id"])
            if owner != chat_id:
                continue
            current_number += 1
            if current_number == number:
                del config["queries"][index]
                self.save(config)
                return
        raise IndexError("Query number out of range")

    def get_query(self, number: int, chat_id: str | None = None) -> dict | None:
        config = self.load()
        current_number = 0
        for query in config["queries"]:
            owner = query.get("chat-id", config["telegram"]["chat-id"])
            if chat_id is not None and owner != chat_id:
                continue
            current_number += 1
            if current_number == number:
                return query
        raise IndexError("Query number out of range")

    def update_query(self, chat_id: str, number: int, query: dict):
        config = self.load()
        current_number = 0
        for index, current_query in enumerate(config["queries"]):
            owner = current_query.get(
                "chat-id",
                config["telegram"]["chat-id"],
            )
            if owner != chat_id:
                continue
            current_number += 1
            if current_number == number:
                config["queries"][index] = query
                self.save(config)
                return
        raise IndexError("Query number out of range")
