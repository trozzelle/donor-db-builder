import orjson as json
import requests
from typing import Dict
from pathlib import Path
from pydantic import BaseModel
from donor_db_builder.utils.args import get_args
from argparse import Namespace
from donor_db_builder.raising_types import TabType, valid_tabs, DBModes, valid_db_modes
import os
from textual import log


# class ProjectPaths:
#     def __init__(self):
#         # Project root is up 3 levels from config.py
#         self.PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
#
#         # Explicitly define resource directories
#         self.paths: Dict[str, Path] = {
#             "docker": self.PROJECT_ROOT / "docker",
#             "models": self.PROJECT_ROOT / "models",
#             "data": self.PROJECT_ROOT / "data",
#             "theme": self.PROJECT_ROOT / "themes",
#         }
#
#     def get_path(self, name: str) -> Path:
#         """Get a project path by name"""
#         if name not in self.paths:
#             raise ValueError(f"Unknown path name: {name}")
#         return self.paths[name]


class ProjectPaths(BaseModel):
    PROJECT_ROOT: Path
    paths: Dict[str, Path]

    def __init__(self):
        # Project root is up 3 levels from config.py
        project_root = Path(__file__).parent.parent.parent

        # Initialize with default values
        super().__init__(
            PROJECT_ROOT=project_root,
            paths={
                "root": project_root,
                "docker": project_root / "docker",
                "models": project_root / "models",
                "data": project_root / "data",
                "theme": project_root / "themes",
                "absolute": project_root.absolute(),
            },
        )

    def get_path(self, name: str) -> Path:
        """Get a project path by name"""
        if name not in self.paths:
            raise ValueError(f"Unknown path name: {name}")
        return self.paths[name]


def get_project_path(name: str) -> Path:
    """Get a project path by name"""
    paths = ProjectPaths()
    return paths.get_path(name)


class Settings(BaseModel):
    _shutting_down: bool = False
    show_first_run: bool = False

    no_save: bool = False
    no_save_chat: bool = False
    project_paths: ProjectPaths = ProjectPaths()
    data_dir: Path = project_paths.get_path("data")
    settings_dir: Path = project_paths.PROJECT_ROOT / ".raising"
    settings_file: Path = "settings.json"
    cache_dir: Path = ""
    secret_key: str = ""
    secrets_file: Path = ""

    app_db: Path = data_dir / "app.db"
    app_db_mode: DBModes = "Persist"

    default_theme_dir: Path = Path(os.path.dirname(Path(__file__))) / "cli" / "themes"
    theme_dir: Path = project_paths.get_path("theme")
    theme_name: str = "raise"
    theme_mode: str = "dark"

    starting_tab: TabType = "Options"
    last_tab: TabType = "Options"
    use_last_tab_on_startup: bool = True

    max_log_lines: int = 1000

    def __init__(self) -> None:
        super().__init__()

        args: Namespace = get_args()

        if args.no_save:
            self.no_save = True

        if args.no_chat_save:
            self.no_save_chat = True

        self.data_dir = args.data_dir or self.project_paths.get_path("data")

        self.secrets_file = self.data_dir / "secrets.json"

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.settings_dir, exist_ok=True)

        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory does not exist: {self.data_dir}")

        self.settings_file = self.settings_dir / "settings.json"

        if os.environ.get("RAISING_THEME_NAME"):
            self.theme_name = os.environ.get("RAISING_THEME_NAME", self.theme_name)

        if os.environ.get("RAISING_THEME_MODE"):
            self.theme_mode = os.environ.get("RAISING_THEME_MODE", self.theme_mode)

        if args.theme_name:
            self.theme_name = args.theme_name
        if args.theme_mode:
            self.theme_mode = args.theme_mode

    def load_from_file(self) -> None:
        try:
            settings_file = self.settings_file

            data = json.loads(settings_file.read_bytes())

            self.theme_name = data.get("theme_name", self.theme_name)
            self.theme_mode = data.get("theme_mode", self.theme_mode)

            self.max_log_lines = max(0, data.get("max_log_lines", 1000))

            self.app_db_mode = data.get("app_db_mode", "Persist")

            self.show_first_run = data.get("show_first_run", self.show_first_run)
        except FileNotFoundError:
            pass

    def update_env(self) -> None:
        """Set environment variables from settings"""
        pass

    def save_settings_to_file(self) -> None:
        self.update_env()

        if self.no_save or self._shutting_down:
            return

        os.makedirs(self.settings_dir, exist_ok=True)
        if not os.path.exists(self.settings_dir):
            raise FileNotFoundError(
                f"Settings directory does not exist: {self.settings_dir}"
            )

        with open(self.settings_file, "w", encoding="utf-8") as settings_file:
            log.warning(self.model_dump_json(indent=4))
            settings_file.write(self.model_dump_json(indent=4))

    def save(self) -> None:
        self.save_settings_to_file()

    @property
    def initial_tab(self) -> TabType:
        if settings.show_first_run:
            return "Options"
        if settings.use_last_tab_on_startup:
            return settings.last_tab
        return settings.starting_tab

    @property
    def shutting_down(self) -> bool:
        return self._shutting_down

    @shutting_down.setter
    def shutting_down(self, value: bool) -> None:
        self._shutting_down = value


settings = Settings()
