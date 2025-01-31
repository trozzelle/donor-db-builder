from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Literal, TypeAlias

import orjson as json
from textual.app import App
from textual.theme import Theme

from donor_db_builder.raising_types import ThemeMode, ThemeModes, Themes
from donor_db_builder.settings import settings


class InvalidThemeError(Exception):
    def __init__(self, theme_name: str) -> None:
        self.theme_name = theme_name
        super().__init__(f"Invalid theme name '{theme_name}'")


class ThemeModeError(Exception):
    def __init__(self, theme_name: str) -> None:
        super().__init__(
            f"Invalid theme mode. '{theme_name}' does not have either 'dark' or 'light' mode"
        )


class ThemeManager:
    app: App[Any] | None
    theme_folder: Path

    def __init__(self) -> None:
        self.theme_folder = settings.theme_dir

    def set_app(self, app: App[Any] | None) -> None:
        self.app = app
        self.load_themes()

    def ensure_default_theme(self) -> None:
        default_theme_file: Path = settings.default_theme_dir / "raise.json"

        if not self.theme_folder.exists():
            self.theme_folder.mkdir(parents=True)
        theme_file: Path = self.theme_folder / "raise.json"

        if not theme_file.exists():
            shutil.copy(default_theme_file, theme_file)

    def load_theme(self, theme_name: str) -> None:
        if not self.app:
            raise Exception("App is not initialized")

        theme_name = os.path.basename(theme_name)
        theme_file: Path = self.theme_folder / (theme_name + ".json")
        theme_definition = json.loads(theme_file.read_bytes())

        if "dark" not in theme_definition and "light" not in theme_definition:
            raise ThemeModeError(theme_name)

        for mode in ThemeModes:
            if mode in theme_definition:
                self.app.register_theme(
                    Theme(
                        name=f"{theme_name}_{mode}",
                        **theme_definition[mode],
                    )
                )

    def load_themes(self) -> None:
        self.ensure_default_theme()

        for file in os.listdir(self.theme_folder):
            if file.lower().endswith(".json"):
                self.load_theme(f"{self.theme_folder}/{os.path.splitext(file)[0]}")

    def get_theme(self, theme_name: str) -> Theme:
        """Get theme by name"""
        if not self.app:
            raise Exception("App is not initialized")
        return self.app.available_themes[theme_name]

    def list_themes(self) -> list[str]:
        """Get list of themes"""
        if not self.app:
            raise Exception("App is not initialized")

        return list(self.app.available_themes.keys())

    def theme_select_options(self) -> list[tuple[str, str]]:
        return [(theme, theme) for theme in self.list_themes()]

    def change_theme(self, theme_name: str) -> None:
        if not self.app:
            raise Exception("App is not initialized")
        self.app.theme = theme_name


theme_manager = ThemeManager()
