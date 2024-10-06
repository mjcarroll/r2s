from textual.widget import Widget
from textual.widgets import Static

from ros2doctor.api import platform

import os
import socket

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

    ros_version = ""
    distro_report = platform.RosdistroReport()
    report = distro_report.report()
    for k, v in report.items:
        if k == 'distribution name':
            ros_version = v
            break

    hostname = socket.gethostname()

    workspace = os.getcwd()

    INFO = """0.0.1
{ros_version}
{hostname}
{workspace}""".format(ros_version=ros_version, hostname=hostname, workspace=workspace)

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
