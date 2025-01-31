from __future__ import annotations

import asyncio
from collections.abc import Iterator
from queue import Empty, Queue

import humanize
import ollama
from httpx import ConnectError
from ollama import ProgressResponse
from rich.columns import Columns
from rich.console import ConsoleRenderable, RenderableType, RichCast
from rich.progress_bar import ProgressBar
from rich.style import Style
from rich.text import Text
from textual import on, work
from textual.app import App
from textual.binding import Binding
from textual.color import Color
from textual.message import Message
from textual.message_pump import MessagePump
from textual.notifications import SeverityLevel
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Input, Select, TextArea
from torchgen.executorch.api.et_cpp import return_type

from donor_db_builder import __application_title__
from donor_db_builder.cli.screens.main import MainScreen
from donor_db_builder.cli.theme_manager import theme_manager
from donor_db_builder.settings import settings
from donor_db_builder.cli.dialogs.information import InformationDialog
from donor_db_builder.cli.dialogs.help import HelpDialog
from donor_db_builder.cli.messages.messages import StatusMessage, ChangeTab, LogIt

from textual import Logger, log, LogGroup, LogVerbosity

logg = Logger(log, group=LogGroup.DEBUG, verbosity=LogVerbosity.HIGH)


class RaisingApp(App[None]):
    debug: bool = True
    TITLE = __application_title__
    COMMAND_PALETTE_BINDING = "ctrl+underscore"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding(key="f1", action="help", description="Help", show=True, priority=True),
        Binding(key="ctrl+q", action="app.shutdown", description="Quit", show=True),
        Binding(
            key="f10",
            action="change_theme",
            description="Change Theme",
            show=True,
            priority=True,
        ),
        Binding(key="ctrl+c", action="noop", show=False),
    ]

    commands: list[dict[str, str]] = [
        {
            "action": "action_quit",
            "cmd": "Quit Application",
            "help": "Quit the application as soon as possible",
        }
    ]

    CSS_PATH = "raising.tcss"

    main_screen: MainScreen
    last_status: RenderableType = ""
    ps_timer: Timer | None

    def __init__(self) -> None:
        super().__init__()
        theme_manager.set_app(self)

        self.ps_timer = None

        self.title = __application_title__

        if settings.theme_name not in theme_manager.list_themes():
            settings.theme_name = f"{settings.theme_name}_{settings.theme_mode}"
            if settings.theme_name not in theme_manager.list_themes():
                settings.theme_name = "raise_dark"

        theme_manager.change_theme(settings.theme_name)

    async def on_mount(self) -> None:
        self.main_screen = MainScreen()

        await self.push_screen(self.main_screen)

        if settings.show_first_run:
            settings.show_first_run = False
            settings.save()
            self.set_timer(1, self.show_first_run)

    async def show_first_run(self) -> None:
        await self.app.push_screen(
            InformationDialog(
                title="Hello",
                message="This should render fine",
            )
        )

    def action_noop(self) -> None:
        """"""

    def action_help(self) -> None:
        self.app.push_screen(HelpDialog())

    def action_clear_field(self) -> None:
        focused: Widget | None = self.screen.focused

        if not focused:
            return
        if isinstance(focused, Input):
            focused.value = ""
        if isinstance(focused, TextArea):
            focused.text = ""
        if isinstance(focused, Select):
            focused.value = Select.BLANK

    def status_notify(
        self, message: str, severity: SeverityLevel = "information"
    ) -> None:
        self.notify(
            message, severity=severity, timeout=5 if severity != "information" else 3
        )
        self.main_screen.post_message(StatusMessage(message))

    @on(ChangeTab)
    def on_change_tab(self, event: ChangeTab) -> None:
        event.stop()
        self.main_screen.change_tab(event.tab)

    @on(LogIt)
    def on_log_it(self, event: LogIt) -> None:
        """Log an event to the log view"""
        event.stop()
        self.log_it(event.msg)
        if event.notify and isinstance(event.msg, str):
            self.notify(
                event.msg,
                severity=event.severity,
                timeout=event.timeout or 5,
            )

    def log_it(self, msg: ConsoleRenderable | RichCast | str | object) -> None:
        """Log a message to the log view"""
        self.main_screen.log_view.richlog.write(msg)

    async def action_shutdown(self) -> None:
        settings.shutting_down = True
        await self.action_quit()

    # @work
    # async def action_change_theme(self) -> None:
    #     """An action to change the theme."""
    #     theme = await self.push_screen_wait(ThemeDialog())
    #     settings.theme_name = theme
