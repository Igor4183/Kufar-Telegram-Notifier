from datetime import datetime
from pathlib import Path
import zipfile

from services.path_manager import PathManager


class LogManager:
    def __init__(self):
        path_manager = PathManager()

        self.logs_directory = path_manager.logs_python
        self.archive_directory = path_manager.admin_logs

        self.logs_directory.mkdir(parents=True, exist_ok=True)

        file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        self.log_path = self.logs_directory / file_name

        if not self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8-sig")

    def write(self, level: str, chat_id: int | None, text: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat = "-" if chat_id is None else str(chat_id)
        message = f"[{current_time}] [{level}] [{chat}] {text}"

        print(message)

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(message + "\n")

    def get_logs(self) -> list[Path]:
        return sorted(self.logs_directory.glob("*.log"), reverse=True)

    def get_latest_log(self) -> Path | None:
        logs = self.get_logs()
        return logs[0] if logs else None

    def get_last_logs(self, count: int) -> list[Path]:
        return self.get_logs()[:count]

    def get_today_logs(self) -> list[Path]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [log for log in self.get_logs() if log.name.startswith(today)]

    def create_archive(self, logs: list[Path]) -> Path:
        self.archive_directory.mkdir(parents=True, exist_ok=True)

        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_path = self.archive_directory / f"python_logs_{date}.zip"

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for log in logs:
                archive.write(log, log.name)

        return archive_path
