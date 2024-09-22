from rich import terminal_theme
from textual.app import App
from textual.binding import Binding
from r2s.screens.ros2.nodes import NodeListScreen
from r2s.screens.ros2.topics import TopicListScreen


class UI(App):
    BINDINGS = [
        Binding(key="n", action="switch_mode('nodes')", description="Nodes", key_display="n"),
        Binding(key="t", action="switch_mode('topics')", description="Topics", key_display="t"),
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
    ]
    MODES = {
        "nodes": NodeListScreen,
        "topics": TopicListScreen,
    }

    async def on_mount(self) -> None:
        self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI
        self.switch_mode("nodes")
