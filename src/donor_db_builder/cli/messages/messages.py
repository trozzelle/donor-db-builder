from dataclasses import dataclass

from rich.console import ConsoleRenderable, RenderableType, RichCast
from textual.message import Message
from textual.message_pump import MessagePump
from textual.notifications import SeverityLevel
from textual.widgets import Input, TextArea

from donor_db_builder.raising_types import TabType


@dataclass
class StatusMessage(Message):
    """Message to update status bar."""

    msg: RenderableType
    log_it: bool = True


@dataclass
class ChangeTab(Message):
    """Change to requested tab."""

    tab: TabType


@dataclass
class LogIt(Message):
    """Log message."""

    msg: ConsoleRenderable | RichCast | str | object
    notify: bool = False
    severity: SeverityLevel = "information"
    timeout: int = 5
