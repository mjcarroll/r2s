import time

from textual.screen import Screen
from textual.app import ComposeResult

from textual.widgets import Footer

from textual import log

from r2s.widgets import Header
from r2s.widgets import DataGrid
from r2s.watcher import WatcherBase


class NodeWatcher(WatcherBase):
    def run(self) -> None:
        while not self._exit_event.is_set():
            time.sleep(1.0)
            log("Watching")


class MainScreen(Screen):
    CSS = """
    MainScreen {}
    """

    def __init__(self):
        self.watcher = NodeWatcher()
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataGrid()
