from textual.widget import Widget
from textual.widgets import Static

LOGO = """       ________
_______\\_____  \\   ______
\\_  __ \\/  ____/  /  ___/
 |  | \\/       \\  \\___ \\
 |__|  \\_______ \\/____  >
               \\/     \\/ """

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

    def left(self):
        return Static("", classes="header-box")

    def center(self):
        return Static("", classes="header-box")

    def right(self):
        return Static(LOGO, classes="header-box")

    def compose(self):
        yield self.left()
        yield self.center()
        yield self.right()
