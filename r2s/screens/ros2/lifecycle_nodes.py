from dataclasses import dataclass

from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Footer

from r2s.watcher import WatcherBase
from r2s.widgets import DataGrid, Header

from ros2lifecycle import api as r2CycleApi

from typing import List
import time


@dataclass(frozen=True, eq=False)
class LifecycleNode:
    name: str
    state: str


class LifecycleNodesFetched(Message):
    def __init__(self, lifecycle_nodes_list: List[LifecycleNode]) -> None:
        self.lifecycle_nodes_list = lifecycle_nodes_list
        super().__init__()


class LifecycleNodesListWatcher(WatcherBase):
    target: Widget

    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self) -> None:
        while not self._exit_event.is_set():
            lifecycle_nodes: List[LifecycleNode] = []

            # TODO make include_hidden_nodes an option, for now default to true
            node_names = r2CycleApi.get_node_names(
                node=self.node.node, include_hidden_nodes=True
            )

            states = r2CycleApi.call_get_states(
                node=self.node.node, node_names=[name.full_name for name in node_names]
            )

            # Fill list of lifecycle nodes
            for n in node_names:

                state = states[n.full_name]

                lifecycle_nodes.append(
                    LifecycleNode(name=n.full_name, state=state.label.upper())
                )
            self.target.post_message(LifecycleNodesFetched(lifecycle_nodes))
            time.sleep(0.2)


class LifecycleNodesListGrid(DataGrid):
    id = "lifecycle_nodes_list_table"

    def __init__(self):
        super().__init__(id=self.id)

    def columns(self):
        return ["Name", "State"]

    def on_lifecycle_nodes_fetched(self, message: LifecycleNodesFetched) -> None:
        message.stop()
        table = self.query_one("#" + self.id, DataTable)
        for lifecycle_node in message.lifecycle_nodes_list:

            if lifecycle_node.name not in table.rows:
                table.add_row(
                    lifecycle_node.name,
                    lifecycle_node.state,
                    key=lifecycle_node.name,
                )
            elif table.get_cell(lifecycle_node.name, "state") != lifecycle_node.state:
                table.update_cell(lifecycle_node.name, "state", lifecycle_node.state)


class LifecycleNodesListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self, node):
        self.watcher = LifecycleNodesListWatcher(node)
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(LifecycleNodesListGrid)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield LifecycleNodesListGrid()
        yield Footer()
