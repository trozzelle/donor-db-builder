from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Label, Tree, Select
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widget import Widget
from config import Settings, Config

# class LabeledInput(Static):
#
#     def __init__(self, label: str, placeholder: str, element_id: str):
#         self.label = label
#         self.placeholder = placeholder
#         self.id = element_id
#         super().__init__(id)
#
#     def compose(self) -> ComposeResult:
#         yield Label(self.label, id=f"{self.id}-cf-label")
#         yield Input(placeholder=self.placeholder, id=f"{self.id}-cf-input")


class LabeledInput(Widget):
    def __init__(self, label: str, placeholder: str, value: str = None):
        self.label = label
        self.placeholder = placeholder
        self.value = value
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.label)
        yield Input(placeholder=self.placeholder)


class ConfigScreenBody(Static):
    def compose(self) -> ComposeResult:
        yield LabeledInput("DB Host", placeholder="127.0.0.1")
        yield LabeledInput("DB Pass", placeholder="****")

        # yield Container(LabeledInput("DB Pass", placeholder="****"))


class ConfigScreenMain(Static):
    def compose(self) -> ComposeResult:
        yield Container(ConfigScreenBody())


class ConfigScreen(App):
    CSS_PATH = "ConfigScreen.tcss"

    def __init__(self):
        self.config = Settings()
        super().__init__()

    # def on_mount(self) -> None:
    # footer = self.query_one("#modal_footer", Static)
    # footer.display = False
    # if self.error_message:
    #     footer.update(self.error_message.output())
    #     footer.display = True

    # self.query_one("#host", Input).border_title = "Host"

    def on_mount(self) -> None:
        self.query_one("#host", Input).border_title = "Host"
        self.query_one("#user", Input).border_title = "User"
        self.query_one("#password", Input).border_title = "Password"

    def compose(self) -> ComposeResult:
        # yield Header()
        settings, labels = self.config.get_all_with_labels()
        # for field_name, value in settings.items():
        #     yield ScrollableContainer(
        #         LabeledInput(
        #             label=labels[field_name]["label"],
        #             placeholder=labels[field_name]["placeholder"],
        #             value=str(value) if not None else "",
        #         )
        #     )
        # yield Footer()

        yield Header()
        with Vertical():
            with Vertical(classes="main_container"):
                yield Label("Connect to a Host")

                yield Input(value="localhost", id="host", placeholder="Host:Port")
                yield Input(value="", id="user", placeholder="Username")
                yield Input(
                    value="", id="password", placeholder="Password", password=True
                )
                # yield Select(
                #     options=[],
                #     id="credential_profile",
                #     value="",
                #     prompt="Select a credential profile (optional)",
                # )

                # yield AutoComplete(
                #     Input(value=self.host, id="host", placeholder="Host:Port"),
                #     Dropdown(id="dropdown_items", items=self.options_available_hosts),
                # )
        yield Footer()


if __name__ == "__main__":
    app = ConfigScreen()
    app.run()
