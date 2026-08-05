from datetime import datetime
from enum import Enum
from pathlib import Path
import re
import zipfile


class LogType(Enum):
    PYTHON = "python"
    CPP = "cpp"


class LogManager:
    LOG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.log$")

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.logs = {
            LogType.PYTHON: self.project_root / "data" / "logs_python",
            LogType.CPP: self.project_root / "data" / "logs_cpp",
        }

    def get_logs(self, log_type: LogType) -> list[Path]:
        directory = self.logs[log_type]
        if not directory.exists():
            return []
        files = [
            path
            for path in directory.iterdir()
            if path.is_file() and self.LOG_PATTERN.match(path.name)
        ]
        return sorted(files, key=lambda path: path.name, reverse=True)

    def get_latest_log(self, log_type: LogType) -> Path | None:
        logs = self.get_logs(log_type)
        if not logs:
            return None
        return logs[0]

    def get_last_logs(self, log_type: LogType, count: int) -> list[Path]:
        return self.get_logs(log_type)[:count]

    def get_today_logs(self, log_type: LogType) -> list[Path]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [path for path in self.get_logs(log_type) if path.name.startswith(today)]

    def create_archive(self, log_type: LogType, logs: list[Path]) -> Path:
        archive_directory = self.project_root / "data" / "admin_logs"
        archive_directory.mkdir(parents=True, exist_ok=True)
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_path = archive_directory / f"{log_type.value}_logs_{date}.zip"

        with zipfile.ZipFile(
            archive_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for log in logs:
                archive.write(log, arcname=log.name)

        return archive_path
