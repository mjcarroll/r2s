from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, ContentSwitcher, DataTable
from textual.widget import Widget

from textual import events
from textual import log

from rich.text import Text

from r2s.modals import HelpModal


class NodeWidget(Widget):
    DEFAULT_CSS = """
        NodeWidget {
            height: 100%;
            width: 100%;
        } 
    """

    def compose(self) -> ComposeResult:
        table: DataTable[Text] = DataTable(
            id="node_table",
            header_height=1,
            show_cursor=True,
            zebra_stripes=True,
        )
        table.focus()
        table.add_column("ns")
        table.add_column("node")

        table.add_row(Text("foo", justify="left"), Text("bar"))
        table.add_row(Text("foo", justify="left"), Text("baz"))
        table.cursor_type = "row"
        table.ordered_columns[0].content_width = 50
        yield table


class AppHeader(Horizontal):
    def on_mount(self):
        self.styles.border = (None, None)


class Body(Vertical):
    BORDER_TITLE = "Nodes (all) [0]"

    def on_mount(self):
        self.styles.border = ("solid", "white")

    def compose(self) -> ComposeResult:
        yield NodeWidget()


class r2sApp(App):
    TITLE = "r2s"
    SUBTITLE = "TUI for ros2cli"
    CSS_PATH = "ui.tcss"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
        Binding("esc", "escape", "Esc"),
        ("/", "search", "Search"),
        (":", "command", "Command"),
        ("?", "help", "Help"),
    ]

    def on_mount(self):
        self.search = self.get_widget_by_id("search")
        self.command = self.get_widget_by_id("command")
        self.search.disabled = True
        self.command.disabled = True

    def compose(self):
        yield AppHeader(id="header")
        with ContentSwitcher(id="switcher"):
            yield Input(id="search", placeholder="Search text...")
            yield Input(id="command", placeholder="Command text...")
        yield Body(id="body")

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_search(self) -> None:
        log("action_search")
        self.query_one(ContentSwitcher).current = "search"
        self.search.disabled = False
        self.search.focus()

    def action_command(self) -> None:
        log("action_command")
        self.query_one(ContentSwitcher).current = "command"
        self.command.disabled = False
        self.command.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            search_string = event.value.strip()
        elif event.input.id == "command":
            command_string = event.value.strip()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.app.search.value = ""
            self.search.disabled = True
            self.query_one(ContentSwitcher).current = None
        elif event.input.id == "command":
            self.app.command.value = ""
            self.command.disabled = True
            self.query_one(ContentSwitcher).current = None


def main(*args, **kwargs):
    app = r2sApp()
    app.run()


if __name__ == "__main__":
    main()
