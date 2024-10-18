
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive

from r2s.widgets.log_view.log_lines import LogLines
from r2s.widgets.log_view.log_source import LogSourceBase
from r2s.widgets.log_view.find_dialog import FindDialog
from r2s.widgets.log_view.messages import PointerMoved


class LogView(Horizontal):
    """Widget that contains log lines and associated widgets."""

    DEFAULT_CSS = """
    LogView {
        &.show-panel {
            LinePanel {
                display: block;
            }
        }
        LogLines {
            width: 1fr;            
        }     
        LinePanel {
            width: 50%;
            display: none;            
        }
    }
    """

    BINDINGS = [
        Binding("ctrl+t", "toggle_tail", "Tail", key_display="^t"),
        Binding("ctrl+l", "toggle('show_line_numbers')", "Line nos.", key_display="^l"),
        Binding("ctrl+f", "show_find_dialog", "Find", key_display="^f"),
        Binding("slash", "show_find_dialog", "Find", key_display="^f", show=False),
        Binding("ctrl+g", "goto", "Go to", key_display="^g"),
    ]

    show_find: reactive[bool] = reactive(False)
    show_panel: reactive[bool] = reactive(False)
    show_line_numbers: reactive[bool] = reactive(False)
    tail: reactive[bool] = reactive(False)
    can_tail: reactive[bool] = reactive(True)

    def __init__(
        self, log_source: LogSourceBase, can_tail: bool = True
    ) -> None:
        self.log_source = log_source
        super().__init__()
        self.can_tail = can_tail

    def compose(self) -> ComposeResult:
        yield (
            log_lines := LogLines(self.log_source).data_bind(
                LogView.tail,
                LogView.show_line_numbers,
                LogView.show_find,
                LogView.can_tail,
            )
        )
        #yield LinePanel()
        yield FindDialog(log_lines._suggester)
        #yield InfoOverlay().data_bind(LogView.tail)
        #yield LogFooter().data_bind(LogView.tail, LogView.can_tail)

    @on(FindDialog.Update)
    def filter_dialog_update(self, event: FindDialog.Update) -> None:
        log_lines = self.query_one(LogLines)
        log_lines.find = event.find
        log_lines.regex = event.regex
        log_lines.case_sensitive = event.case_sensitive

    async def watch_show_find(self, show_find: bool) -> None:
        if not self.is_mounted:
            return
        filter_dialog = self.query_one(FindDialog)
        filter_dialog.set_class(show_find, "visible")
        if show_find:
            filter_dialog.focus_input()
        else:
            self.query_one(LogLines).focus()

    @on(FindDialog.Dismiss)
    def dismiss_filter_dialog(self, event: FindDialog.Dismiss) -> None:
        event.stop()
        self.show_find = False

    @on(FindDialog.MovePointer)
    def move_pointer(self, event: FindDialog.MovePointer) -> None:
        event.stop()
        log_lines = self.query_one(LogLines)
        log_lines.advance_search(event.direction)

    def action_show_find_dialog(self) -> None:
        find_dialog = self.query_one(FindDialog)
        if not self.show_find or not any(
            input.has_focus for input in find_dialog.query("Input")
        ):
            self.show_find = True
            find_dialog.focus_input()

    @on(PointerMoved)
    async def pointer_moved(self, event: PointerMoved):
        if event.pointer_line is None:
            self.show_panel = False
        if self.show_panel:
            await self.update_panel()

        log_lines = self.query_one(LogLines)
        pointer_line = (
            log_lines.scroll_offset.y
            if event.pointer_line is None
            else event.pointer_line
        )
