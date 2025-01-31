from __future__ import annotations

from typing import cast

from rich.console import RenderableType
from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
from donor_db_builder.settings import settings, TabType
from donor_db_builder.cli.views import IngestView, LogView, OptionsView


class MainScreen(Screen[None]):
    CSS_PATH = "main.tcss"

    status_bar: Static
    ps_status_bar: Static
    tabbed_content: TabbedContent

    options_view: OptionsView
    log_view: LogView

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.status_bar = Static("", id="status-bar")
        self.ps_status_bar = Static("", id="ps-status-bar")
        self.ps_status_bar.display = False

        self.ingest_view = IngestView()
        self.options_view = OptionsView(id="options")
        self.log_view = LogView()

    async def on_mount(self) -> None:
        self.set_timer(0.5, self.done_loading)

    def done_loading(self) -> None:
        self.tabbed_content.loading = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield self.status_bar
        yield self.ps_status_bar

        with TabbedContent(id="tabbed_content", initial=settings.initial_tab) as tabs:
            self.tabbed_content = tabs
            tabs.loading = True

            with TabPane("Ingest", id="Ingest"):
                yield self.ingest_view
            with TabPane("Options", id="Options"):
                yield self.options_view
            with TabPane("Logs", id="Logs"):
                yield self.log_view

    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, message: TabbedContent.TabActivated) -> None:
        message.stop()

        settings.last_tab = cast(TabType, message.tab.label.plain)
        settings.save()

        self.log_view.richlog.write(f"Tab activated: {message.tab.label.plain}")

    def change_tab(self, tab: TabType) -> None:
        self.tabbed_content.active = tab
