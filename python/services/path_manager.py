from pathlib import Path


class PathManager:
    def __init__(self):
        self.project_dir = Path(__file__).resolve().parents[2]

        self.data_dir = self.project_dir / "data"
        self.python_dir = self.project_dir / "python"

        self.logs_cpp = self.data_dir / "logs_cpp"
        self.logs_python = self.data_dir / "logs_python"
        self.admin_logs = self.data_dir / "admin_logs"

        self.config_path = self.data_dir / "config.json"
        self.queries_path = self.data_dir / "queries.json"
        self.filters_path = self.data_dir / "filters.json"
        self.database_path = self.data_dir / "bot.db"

    def create_directories(self):
        self.data_dir.mkdir(exist_ok=True)
