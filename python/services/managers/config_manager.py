import fcntl
import json

from services.path_manager import PathManager

path_manager = PathManager()


class ConfigManager:
    def __init__(self):
        self.path = path_manager.config_path

    def load(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            config = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)

        return config

    def get_bot_token(self) -> str:
        return self.load()["bot-token"]

    def get_support_chat_id(self) -> int:
        return int(self.load()["support-chat-id"])

    def get_kufar_api(self) -> str:
        return self.load()["kufar-api"]

    def get_default_max_queries(self) -> int:
        return int(self.load()["constants"]["default-max-queries"])

    def get_kufar_default_max_price(self) -> int:
        return int(self.load()["constants"]["kufar-default-max-price"])

    def get_kufar_timeout(self) -> int:
        return int(self.load()["constants"]["kufar-timeout"])

    def get_admin_chat_id(self) -> int:
        return int(self.load()["admin-chat-id"])
