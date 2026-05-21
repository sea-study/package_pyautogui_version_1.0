"""Execution history persistence to ~/.mouse_automator/history.json"""
import json
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class HistoryEntry:
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    task_type: str = ""
    action: str = ""
    steps_count: int = 0
    repeat: int = 1
    status: str = ""
    duration_seconds: float = 0.0


class HistoryStore:
    MAX_ENTRIES: int = 50

    def __init__(self) -> None:
        self._dir: str = os.path.expanduser("~/.mouse_automator")
        self._file: str = os.path.join(self._dir, "history.json")
        os.makedirs(self._dir, exist_ok=True)
        self._entries: list[HistoryEntry] = self._load()

    def _load(self) -> list[HistoryEntry]:
        if not os.path.exists(self._file):
            return []
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [HistoryEntry(**e) for e in raw]
        except (json.JSONDecodeError, TypeError):
            return []

    def _save(self) -> None:
        tmp = self._file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self._entries], f, indent=2, ensure_ascii=False)
        os.replace(tmp, self._file)

    def add_entry(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries = self._entries[:self.MAX_ENTRIES]
        self._save()

    def get_entries(self) -> list[HistoryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._save()
