from dataclasses import dataclass

from textual import log
from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Footer

from r2s.watcher import WatcherBase
from r2s.widgets import DataGrid, Header

from typing import List
import time

@dataclass(frozen=True, eq=False)
class Action:
    name: str
    type: str


class ActionsFetched(Message):
    def __init__(self, action_list: List[Action]) -> None:
        self.action_list = action_list
        super().__init__()


class ActionListWatcher(WatcherBase):
    target: Widget

    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self) -> None:
        while not self._exit_event.is_set():
            actions: List[Action] = []
            action_names_and_types = self.node.node.handle.get_action_names_and_types()

            # Fill list of actions
            for s in action_names_and_types:

                actions.append(
                    Action(
                        name=s[0],
                        type=s[1],
                    )
                )
            self.target.post_message(ActionsFetched(actions))
            time.sleep(0.2)


class ActionListGrid(DataGrid):
    id = "action_list_table"

    def __init__(self):
        super().__init__(id=self.id)

    def columns(self):
        return [
            "Name",
            "Type",
        ]

    def on_actions_fetched(self, message: ActionsFetched) -> None:
        message.stop()
        table = self.query_one("#" + self.id, DataTable)
        for action in message.action_list:

            if action.name not in table.rows:
                table.add_row(
                    action.name,
                    action.type,
                    key=action.name,
                )


class ActionListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self, node):
        self.watcher = ActionListWatcher(node)
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(ActionListGrid)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ActionListGrid()
        yield Footer()
