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
class Service:
    name: str
    type: str


class ServicesFetched(Message):
    def __init__(self, service_list: List[Service]) -> None:
        self.service_list = service_list
        super().__init__()


class ServiceListWatcher(WatcherBase):
    target: Widget

    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self) -> None:
        while not self._exit_event.is_set():
            services: List[Service] = []
            service_names_and_types = self.node.node.get_service_names_and_types()

            # Fill list of services
            for s in service_names_and_types:

                services.append(
                    Service(
                        name=s[0],
                        type=s[1],
                    )
                )
            self.target.post_message(ServicesFetched(services))
            time.sleep(0.2)


class ServiceListGrid(DataGrid):
    id = "service_list_table"

    def __init__(self):
        super().__init__(id=self.id)

    def columns(self):
        return [
            "Name",
            "Type",
        ]

    def on_services_fetched(self, message: ServicesFetched) -> None:
        message.stop()
        table = self.query_one("#" + self.id, DataTable)
        for service in message.service_list:

            if service.name not in table.rows:
                table.add_row(
                    service.name,
                    service.type,
                    key=service.name,
                )


class ServiceListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self, node):
        self.watcher = ServiceListWatcher(node)
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(ServiceListGrid)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ServiceListGrid()
        yield Footer()
