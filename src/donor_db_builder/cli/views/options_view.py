from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Show
from textual.validation import Integer
from textual.widgets import Button, Checkbox, Input, Label, Select, Static
from donor_db_builder.settings import settings, valid_tabs, valid_db_modes
from textual import log


class OptionsView(Horizontal):
    DEFAULT_CSS = """
        OptionsView {
            width: 1fr;
            height: 1fr;
            overflow: auto;

            Horizontal {
                height: auto;
                Label {
                    padding-top: 1;
                    height: 3;
                }
            }

            .column {
                width: 1fr;
                height: auto;
            }

            .folder-item {
                height: 1;
                width: 1fr;
                Label, Static {
                    height: 1;
                    padding: 0;
                    margin: 0;
                    width: 2fr;
                }
                Label {
                    width: 1fr;
                }
            }
            .section {
                background: $panel;
                height: auto;
                width: 1fr;
                border: solid $primary;
                border-title-color: $primary;
            }
        }
        """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._provider_changed = False

    def compose(self) -> ComposeResult:
        with self.prevent(
            Input.Changed, Input.Submitted, Select.Changed, Checkbox.Changed
        ):
            with Vertical(classes="column"):
                with Vertical(classes="section") as about:
                    about.border_title = "About"
                    yield Static(f"Raising app")

                with Vertical(classes="section") as app_folders:
                    app_folders.border_title = "App Directories"
                    with Horizontal(classes="folder-item"):
                        yield Label("Data Dir")
                        yield Static(str(settings.data_dir))
                    with Horizontal(classes="folder-item"):
                        yield Label("Cache Dir")
                        yield Static(str(settings.cache_dir))
                    with Horizontal(classes="folder-item"):
                        yield Label("Settings Dir")
                        yield Static(str(settings.settings_dir))

                with Vertical(classes="section") as startup:
                    startup.border_title = "Startup"
                    yield Checkbox(
                        label="Show first run",
                        value=settings.show_first_run,
                        id="show_first_run",
                    )

                    with Horizontal():
                        yield Checkbox(
                            label="Start on last tab used",
                            value=settings.use_last_tab_on_startup,
                            id="use_last_tab_on_startup",
                        )
                        yield Label("Startup Tab")
                        yield Select[str](
                            value=settings.starting_tab,
                            options=[(vs, vs) for vs in valid_tabs],
                            id="starting_tab",
                        )

                with Vertical(classes="section") as database:
                    database.border_title = "Database"

                    yield Label("DB Mode")
                    yield Select[str](
                        value=settings.app_db_mode,
                        options=[(vs, vs) for vs in valid_db_modes],
                        id="db_mode",
                    )
            with Vertical(classes="column"):
                with Vertical(classes="section") as models:
                    models.border_title = "Models"
                with Vertical(classes="section") as modes:
                    modes.border_title = "Modes"
                with Vertical(classes="section") as misc:
                    misc.border_title = "Misc"

    def _on_show(self, event: Show) -> None:
        self.screen.sub_title = "Options"
        self.refresh(recompose=True)

    @on(Select.Changed)
    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()

        control: Select = event.control

        if control.id == "starting_tab":
            if control.value == Select.BLANK:
                settings.starting_tab = "Options"
            else:
                settings.starting_tab = control.value
        elif control.id == "db_mode":
            log.warning(f"Setting before: {settings.app_db_mode}")
            settings.app_db_mode = control.value
            log.warning(f"Setting after: {settings.app_db_mode}")
        else:
            self.notify(f"Unhandled input: {control.id}", severity="error", timeout=8)
            return
        settings.save()

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        event.stop()
        control: Checkbox = event.control

        if control.id == "use_last_tab_on_startup":
            settings.use_last_tab_on_startup = control.value
        else:
            self.notify(f"Unhandled input: {control.id}", severity="error", timeout=8)
            return
        settings.save()
