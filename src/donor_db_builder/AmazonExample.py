from textual.app import App, ComposeResult
from textual.widgets import RadioButton, RadioSet, Footer, Header, Static, \
    Input, Label, Tree, TabbedContent, TabPane
from textual.containers import Container
#import boto3

class AWSAccessStateInfo(Static):

    def on_mount(self) -> None:
        self.check_aws_access()

    def check_aws_access(self) -> None:
        aws_connection_state_btn = self.query_one(RadioButton)
        isConnected = self.isConnectable()
        if isConnected:
            aws_connection_state_btn.styles.border = ("solid", "green")
            # aws_connection_state_btn.action_toggle()
            aws_connection_state_btn.disabled = False
        else:
            aws_connection_state_btn.styles.border = ("solid", "darkred")

    def isConnectable(self):
        """ !FIX: Is there a better way to test if client has access to AWS? """
        # try:
            # s3 = boto3.client('s3')
            # s3.list_buckets()
        return True
        # except Exception as e:
        #     print(f"Connection test failed: {e}")
        #     return False

    def compose(self) -> ComposeResult:
        yield Label("AWS:", id='aws-access-state-label')
        yield RadioButton("Good", id="aws-access-state-value", disabled=True)

class AmiInfo(Static):

    def compose(self) -> ComposeResult:
        yield Label("AMI ID:", id="ami-label")
        yield Input(placeholder="(ami-id)", id="ami-id")

class VersionInfo(Static):

    def compose(self) -> ComposeResult:
        yield Label("Ver:", id="version-label")
        yield Input(placeholder="xx.yy.zz(-abc)", id="version-number")

class AWSMonitorBody(Static):

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="yum-repositories-tab",id="aws-resources-tabbed-content"):
            with TabPane("Yum Repos", id="yum-repositories-tab"):
                yield Tree("Repositories", id="tree-control")
            with TabPane("Base AMIs",id="base-amis-tab"):
                with RadioSet(id="radio-button-group"):
                    yield RadioButton("Centos 7")
                    yield RadioButton("Centos 8")
                    yield RadioButton("Red Hat 8")
                    yield RadioButton("Rocky 9")


class MottoInfo(Static):

    def compose(self) -> ComposeResult:
        yield Label("Motto:", id='motto-label')
        yield Input(placeholder="     (Enter Motto)", id="motto-value")


class AWSMonitorHeader(Static):
    """An AWS Monitor widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of an AWS monitor."""
        yield Container(AWSAccessStateInfo())
        yield Container(AmiInfo())
        yield Container(VersionInfo())
        yield Container(MottoInfo())

class AWSMonitorMain(Static):

    def compose(self) -> ComposeResult:
        """Create child widgets of an AWS monitor."""
        yield Container(AWSMonitorHeader())
        yield Container(AWSMonitorBody())

class AWSMonitorApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "AWS_MonitorApp.css"
    # BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(AWSMonitorMain())

if __name__ == "__main__":
    app = AWSMonitorApp()
    app.run()