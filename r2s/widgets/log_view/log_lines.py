from textual.scroll_view import ScrollView

from textual.reactive import reactive

class LogLines(ScrollView):
    show_find: reactive[bool] = reactive(False)
    show_line_numbers: reactive[bool] = reactive(False)
