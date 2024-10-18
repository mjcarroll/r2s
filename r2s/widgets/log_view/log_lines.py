import re

from threading import Event, RLock, Thread
from typing import Mapping

from rich.segment import Segment
from rich.text import Text
from rich.style import Style

from textual import events, on, work, log
from textual.binding import Binding
from textual.cache import LRUCache
from textual.geometry import Region, Size
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.suggester import Suggester
from textual.worker import Worker, get_current_worker

from r2s.widgets.log_view.messages import NewBreaks, ScanComplete
from r2s.widgets.log_view.find_dialog import FindDialog

SPLIT_REGEX = r"[\s/\[\]\(\)\"\/]"

class SearchSuggester(Suggester):
    def __init__(self, search_index: Mapping[str, str]) -> None:
        self.search_index = search_index
        super().__init__(use_cache=False, case_sensitive=True)

    async def get_suggestion(self, value: str) -> str | None:
        word = re.split(SPLIT_REGEX, value)[-1]
        start = value[: -len(word)]

        if not word:
            return None
        search_hit = self.search_index.get(word.lower(), None)
        if search_hit is None:
            return None
        return start + search_hit


class LogLines(ScrollView, inherit_bindings=False):
    DEFAULT_CSS = """
    LogLines {
        scrollbar-gutter: stable;
        overflow: scroll;
        border: heavy transparent;        
        .loglines--filter-highlight {
            background: $secondary;
            color: auto;
        }
        .loglines--pointer-highlight {
            background: $primary;
        }
        &:focus {
            border: heavy $accent;
        }

        border-subtitle-color: $success;
        border-subtitle-align: center;        
        align: center middle;

        &.-scanning {
            tint: $background 30%;
        }
        .loglines--line-numbers {
            color: $warning 70%;            
        }
        .loglines--line-numbers-active {
            color: $warning;            
            text-style: bold;
        }               
    }
    """
    COMPONENT_CLASSES = {
        "loglines--filter-highlight",
        "loglines--pointer-highlight",
        "loglines--line-numbers",
        "loglines--line-numbers-active",
    }

    BINDINGS = [
        Binding("up,w,k", "scroll_up", "Scroll Up", show=False),
        Binding("down,s,j", "scroll_down", "Scroll Down", show=False),
        Binding("left,h", "scroll_left", "Scroll Left", show=False),
        Binding("right,l", "scroll_right", "Scroll Right", show=False),
        Binding("home,G", "scroll_home", "Scroll Home", show=False),
        Binding("end,g", "scroll_end", "Scroll End", show=False),
        Binding("pageup,b", "page_up", "Page Up", show=False),
        Binding("pagedown,space", "page_down", "Page Down", show=False),
        Binding("enter", "select", "Select line", show=False),
        Binding("escape", "dismiss", "Dismiss", show=False, priority=True),
        Binding("m", "navigate(+1, 'm')"),
        Binding("M", "navigate(-1, 'm')"),
        Binding("o", "navigate(+1, 'h')"),
        Binding("O", "navigate(-1, 'h')"),
        Binding("d", "navigate(+1, 'd')"),
        Binding("D", "navigate(-1, 'd')"),
    ]
     
    show_find = reactive(False)
    find = reactive("")
    show_gutter = reactive(False)
    pointer_line: reactive[int | None] = reactive(None, repaint=False)
    is_scrolling: reactive[int] = reactive(int)
    pending_lines: reactive[int] = reactive(int)
    tail: reactive[bool] = reactive(True)
    can_tail: reactive[bool] = reactive(True)
    show_line_numbers: reactive[bool] = reactive(False)

    def __init__(self, log_source) -> None:
        super().__init__()
        self.log_source = log_source
        self._max_width = 0
        self._line_count = 0
        self._scanned_size = 0
        self._scan_start = 0
        self._gutter_width = 0
        self._line_breaks: list[int] = []
        self.icons: dict[int, str] = {}

        self._lock = RLock()
        self._line_cache: LRUCache[int, str] = LRUCache(10000)
        self._render_line_cache: LRUCache[tuple[int, int, bool, str], Strip] = LRUCache(maxsize=1000)
        self._search_index: LRUCache[str, str] = LRUCache(maxsize=10000)
        self._suggester = SearchSuggester(self._search_index)


    @property
    def line_count(self) -> int:
        with self._lock:
            return self._line_count

    @property
    def gutter_width(self) -> int:
        return self._gutter_width

    def clear_caches(self) -> None:
        self._line_cache.clear()

    def validate_pointer_line(self, pointer_line: int | None) -> int | None:
        if pointer_line is None:
            return None
        if pointer_line < 0:
            return 0
        if pointer_line >= self.line_count:
            return self.line_count - 1
        return pointer_line


    def on_mount(self) -> None:
        self.loading = True
        self.add_class("-scanning")
        self.initial_scan_worker = self.run_scan()

    def on_unmount(self) -> None:
        self.log_source.close()

    def on_idle(self) -> None:
        self.update_virtual_size()

    def update_virtual_size(self) -> None:
        self.virtual_size = Size(
            self._max_width 
            + (self.gutter_width if self.show_line_numbers else 0),
            self.line_count
        )

    def render_lines(self, crop: Region) -> list[Strip]:
        self.update_virtual_size()

        page_height = self.scrollable_content_region.height
        scroll_y = self.scroll_offset.y
        line_count = self.line_count


        for index in range(
            max(0, scroll_y - page_height),
            min(line_count, scroll_y + page_height + page_height),
        ):
            if index not in self._line_cache:
                self._line_cache.set(index, self.log_source.get_line(index))
        if self.show_line_numbers:
            max_line_no = self.scroll_offset.y + page_height
            self._gutter_width = len(f"{max_line_no+1} ")
        else:
            self._gutter_width = 0
        if self.pointer_line is not None:
            self._gutter_width += 3
        return super().render_lines(crop)

    def render_line(self, y:int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        index = y + scroll_y
        style = self.rich_style
        width, height = self.size
        if index >= self.line_count:
            return Strip.blank(width, style)

        is_pointer = self.pointer_line is not None and index == self.pointer_line
        cache_key = (index, is_pointer, self.find)

        try:
            strip = self._render_line_cache[cache_key]
        except KeyError:
            line = self.log_source.get_line(index)
            if len(line) > 150:
                line = line[:150] + "..."
            text = Text(line)
            text.stylize_before(style)
            if is_pointer:
                pointer_style = self.get_component_rich_style(
                    "loglines--pointer-highlight"
                )
                text.stylize(Style(bgcolor=pointer_style.bgcolor, bold=True))
                search_index = self._search_index

            search_index = self._search_index
            for word in re.split(SPLIT_REGEX, text.plain):
                if len(word) <= 1:
                    continue
                for offset in range(1, len(word) - 1):
                    sub_word = word[:offset]
                    if sub_word in search_index:
                        if len(search_index[sub_word]) < len(word):
                            search_index[sub_word.lower()] = word
                    else:
                        search_index[sub_word.lower()] = word

            if self.find and self.show_find:
                self.highlight_find(text)

            strip = Strip(text.render(self.app.console), text.cell_len)
            self._max_width = max(self._max_width, strip.cell_length)
            self._render_line_cache[cache_key] = strip

        if is_pointer: 
            pointer_style = self.get_component_rich_style("loglines--pointer-highlight")
            strip = strip.crop_extend(scroll_x, scroll_x + width, pointer_style)
        else:
            strip = strip.crop_extend(scroll_x, scroll_x + width, None)

        if self.show_gutter or self.show_line_numbers:
            line_number_style = self.get_component_rich_style(
                "loglines--line-numbers-active"
                if index == self.pointer_line
                else "loglines--line-numbers"
            )
            if self.pointer_line is not None and index == self.pointer_line:
                icon = "👉"
            else:
                icon = self.icons.get(index, " ")

            if self.show_line_numbers:
                segments = [Segment(f"{index+1} ", line_number_style), Segment(icon)]
            else:
                segments = [Segment(icon)]
            icon_strip = Strip(segments)
            icon_strip = icon_strip.adjust_cell_length(self._gutter_width)
            strip = Strip.join([icon_strip, strip])
        return strip

    def update_line_count(self) -> None:
        line_count = len(self._line_breaks)
        line_count = max(1, line_count)
        self._line_count = line_count

    @work(thread=True)
    def run_scan(self) -> None:
        worker = get_current_worker()

        try:
            if not self.log_source.open(worker.cancelled_event):
                self.loading = False
                return
        except FileNotFoundError:
            self.notify(
                f"Could not open log source {self.log_source}", severity="error"
            )
            self.loading = False
            return

        new_count = self.log_source.scan()
        log(new_count)
        self._line_count = self.log_source.num_lines()
        self.loading = False

    def highlight_regex(self, text: Text) -> None:
        filter_style = self.get_component_rich_style("loglines--filter-highlight")
        try:
            re.compile(self.find)
        except Exception:
            # Invalid regex
            return
        matches = list(
            re.finditer(
                self.find,
                text.plain,
                flags=0 if self.case_sensitive else re.IGNORECASE,
            )
        )
        if matches:
            for match in matches:
                text.stylize(filter_style, *match.span())
        else:
            text.stylize("dim")

    def highlight_words(self, text: Text) -> None:
        filter_style = self.get_component_rich_style("loglines--filter-highlight")
        if not text.highlight_words(
            [self.find], filter_style, case_sensitive=self.case_sensitive
        ):
            text.stylize("dim")


    def highlight_find(self, text: Text) -> None:
        if self.regex:
            self.highlight_regex(text)
        else:
            self.highlight_words(text)

    def check_match(self, line: str) -> bool:
        if not line:
            return True
        if self.regex:
            try:
                return (
                    re.match(
                        self.find,
                        line,
                        flags=0 if self.case_sensitive else re.IGNORECASE,
                    )
                    is not None
                )
            except Exception:
                self.notify("Regex is invalid!", severity="error")
                return True
        else:
            if self.case_sensitive:
                return self.find in line
            else:
                return self.find.lower() in line.lower()

    def advance_search(self, direction: int = 1) -> None:
        first = self.pointer_line is None
        start_line = (
            (
                self.scroll_offset.y
                if direction == 1
                else self.scroll_offset.y + self.scrollable_content_region.height - 1
            )
            if self.pointer_line is None
            else self.pointer_line + direction
        )
        if direction == 1:
            line_range = range(start_line, self.line_count)
        else:
            line_range = range(start_line, -1, -1)

        scroll_y = self.scroll_offset.y
        max_scroll_y = scroll_y + self.scrollable_content_region.height - 1
        if self.show_find:
            check_match = self.check_match

            with self._lock:
                for line_no in line_range:
                    line = self._line_cache.get(line_no)
                    if check_match(line):
                        self.pointer_line = line_no
                        self.scroll_pointer_to_center()
                        break
            self.app.bell()
        else:
            self.pointer_line = next(
                iter(line_range), self.pointer_line or self.scroll_offset.y
            )
        if first:
            self.refresh()
        else:
            if self.pointer_line is not None and (
                self.pointer_line < scroll_y or self.pointer_line > max_scroll_y
            ):
                self.scroll_pointer_to_center()

    def scroll_pointer_to_center(self, animate: bool = True):
        if self.pointer_line is None:
            return
        y_offset = self.pointer_line - self.scrollable_content_region.height // 2
        scroll_distance = abs(y_offset - self.scroll_offset.y)
        self.scroll_to(
            y=y_offset,
            animate=animate and 100 > scroll_distance > 1,
            duration=0.2,
        )

    def watch_show_find(self, show_find: bool) -> None:
        self.clear_caches()
        if not show_find:
            self.pointer_line = None

    def watch_find(self, find: str) -> None:
        if not find:
            self.pointer_line = None

    def watch_case_sensitive(self) -> None:
        self.clear_caches()

    def watch_regex(self) -> None:
        self.clear_caches()

    def watch_pointer_line(
        self, old_pointer_line: int | None, pointer_line: int | None
    ) -> None:
        if old_pointer_line is not None:
            self.refresh_line(old_pointer_line)
        if pointer_line is not None:
            self.refresh_line(pointer_line)
        self.show_gutter = pointer_line is not None

    def action_select(self):
        if self.pointer_line is None:
            self.pointer_line = self.scroll_offset.y
        else:
            self.post_message(FindDialog.SelectLine())

    @on(ScanComplete)
    def on_scan_complete(self, event: ScanComplete) -> None:
        self._scanned_size = max(self._scanned_size, event.size)
        self._scan_start = event.scan_start
        self.update_line_count()
        self.refresh()

    def action_scroll_up(self) -> None:
        if self.pointer_line is None:
            super().action_scroll_up()
        else:
            self.advance_search(-1)

    def action_scroll_down(self) -> None:
        if self.pointer_line is None:
            super().action_scroll_down()
        else:
            self.advance_search(+1)

    def action_scroll_home(self) -> None:
        if self.pointer_line is not None:
            self.pointer_line = 0
        self.scroll_to(y=0, duration=0)

    def action_scroll_end(self) -> None:
        if self.pointer_line is not None:
            self.pointer_line = self.line_count
        if self.scroll_offset.y == self.max_scroll_y:
            pass
        else:
            self.scroll_to(y=self.max_scroll_y, duration=0)

    def action_page_down(self) -> None:
        if self.pointer_line is None:
            super().action_page_down()
        else:
            self.pointer_line = (
                self.pointer_line + self.scrollable_content_region.height
            )
            self.scroll_pointer_to_center()

    def action_page_up(self) -> None:
        if self.pointer_line is None:
            super().action_page_up()
        else:
            self.pointer_line = (
                self.pointer_line - self.scrollable_content_region.height
            )
            self.scroll_pointer_to_center()

    def on_click(self, event: events.Click) -> None:
        if self.loading:
            return
        new_pointer_line = event.y + self.scroll_offset.y - self.gutter.top
        if new_pointer_line == self.pointer_line:
            self.post_message(FindDialog.SelectLine())
        self.pointer_line = new_pointer_line

    def action_select(self):
        if self.pointer_line is None:
            self.pointer_line = self.scroll_offset.y
        else:
            self.post_message(FindDialog.SelectLine())