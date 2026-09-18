from services.path_manager import PathManager
from utils.logger import Logger

import json
import fcntl


class ConfigManager:

    def __init__(self):
        self.path = PathManager().config_path
        self.update_params()

    def _load_config(self):
        with open(self.path, "r", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            config = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)
            return config

    def _save_config(self, config):
        with open(self.path, "r+", encoding="utf-8") as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.seek(0)
            file.truncate()
            json.dump(config, file, ensure_ascii=False, indent=4)
            file.flush()
            fcntl.flock(file, fcntl.LOCK_UN)

    def update_params(self):
        try:
            config = self._load_config()
            self.bot_token = config["bot-token"]
            self.support_chat_id = config["support-chat-id"]
            self.admin_chat_id = config["admin-chat-id"]
            self.limit_coefficient = config["limit-coefficient"]
            self.kufar_api = config["kufar-api"]
            self.default_delay = config["constants"]["default-delay"]
            self.default_max_queries = config["constants"]["default-max-queries"]
            self.default_limit = config["constants"]["default-limit"]
            self.kufar_default_max_price = config["constants"][
                "kufar-default-max-price"
            ]
            self.kufar_timeout = config["constants"]["kufar-timeout"]
        except Exception as exc:
            Logger.error(
                None,
                "Ошибка config_manager в обновлении параметров "
                f"[{type(exc).__name__}]: {exc}",
            )
            raise
