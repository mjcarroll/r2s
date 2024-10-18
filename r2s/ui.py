from rich import terminal_theme
from textual.app import App
from textual.binding import Binding
from r2s.screens.ros2.lifecycle_nodes import LifecycleNodesListScreen
from r2s.screens.ros2.nodes import NodeListScreen
from r2s.screens.ros2.topics import TopicListScreen
from r2s.screens.ros2.services import ServiceListScreen
from r2s.screens.ros2.actions import ActionListScreen

from r2s.screens.ros2.get_node import get_node


class UI(App):
    BINDINGS = [
        Binding(
            key="n", action="switch_mode('nodes')", description="Nodes", key_display="n"
        ),
        Binding(
            key="t",
            action="switch_mode('topics')",
            description="Topics",
            key_display="t",
        ),
        Binding(
            key="l",
            action="switch_mode('lifecycle')",
            description="Lifecycle",
            key_display="l",
        ),
        Binding)
            key="s",
            action="switch_mode('services')",
            description="Services",
            key_display="s",
        ),
        Binding(
            key="a",
            action="switch_mode('actions')",
            description="Actions",
            key_display="a",
        ),
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
    ]
    MODES = {}

    node = get_node()

    async def on_mount(self) -> None:
        self.MODES["lifecycle"] = LifecycleNodesListScreen(self.node)
        self.MODES["nodes"] = NodeListScreen(self.node)
        self.MODES["topics"] = TopicListScreen(self.node)
        self.MODES["services"] = ServiceListScreen(self.node)
        self.MODES["actions"] = ActionListScreen(self.node)
        self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI
        self.switch_mode("nodes")

    async def on_unmount(self) -> None:
        self.node.stop()
