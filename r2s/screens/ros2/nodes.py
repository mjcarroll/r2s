import time
from dataclasses import dataclass
from typing import List

from textual import log
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import DataTable, Footer

from r2s.watcher import WatcherBase
from r2s.widgets import DataGrid, Header


@dataclass(frozen=True, eq=False)
class Node:
    namespace: str
    name: str
    full_name: str


class NodesFetched(Message):
    def __init__(self, node_list: List[Node]) -> None:
        self.node_list = node_list
        super().__init__()


class NodeListWatcher(WatcherBase):
    target: Widget

    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self) -> None:
        while not self._exit_event.is_set():
            log("nodelistwatcher::run")
            nodes: List[Node] = []
            node_names_and_namespaces = self.node.node.get_node_names_and_namespaces()

            # Fill list of nodes here
            for t in node_names_and_namespaces:
                nodes.append(
                    Node(
                        name=t[0],
                        namespace=t[1],
                        full_name=t[1] + ("" if t[1].endswith("/") else "/") + t[0],
                    )
                )
            self.target.post_message(NodesFetched(nodes))
            time.sleep(0.5)


class NodeListGrid(DataGrid):
    def columns(self):
        return ["Namespace", "Name", "Full Name"]

    def on_nodes_fetched(self, message: NodesFetched) -> None:
        message.stop()
        table = self.query_one("#data_table", DataTable)
        for node in message.node_list:
            if node.full_name not in table.rows:
                table.add_row(
                    node.namespace,
                    node.name,
                    node.full_name,
                    key=node.full_name
                )


class NodeListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self, node):
        self.watcher = NodeListWatcher(node)
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(NodeListGrid)
        self.watcher.start()
        log("on_mount")

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield NodeListGrid()
        yield Footer()
