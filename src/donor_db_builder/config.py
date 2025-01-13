import os
import json
from linecache import cache
from pathlib import Path
from typing import Literal, Dict
from pydantic_settings import BaseSettings
from functools import cache

CONFIG_DIR = os.getcwd() + "/.config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        return {}


def save_config(config):
    """Save configuration to file"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        click.echo(f"Error saving config: {e}", err=True)


def get_setting(key, default=None):
    """Get a setting from config"""
    config = load_config()
    return config.get(key, default)


def set_setting(key, value):
    """Set a setting in config"""
    config = load_config()
    config[key] = value
    save_config(config)


# Below is new code and the above needs to be refactored in


class Settings(BaseSettings):
    """Environment-specific settings"""

    ENV: Literal["development", "testing", "production"] = "development"
    DB_NAME: str = "app.db"


@cache
def get_settings():
    return Settings()


class ProjectPaths:
    def __init__(self):
        # Project root is up 3 levels from config.py
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent

        # Explicitly define resource directories
        self.paths: Dict[str, Path] = {
            "docker": self.PROJECT_ROOT / "docker",
            "models": self.PROJECT_ROOT / "models",
            "data": self.PROJECT_ROOT / "data",
        }

    def get_path(self, name: str) -> Path:
        """Get a project path by name"""
        if name not in self.paths:
            raise ValueError(f"Unknown path name: {name}")
        return self.paths[name]


@cache
def get_project_paths() -> ProjectPaths:
    return ProjectPaths()
