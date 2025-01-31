from __future__ import annotations

from rich.text import TextType
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.widgets._button import ButtonVariant


class TextDialog(ModalScreen[None]):
    DEFAULT_CSS = """
    	TextDialog {
    		align: center middle;
    	}

    	TextDialog Center {
    		width: 100%;
    	}

    	TextDialog > Vertical {
    		background: $boost;
    		min-width: 30%;
    		width: auto;
    		height: auto;
    		border: round $primary;
    	}

    	TextDialog Static {
    		width: auto;
    	}

    	TextDialog .spaced {
    		padding: 1 4;
    	}

    	TextDialog #message {
    		min-width: 100%;
    	}
    	"""

    BINDINGS = [Binding("escape", "dismiss(None)", "", show=False)]

    def __init__(self, title: TextType, message: TextType) -> None:
        super().__init__()
        self._title = title
        self._message = message

    @property
    def button_style(self) -> ButtonVariant:
        return "primary"

    def compose(self) -> ComposeResult:
        with Vertical():
            with Center():
                yield Static(self._title, classes="spaced")
            yield Static(self._message, classes="spaced")
            with Center(classes="spaced"):
                yield Button("Ok", variant=self.button_style)

    def on_mount(self) -> None:
        self.query_one(Button).focus()

    def on_button_pressed(self) -> None:
        self.dismiss(None)
