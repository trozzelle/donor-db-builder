# import click
from dotenv import load_dotenv

# from .config import get_setting, set_setting
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Label, Button, Static
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from config import Config
from components.LabeledInput import LabeledInput

load_dotenv("../../.env")




class ConfigScreen(Static):
    def __init__(self):
        super().__init__()
        self.config = Config()

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("Neo4j Configuration", classes="heading"),
            # Label("Host", classes="label"),
            # Input(
            #     placeholder="localhost",
            #     value=self.config.get_setting("NEO_HOST", "localhost"),
            #     id="neo_host",
            # ),
            Label("Port", classes="label"),
            Input(
                placeholder="7687",
                value=self.config.get_setting("NEO_PORT", "7687"),
                id="neo_port",
            ),
            Label("Username", classes="label"),
            Input(
                placeholder="neo4j",
                value=self.config.get_setting("NEO_USER", "neo4j"),
                id="neo_user",
            ),
            Label("Password", classes="label"),
            Input(
                placeholder="neo4j",
                value=self.config.get_setting("NEO_PASS", "neo4j"),
                id="neo_password",
                password=True,
            ),
            LabeledInput(label="Host", placeholder="localhost", value=self.config.get_setting("NEO_HOST", "localhost"), id="neo_host"),
            Button("Save Configuration", id="save_config", variant="primary"),
            id="config_container",
        )

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "save_config":
                for input_widget in self.query(Input):
                    self.config.set_setting(input_widget.id, input_widget.value)
                self.notify("Configuration saved", severity="success")


class DonorBuilder(App):
    CSS_PATH = ["styles/config.tcss"]

    CSS = """
    # ConfigScreen {
    #     padding: 1 2;
    # }
    # 
    # .heading {
    #     text-style: bold;
    #     margin-bottom: 1;
    # }
    # 
    # #config_container {
    #     width: 100%;
    #     height: auto;
    # }
    # 
    # Input > .input--label {
    #     width: 15;  /* Fixed width for labels */
    #     color: $text;
    #     padding-bottom: 1;
    # }
    # 
    # Button {
    #     margin-top: 1;
    # }
    # """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ConfigScreen()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


# @click.group()
# def cli():
#     """Donor Database Builder CLI"""
#     pass
#
# @cli.group()
# def config():
#     """Manage persistent configuration"""
#     pass
#
# @config.command()
# @click.argument("key")
# @click.argument("value")
# def set(key, value):
#     """Set a configuration value"""
#     set_setting(key, value)
#     click.echo(f"Set {key} to {value}")
#
# @config.command()
# @click.argument("key")
# def get(key):
#     """Get a configuration value"""
#     value = get_setting(key)
#     if value is None:
#         click.echo(f"No value set for {key}")
#     else:
#         click.echo(f"{key}: {value}")
#
# @cli.command()
# @click.option('--host', envvar='NEO_HOST',
#               default=lambda: get_setting('NEO_HOST', 'localhost'),
#               help='Neo4j DB host')
# @click.option('--port', envvar='NEO_PORT',
#               default=lambda: get_setting('NEO_PORT', '7687'),
#               help='Neo4j DB port')
# @click.option('--user', envvar='NEO_USER',
#               default=lambda: get_setting('NEO_USER', 'neo4j'),
#               help='Neo4j DB user')
# @click.option('--password', envvar='NEO_PASS',
#               default=lambda: get_setting('NEO_PASS', 'neo4j'),
#               help='Neo4j DB pass')
# def import_data(host, port, user, password):
#     """Import campaign finance data"""
#     uri = f"neo4j://{host}:{port}"
#     # Your existing import logic here
#     click.echo(f"Import data")
#     pass


if __name__ == "__main__":
    app = DonorBuilder()
    app.run()
