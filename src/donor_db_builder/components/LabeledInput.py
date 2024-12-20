from textual.containers import Horizontal
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.widgets import Static

class LabeledInput(Static):

    def __init__(self, label: str, placeholder: str = "", value: str = "", password: bool = False, id: str | None = None):
        super().__init__()
        self.label_text = label
        self.placeholder = placeholder
        self.value = value
        self.password = password
        self.input_id = id
        self.classes = "input-row"

    def compose(self) -> ComposeResult:
        yield Label(self.label_text, classes="label")
        yield Input(placeholder=self.placeholder, value=self.value, password=self.password, id=self.input_id, classes="input")
