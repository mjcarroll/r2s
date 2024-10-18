from rich import terminal_theme
from textual.app import App
from textual.binding import Binding
from textual import log

ROS_AVAILABLE = True
COLCON_AVAILABLE = True

try:
    from r2s.screens.ros2.get_node import get_node
    from r2s.screens.ros2.nodes import NodeListScreen, NodeSelected
    from r2s.screens.ros2.interfaces import InterfaceListScreen
except ImportError as ex:
    ROS_AVAILABLE = False
    ROS_ERROR = ex
    print(ex)

try:
    from r2s.screens.colcon.log import LogScreen
except ImportError as ex:
    COLCON_AVAILABLE = False
    print(ex)



class UI(App):
    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit", show=True, key_display="Q"),
    ]
    MODES = {}
    current_mode = ""
    mode_stack = []
    node = None

    async def on_load(self) -> None:
        if ROS_AVAILABLE:
            self.bind("n", action="nodes", description="Nodes")
            self.bind("i", action="interfaces", description="Interfaces")

    async def on_mount(self) -> None:
        if ROS_AVAILABLE:
            self.node = get_node()
            self.MODES["interfaces"] = InterfaceListScreen(self.node)
            self.MODES["nodes"] = NodeListScreen(self.node)
            self.action_interfaces()
            self.current_mode = "interfaces"

        else:
            self.log.warning(ROS_ERROR)
        self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI


    def on_node_selected(self, message: NodeSelected) -> None:
        self.mode_stack.append(self.current_mode)
        self.MODES["interfaces"].filter_node = message.node_name
        self.switch_mode("interfaces")
        self.bind("escape", action="return", description="Return", show=True)

    def action_nodes(self) -> None:
        if self.current_mode != "nodes":
            self.switch_mode("nodes")
            self.mode_stack.append("nodes")

    def action_interfaces(self) -> None:
        self.MODES["interfaces"].filter_node = ""
        self.switch_mode("interfaces")
        self.bind("escape", action="return", description="Return", show=False)

    def action_return(self) -> None:
        if not len(self.mode_stack):
            return

        mode = self.mode_stack.pop()
        self.current_mode = mode
        self.switch_mode(self.current_mode)
        if not len(self.mode_stack):
            self.bind("escape", action="return", description="Return", show=False)

    async def on_unmount(self) -> None:
        if ROS_AVAILABLE and self.node:
            self.node.stop()
