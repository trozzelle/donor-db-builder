from dataclasses import dataclass
from sqlalchemy.event import Events
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Blur
from textual.message import Message
from textual.widgets import Input, Label
from textual.theme import Theme

from scratch.widgets.input import RaisingInput


class PromptInput(RaisingInput):
    #     help = HelpData(
    #         "Address Bar",
    #         """\
    # Enter the URL to send a request to. Refer to variables from the environment (loaded via `--env`) using `$variable` or `${variable}` syntax.
    # Resolved variables will be highlighted green. Move the cursor over a variable to preview the value.
    # Base URL suggestions are loaded based on the URLs found in the currently open collection.
    # Press `ctrl+l` to quickly focus this bar from elsewhere.
    #
    # You can also import a `curl` command by pasting it into the URL bar.
    # This will fill out the request details in the UI based on the curl command you pasted, overwriting any existing values.
    # It's recommended you create a new request before pasting a curl command, to avoid overwriting.
    # """,
    #     )

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

    def on_mount(self):
        # self.highlighter = VariablesAndUrlHighlighter(self)
        self.app.theme_changed_signal.subscribe(self, self.on_theme_change)

    @on(Input.Changed)
    def on_change(self, event: Input.Changed) -> None:
        self.remove_class("error")

    def on_blur(self, _: Blur) -> None:
        self.post_message(self.Blurred(self))

    def watch_cursor_position(self, cursor_position: int) -> None:
        self.post_message(self.CursorMoved(cursor_position, self.value, self))

    def on_theme_change(self, theme: Theme) -> None:
        super().on_theme_change(theme)
        # theme_variables = self.app.theme_variables
        # self.highlighter.variable_styles = VariableStyles(
        #     resolved=theme_variables.get("variable-resolved")
        #     or theme_variables.get("text-success"),
        #     unresolved=theme_variables.get("variable-unresolved")
        #     or theme_variables.get("text-error"),
        # )
        #
        # self.highlighter.url_styles = UrlStyles(
        #     base=theme_variables.get("url-base")
        #     or theme_variables.get("text-secondary"),
        #     protocol=theme_variables.get("url-protocol")
        #     or theme_variables.get("text-accent"),
        #     separator=theme_variables.get("url-separator")
        #     or theme_variables.get("foreground-muted"),
        # )


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
        self.cached_base_urls: list[str] = []
        self._trace_events: set[Events] = set()

    def on_env_changed(self, _: None) -> None:
        # self._display_variable_at_cursor()
        self.url_input.refresh()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield PromptInput(placeholder="Enter a command", id="url-input")
            yield Label(id="trace-markers")

    def on_mount(self) -> None:
        self.app.theme_changed_signal.subscribe(self, self.on_theme_change)
        # self.app.env_changed_signal.subscribe(self, self.on_env_changed)

    @on(Input.Changed)
    def on_change(self, event: Input.Changed) -> None:
        # try:
        #     self.variable_value_bar.update("")
        # except NoMatches:
        #     return
        pass

    @on(PromptInput.Blurred)
    def on_blur(self, event: PromptInput.Blurred) -> None:
        # try:
        #     self.variable_value_bar.update("")
        # except NoMatches:
        #     return
        pass

    @on(PromptInput.CursorMoved)
    def on_cursor_moved(self, event: PromptInput.CursorMoved) -> None:
        # self._display_variable_at_cursor()
        pass

    # def _display_variable_at_cursor(self) -> None:
    #     url_input = self.url_input
    #
    #     cursor_position = url_input.cursor_position
    #     value = url_input.value
    #     variable_at_cursor = get_variable_at_cursor(cursor_position, value)
    #
    #     variables = get_variables()
    #     try:
    #         variable_bar = self.variable_value_bar
    #     except NoMatches:
    #         # Can be hidden with config, which will set display = None.
    #         # In this case, the query will fail.
    #         return
    #
    #     if not variable_at_cursor:
    #         variable_bar.update("")
    #         return
    #
    #     variable_name = extract_variable_name(variable_at_cursor)
    #     variable_value = variables.get(variable_name)
    #     if variable_value:
    #         content = f"{variable_name} = {variable_value}"
    #         variable_bar.update(content)
    #     else:
    #         variable_bar.update("")

    def on_theme_change(self, theme: Theme) -> None:
        # markers = self._build_markers()
        # self.trace_markers.update(markers)
        self.url_input.notify_style_update()
        self.url_input.refresh()

    @property
    def url_input(self) -> PromptInput:
        """Get the URL input."""
        return self.query_one("#url-input", PromptInput)
