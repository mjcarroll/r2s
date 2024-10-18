from r2s.widgets.header import Header

from textual.widgets import Static

class ColconHeader(Header):
    def left(self):
        return Static("", classes="header-box")

    def center(self):
        return Static("", classes="header-box")
