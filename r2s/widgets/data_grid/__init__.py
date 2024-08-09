from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from textual.reactive import reactive

from rich.text import Text

from textual.widgets import DataTable

from r2s.widgets.find_dialog import FindDialog

from typing import List

class DataGrid(Horizontal):
    DEFAULT_CSS = """
    DataGrid{
        width: 1fr;
        padding-left: 1;
        padding-right: 1;
    }
    """

    BINDINGS = [
        Binding("<,left", "dec_sort_key", "Previous Sort"),
        Binding(">,right", "inc_sort_key", "Next Sort"),
        Binding("ctrl+f", "show_find_dialog", "Find", key_display="^f"),
        Binding("slash", "show_find_dialog", "Find", key_display="^f", show=False),
    ]

    show_find: reactive[bool] = reactive(False)
    sort_idx: int = 0

    def columns(self) -> List[str]:
        """Get the column labels"""
        return []

    def compose(self) -> ComposeResult:
        table: DataTable[Text] = DataTable(
            id = "data_table",
            header_height = 1,
            show_cursor = True,
            zebra_stripes = True,
        )
        table.focus()

        for col in self.columns():
            table.add_column(col, key=col.lower())

        table.cursor_type='row'
        yield table
        yield FindDialog()


    async def watch_show_find(self, show_find: bool) -> None:
        if not self.is_mounted:
            return
        filter_dialog = self.query_one(FindDialog)
        filter_dialog.set_class(show_find, "visible")
        if show_find:
            filter_dialog.focus_input()
        else:
            self.query_one(DataTable).focus()

    def action_show_find_dialog(self) -> None:
        find_dialog = self.query_one(FindDialog)
        if not self.show_find or not any(
            input.has_focus for input in find_dialog.query("Input")
        ):
            self.show_find = True
            find_dialog.focus_input()

    @on(FindDialog.Dismiss)
    def dismiss_filter_dialog(self, event: FindDialog.Dismiss) -> None:
        event.stop()
        self.show_find = False

    def action_inc_sort_key(self) -> None:
        """Method called to update the table sort key attribute."""
        table = self.query_one(DataTable)
        self.sort_idx = self.sort_idx + 1

        cols = self.columns()
        if self.sort_idx >= len(cols):
            self.sort_idx = len(cols) - 1

        table.sort(cols[self.sort_idx].lower())

    def action_dec_sort_key(self) -> None:
        table = self.query_one(DataTable)
        self.sort_idx = self.sort_idx - 1
        cols = self.columns()
        if self.sort_idx < 0:
            self.sort_idx = 0

        table.sort(cols[self.sort_idx].lower())
