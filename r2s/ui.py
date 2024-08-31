from textual.app import App
from textual.binding import Binding
from rich import terminal_theme

from r2s.screens.main_screen import MainScreen
from r2s.screens.colcon.package_list import PackageListScreen
from r2s.screens.ros2.nodes import NodeListScreen


class UI(App):
    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
    ]

    async def on_mount(self) -> None:
        self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI
        # await self.push_screen(MainScreen())
        # await self.push_screen(PackageListScreen())
        await self.push_screen(NodeListScreen())
