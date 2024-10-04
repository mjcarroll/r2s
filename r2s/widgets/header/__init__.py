from textual.widget import Widget
from textual.widgets import Static


class Header(Widget):
    DEFAULT_CSS = """
    Header {
      border: none;
      border-title-align: center;
      grid-columns: 20 1fr 30;
      height: 8;
      grid-size: 3;
      layout: grid;
    }

    .header-box {
      margin: 0 0 0 3;
      text-align: left;
    }
    """

    TITLES = """r2s Version:
ROS Version:
Hostname:
Workspace:
"""

    INFO = """0.0.1
jazzy
mjcarroll.c.googlers.com
~/workspaces/in_sdk/"""

    LOGO = """       ________
_______\\_____  \\   ______
\\_  __ \\/  ____/  /  ___/
 |  | \\/       \\  \\___ \\
 |__|  \\_______ \\/____  >
               \\/     \\/ """

    def compose(self):
        yield Static(self.TITLES, classes="header-box")
        yield Static(self.INFO, classes="header-box")
        yield Static(self.LOGO, classes="header-box")
