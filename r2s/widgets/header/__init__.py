from textual.widget import Widget

class Header(Widget):
    DEFAULT_CSS = """
    Header {
      border: none;
      border-title-align: center;
      grid-columns: 20 1fr 50;
      grid-size: 3;
      height: 7;
      layout: grid;
    }
    """
