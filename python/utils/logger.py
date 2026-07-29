from pathlib import Path
from datetime import datetime


class Logger:
    project_root = Path(__file__).resolve().parents[2]
    log_directory = project_root / "data" / "logs_python"
    log_directory.mkdir(parents=True, exist_ok=True)
    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    path = log_directory / file_name
    file = open(path, "a", encoding="utf-8")

    @staticmethod
    def _write(level: str, chat_id: int | None, text: str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat = "-" if chat_id is None else str(chat_id)
        message = f"[{current_time}] [{level}] [{chat}] {text}"

        print(message)
        Logger.file.write(message + "\n")
        Logger.file.flush()

    @staticmethod
    def info(chat_id: int | None, text: str):
        Logger._write("INFO", chat_id, text)

    @staticmethod
    def warning(chat_id: int | None, text: str):
        Logger._write("WARNING", chat_id, text)

    @staticmethod
    def error(chat_id: int | None, text: str):
        Logger._write("ERROR", chat_id, text)
