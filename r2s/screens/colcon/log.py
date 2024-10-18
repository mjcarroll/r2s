from textual.app import ComposeResult
from textual.screen import Screen

from textual import log

from r2s.widgets.log_view import LogView
from r2s.widgets.log_view.log_source import LogFileSource
from r2s.screens.colcon.header import Header

class LogScreen(Screen):
    CSS = """
    LogScreen {}
    """

    def compose(self) -> ComposeResult:
        lfs = LogFileSource("/usr/local/google/home/mjcarroll/workspaces/ros2_rolling/log/latest_build/logger_all.log")

        yield Header()
        yield LogView(lfs)
