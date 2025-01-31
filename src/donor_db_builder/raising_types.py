from typing import TypeAlias, Literal
from textual.theme import Theme

TabType: TypeAlias = Literal[
    "Ingest",
    "Options",
    "Logs",
]
valid_tabs: list[TabType] = [
    "Ingest",
    "Options",
    "Logs",
]

DBModes: TypeAlias = Literal["Memory", "Persist"]

valid_db_modes: list[DBModes] = [
    "Memory",
    "Persist",
]

ThemeMode: TypeAlias = Literal["dark", "light"]
ThemeModes: list[ThemeMode] = ["dark", "light"]
Themes: TypeAlias = dict[str, Theme]
