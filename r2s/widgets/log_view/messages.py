from __future__ import annotations
from dataclasses import dataclass

import rich.repr
from textual.message import Message

from r2s.widgets.log_view.log_source import LogSourceBase



@rich.repr.auto
@dataclass
class NewBreaks(Message):
    """New line break to add."""

    log_source: LogSourceBase
    breaks: list[int]
    scanned_size: int = 0
    tail: bool = False

    def __rich_repr__(self) -> rich.repr.Result:
        yield "scanned_size", self.scanned_size
        yield "tail", self.tail


@dataclass
class ScanComplete(Message):
    """Scan has completed."""

    size: int
    scan_start: int


@dataclass
class PointerMoved(Message):
    """Pointer has moved."""

    pointer_line: int | None

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, PointerMoved)