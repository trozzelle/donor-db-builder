from pathlib import Path
from typing import Literal

from rich.console import RenderableType

from textual import messages
from textual.reactive import Reactive, reactive
from textual.app import App, ComposeResult, ReturnType
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Label,
)
from scratch.widgets.prompt import PromptBar, PromptInput

PostingLayout = Literal["horizontal", "vertical"]


class AppHeader(Horizontal):
    def compose(self):
        yield Label("Some test string, could be the user host", id="app-user-host")


class AppBody(Vertical):
    DEFAULT_CSS = """\
    AppBody {
        padding: 0 2;
    }
    """


class MainScreen(Screen[None]):
    AUTO_FOCUS = None
    BINDING_GROUP_TITLE = "Main Screen"
    BINDINGS = [
        Binding(
            "ctrl+j,alt+enter",
            "send_request",
            "Send",
            tooltip="Send the current request.",
            id="send-request",
        ),
        Binding(
            "ctrl+t",
            "change_method",
            "Method",
            tooltip="Focus the method selector.",
            id="focus-method",
        ),
        Binding(
            "ctrl+l",
            "app.focus('url-input')",
            "Focus URL input",
            show=False,
            tooltip="Focus the URL input.",
            id="focus-url",
        ),
        Binding(
            "ctrl+s",
            "save_request",
            "Save",
            tooltip="Save the current request. If a request is open, this will overwrite it.",
            id="save-request",
        ),
        Binding(
            "ctrl+n",
            "new_request",
            "New",
            tooltip="Create a new request.",
            id="new-request",
        ),
        Binding(
            "ctrl+m",
            "toggle_expanded",
            "Expand section",
            show=False,
            tooltip="Expand or shrink the section (request or response) which has focus.",
            id="expand-section",
        ),
        Binding(
            "ctrl+h",
            "toggle_collection_browser",
            "Toggle collection browser",
            show=False,
            tooltip="Toggle the collection browser.",
            id="toggle-collection",
        ),
    ]

    current_layout: Reactive[PostingLayout] = reactive("vertical", init=False)

    def __init__(
        self,
    ):
        super().__init__()
        self._initial_layout: PostingLayout = "vertical"

    def on_mount(self) -> None:
        self.current_layout = self._initial_layout

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield PromptBar()
        # yield AppBody()
        yield Footer()

    @property
    def prompt_bar(self) -> PromptBar:
        return self.query_one(PromptBar)

    @property
    def prompt_input(self) -> PromptInput:
        return self.query_one(PromptInput)

    @property
    def app_body(self) -> AppBody:
        return self.query_one(AppBody)


class Raising(App[None], inherit_bindings=False):
    AUTO_FOCUS = None
    CSS_PATH = Path(__file__).parent / "raising.tcss"
    BINDING_GROUP_TITLE = "Global Keybinds"
    BINDINGS = [
        Binding(
            "ctrl+p",
            "command_palette",
            description="Commands",
            tooltip="Open the command palette to search and run commands.",
            id="commands",
        ),
        Binding(
            "ctrl+o",
            "toggle_jump_mode",
            description="Jump",
            tooltip="Activate jump mode to quickly move focus between widgets.",
            id="jump",
        ),
        Binding(
            "ctrl+c",
            "app.quit",
            description="Quit",
            tooltip="Quit the application.",
            priority=True,
            id="quit",
        ),
        Binding(
            "f1,ctrl+question_mark",
            "help",
            "Help",
            tooltip="Open the help dialog for the currently focused widget.",
            id="help",
        ),
        Binding("f8", "save_screenshot", "Save screenshot.", show=False),
    ]

    def __init__(self):
        super().__init__()

        def get_default_screen(self) -> MainScreen:
            self.main_screen = MainScreen()
            return self.main_screen

    def exit(
        self,
        result: ReturnType | None = None,
        return_code: int = 0,
        message: RenderableType | None = None,
    ) -> None:
        self._exit = True
        self._return_value = result
        self._return_code = return_code
        self.post_message(messages.ExitApp())
        if message:
            self._exit_renderables.append(message)
            self._exit_renderables = list(set(self._exit_renderables))


if __name__ == "__main__":
    app = Raising()
    app.run()
