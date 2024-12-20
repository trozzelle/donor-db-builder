from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Label, Tree
from textual.containers import Container

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

class LabeledInput(Static):

    def __init__(self, label: str, placeholder: str, id: str):
        self.label = label
        self.placeholder = placeholder
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.label, id=f"cf-label")
        yield Input(placeholder=self.placeholder, id=f"cf-input")

class ConfigScreenBody(Static):

    def compose(self) -> ComposeResult:
        yield LabeledInput("DB Host", placeholder="127.0.0.1", id="host")
        yield LabeledInput("DB Pass", placeholder="****", id="pass")

        # yield Container(LabeledInput("DB Pass", placeholder="****"))

class ConfigScreenMain(Static):

    def compose(self) -> ComposeResult:
        yield Container(ConfigScreenBody())

class ConfigScreen(App):

    CSS_PATH = "ConfigScreen.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(ConfigScreenMain())
        yield Footer()

if __name__ == "__main__":
    app = ConfigScreen()
    app.run()