from dataclasses import dataclass

from textual import log
from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable

from r2s.watcher import WatcherBase
from r2s.widgets import DataGrid
from r2s.widgets import Header

from typing import List


# TODO update to core, rather than quick debugging
from r2s.screens.ros2.get_node import get_node


@dataclass(frozen=True, eq=False)
class Topic:
    name: str
    type: str
    numPubs: int
    numSubs: int
    # TODO add node where the topic is coming from
    # TODO namespace

class TopicsFetched(Message):
    def __init__(self, topic_list: List[Topic]) -> None:
        self.topic_list = topic_list
        super().__init__()

class TopicListWatcher(WatcherBase):
    target: Widget

    def run(self) -> None:
        while not self._exit_event.is_set():
            topics: List[Topic] = []

            # TODO probably want to get node from node screen
            node = get_node()
            topic_names_and_types = node.get_topic_names_and_types()

            # Fill list of topics
            for t in topic_names_and_types:
                topicName = t[0]
                numPubs = node.count_publishers(topicName)
                numSubs = node.count_subscribers(topicName)
                topics.append(
                    Topic(name=topicName, type=t[1], numPubs=numPubs, numSubs=numSubs)
                )

            log(topics)
            self.target.post_message(TopicsFetched(topics))

class TopicListGrid(DataGrid):
    def columns(self):
        return ["Name", "Type", "# Pubs", "# Subs"]

    def on_topics_fetched(self, message: TopicsFetched) -> None:
        message.stop()

        table = self.query_one("#data_table", DataTable)
        for topic in message.topic_list:
            if topic.name not in table.rows:
                table.add_row(
                    topic.name,
                    topic.type,
                    topic.numPubs,
                    topic.numSubs,
                    )

class TopicListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self):
        self.watcher = TopicListWatcher()
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(TopicListGrid)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield TopicListGrid()