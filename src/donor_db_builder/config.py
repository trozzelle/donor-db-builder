import os
import json
from linecache import cache
from pathlib import Path
from typing import Literal, Dict, Any, Optional
from pydantic_settings import BaseSettings
from functools import cache
from rich.console import Console
from rich.table import Table
from loguru import logger

path = Path.cwd()
CONFIG_DIR = Path(__file__).parent.parent.parent / "/.config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class ProjectPaths:
    def __init__(self):
        # Project root is up 3 levels from config.py
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent

        # Explicitly define resource directories
        self.paths: Dict[str, Path] = {
            "docker": self.PROJECT_ROOT / "docker",
            "models": self.PROJECT_ROOT / "models",
            "data": self.PROJECT_ROOT / "data",
            "themes": self.PROJECT_ROOT / "themes",
        }

    def get_path(self, name: str) -> Path:
        """Get a project path by name"""
        if name not in self.paths:
            raise ValueError(f"Unknown path name: {name}")
        return self.paths[name]


@cache
def get_project_paths() -> ProjectPaths:
    return ProjectPaths()


# class ContextSettings:
#     """Settings class for a context"""
#
#     def __init__(self, context_name: str, parent=None):
#         self.context_name = context_name
#         self.parent = parent
#         self.settings: Dict[str, Any] = {}
#         self.subcontexts: Dict[str, "ContextSettings"] = {}
#
#     def set_setting(self, key: str, value: Any):
#         self.settings[key] = value
#
#     def get_setting(self, key: str) -> Optional[Any]:
#         if key in self.settings:
#             return self.settings[key]
#         elif self.parent is not None:
#             return self.parent.get_setting(key)
#         else:
#             return None
#
#     def add_subcontext(self, name: str) -> "ContextSettings":
#         context = ContextSettings(name, parent=self)
#         self.subcontexts[name] = context
#         return context
#
#     def get_full_context_path(self) -> str:
#         if self.parent is not None:
#             parent_path = self.parent.get_full_context_path()
#             return f"{parent_path}/{self.context_name}"
#         return self.context_name
#
#
# class SettingsManager:
#     def __init__(self, config_dir: Optional[Path] = None):
#         self.paths = ProjectPaths()
#         self.console = Console()
#         self.root = ContextSettings("main")
#         self.current_context = self.root
#         self.config_dir = config_dir or self.paths.get_path("data")
#
#         # Create settings directory if it doesn't already exist
#         self.config_dir.mkdir(parents=True, exist_ok=True)
#
#         self.root.add_subcontext("ingest")
#         self.root.add_subcontext("rag")
#
#         self.load_config()
#
#     def set_setting(self, key: str, value: Any) -> None:
#         self.current_context.set_setting(key, value)
#         self.save_config()
#
#     def get_setting(self, key: str) -> Optional[Any]:
#         return self.current_context.get_setting(key)
#
#     def change_context(self, context_path: str) -> bool:
#         if context_path == "..":
#             if self.current_context.parent is not None:
#                 self.current_context = self.current_context.parent
#                 return True
#             return False
#
#         parts = context_path.split("/")
#         current = self.root
#
#         for part in parts:
#             if part in current.subcontexts:
#                 current = current.subcontexts[part]
#             else:
#                 return False
#
#         self.current_context = current
#         return True
#
#     def get_prompt_path(self) -> str:
#         return self.current_context.get_full_context_path()
#
#     def show_settings(self) -> None:
#         table = Table(f"Settings for {self.current_context.context_name}")
#         table.add_column("Setting", style="cyan")
#         table.add_column("Value", style="green")
#         table.add_column("Source", style="blue")
#
#         for key, value in self.current_context.settings.items():
#             table.add_row(key, str(value), "current")
#
#         if self.current_context.parent is not None:
#             parent = self.current_context.parent
#             while parent:
#                 for key, value in parent.settings.items():
#                     if key not in self.current_context.settings:
#                         table.add_row(key, str(value), parent.context_name)
#                 parent = parent.parent
#
#         self.console.print(table)
#
#     def save_config(self) -> None:
#         config_file = self.config_dir / "config.json"
#         try:
#             with open(config_file, "w") as f:
#                 json.dump(self._serialize_context(self.root), f, indent=2)
#         except Exception as e:
#             self.console.print(f"Error saving config: {e}", style="red")
#
#     def load_config(self) -> None:
#         config_file = self.config_dir / "config.json"
#         if config_file.exists():
#             try:
#                 with open(config_file, "r") as f:
#                     config_data = json.load(f)
#                     self._deserialize_context(self.root, config_data)
#             except Exception as e:
#                 self.console.print(f"Error loading config: {e}", style="red")
#
#     def _serialize_context(self, context: ContextSettings) -> Dict:
#         return {
#             "settings": context.settings,
#             "subcontexts": {
#                 name: self._serialize_context(ctx)
#                 for name, ctx in context.subcontexts.items()
#             },
#         }
#
#     def _deserialize_context(self, context: ContextSettings, data: Dict) -> None:
#         context.settings = data.get("settings", {})
#         for name, subdata in data.get("subcontexts", {}).items():
#             if name not in context.subcontexts:
#                 context.add_subcontext(name)
#             self._deserialize_context(context.subcontexts[name], subdata)
#
#
# def load_config():
#     """Load configuration from file"""
#     if not os.path.exists(CONFIG_FILE):
#         return {}
#
#     try:
#         with open(CONFIG_FILE, "r") as f:
#             return json.load(f)
#     except Exception as e:
#         click.echo(f"Error loading config: {e}", err=True)
#         return {}
#
#
# def save_config(config):
#     """Save configuration to file"""
#     if not os.path.exists(CONFIG_DIR):
#         os.makedirs(CONFIG_DIR)
#
#     try:
#         with open(CONFIG_FILE, "w") as f:
#             json.dump(config, f, indent=2)
#     except Exception as e:
#         click.echo(f"Error saving config: {e}", err=True)
#
#
# def get_setting(key, default=None):
#     """Get a setting from config"""
#     config = load_config()
#     return config.get(key, default)
#
#
# def set_setting(key, value):
#     """Set a setting in config"""
#     config = load_config()
#     config[key] = value
#     save_config(config)
#
#
# # Below is new code and the above needs to be refactored in
#
#
# class Settings(BaseSettings):
#     """Environment-specific settings"""
#
#     ENV: Literal["development", "testing", "production"] = "development"
#     DB_NAME: str = "app.db"
#
#
# @cache
# def get_settings():
#     return Settings()
