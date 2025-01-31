from dataclasses import dataclass
from typing import Any
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.events import Blur, Paste
from textual.message import Message
from textual.widgets import Input, Button, Label
from textual.theme import Theme
from textual_autocomplete import DropdownItem
from textual_autocomplete._autocomplete2 import TargetState
from .input import RaisingInput


class PromptInput(RaisingInput):
    BINDING_GROUP_TITLE = "URL Input"

    BINDINGS = [
        Binding("down", "app.focus_next", "Focus next", show=False),
    ]

    @dataclass
    class CursorMoved(Message):
        cursor_position: int
        value: str
        input: "PromptInput"

        @property
        def control(self) -> "PromptInput":
            return self.input

    @dataclass
    class Blurred(Message):
        input: "PromptInput"

        @property
        def control(self) -> "PromptInput":
            return self.input


class PromptBar(Vertical):
    COMPONENT_CLASSES = {
        "started-marker",
        "complete-marker",
        "failed-marker",
        "not-started-marker",
    }

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield PromptInput(placeholder="Enter command", id="url-input")

    @property
    def url_input(self) -> PromptInput:
        """Get the URL input."""
        return self.query_one("#url-input", PromptInput)
