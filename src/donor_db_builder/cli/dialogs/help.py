import os
from pathlib import Path
from typing import Final

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

from donor_db_builder import __application_title__, __version__

HELP: Final[str] = f"""
# {__application_title__} v{__version__} Help

Welcome to {__application_title__} Help!

"""


class HelpDialog(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpDialog {
        align: center middle;
    }

    HelpDialog > Vertical {
        border: thick $primary 50%;
        width: 80%;
        height: 80%;
        background: $boost;
    }

    HelpDialog > Vertical > VerticalScroll {
        height: 1fr;
    }

    HelpDialog > Vertical > Center {
        padding: 1;
        height: auto;
    }
    """

    BINDINGS = [Binding("escape,f1", "dismiss(None)", "", show=False)]

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        # with open(f"{os.path.dirname(Path(__file__).parent)}/help.md", encoding="utf-8") as f:
        #     help_text = f.read()
        help_text = "..."
        with Vertical():
            with VerticalScroll():
                yield Markdown(HELP + help_text)
            with Center():
                yield Button("Close", variant="primary")

    def on_mount(self) -> None:
        """Configure the help screen once the DOM is ready."""
        # It seems that some things inside Markdown can still grab focus;
        # which might not be right. Let's ensure that can't happen here.
        self.query_one(Markdown).can_focus_children = False
        self.query_one("Vertical > VerticalScroll").focus()

    def on_button_pressed(self) -> None:
        """React to button press."""
        self.dismiss(None)

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        """A link was clicked in the help."""
        self.app.open_url(event.href)
