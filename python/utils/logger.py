from services.log_manager import LogManager


class Logger:
    log_manager = LogManager()

    @staticmethod
    def info(chat_id: int | None, text: str):
        Logger.log_manager.write("INFO", chat_id, text)

    @staticmethod
    def warning(chat_id: int | None, text: str):
        Logger.log_manager.write("WARNING", chat_id, text)

    @staticmethod
    def error(chat_id: int | None, text: str):
        Logger.log_manager.write("ERROR", chat_id, text)
