from rich import terminal_theme
from textual.app import App
from textual.binding import Binding

from r2s.screens.ros2.nodes import NodeListScreen


class UI(App):
    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
    ]

    async def on_mount(self) -> None:
        self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI
        await self.push_screen(NodeListScreen())
