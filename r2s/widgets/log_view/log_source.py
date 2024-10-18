from abc import ABC, abstractmethod

import mmap
import os
from pathlib import Path
import time

from threading import Event, Lock
from typing import IO, List

import rich.repr


@rich.repr.auto(angular=True)
class LogSourceBase(ABC):
    def __init__(self) -> None:
        self.can_tail: bool = True

    @abstractmethod
    def open(self, exit_event: Event) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def num_lines(self) -> int:
        pass

    @abstractmethod
    def get_line(self, line_number: int) -> str:
        pass


@rich.repr.auto(angular=True)
class LogFileSource(LogSourceBase):
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.name = self.path.name
        self.file: IO[bytes] | None = None
        self.size = 0
        self.lines: List[str] = []
        self._lock = Lock()

    @property
    def fileno(self) -> int:
        assert self.file is not None
        return self.file.fileno()

    @property
    def is_open(self) -> bool:
        return self.file is not None

    def open(self, exit_event: Event) -> bool:
        self.file = open(self.path, "rb", buffering = 0)
        self.can_tail = True
        return True

    def close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None

    def scan(self) -> int:
        self.file.seek(0, os.SEEK_END)
        self.new_size = self.file.tell()

        if self.new_size == self.size:
            return 0

        self.file.seek(self.size)
        new_data = self.file.read(self.new_size - self.size)
        new_data = new_data.decode("utf-8")
        new_lines = new_data.splitlines()
        with self._lock:
            self.size = self.new_size
            self.lines.extend(new_lines)
        return len(new_lines)

    def num_lines(self) -> int:
        with self._lock:
            return len(self.lines)

    def get_line(self, line_number: int) -> str:
        with self._lock:
            return self.lines[line_number]