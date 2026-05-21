"""
组合操作本地存储管理。
数据文件: ~/.mouse_automator/combos.json
"""
import json
import os
from dataclasses import asdict
from typing import Optional

from ui.models import ComboTask, Step

DATA_DIR = os.path.expanduser("~/.mouse_automator")
DATA_FILE = os.path.join(DATA_DIR, "combos.json")


class ComboStore:
    """管理已保存的组合任务列表。"""

    def __init__(self):
        self._combos: dict[str, ComboTask] = {}
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load()

    def _load(self):
        if not os.path.exists(DATA_FILE):
            self._combos = {}
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._combos = {}
            for name, data in raw.items():
                steps = [Step(**s) for s in data.get("steps", [])]
                self._combos[name] = ComboTask(steps=steps, repeat=data.get("repeat", 1))
        except (json.JSONDecodeError, TypeError, KeyError):
            self._combos = {}

    def _save(self):
        serialized = {}
        for name, combo in self._combos.items():
            serialized[name] = {
                "repeat": combo.repeat,
                "steps": [asdict(step) for step in combo.steps]
            }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

    def get_all_names(self) -> list[str]:
        return list(self._combos.keys())

    def get_combo(self, name: str) -> Optional[ComboTask]:
        return self._combos.get(name)

    def save_combo(self, name: str, combo: ComboTask):
        self._combos[name] = combo
        self._save()

    def rename_combo(self, old_name: str, new_name: str):
        if old_name not in self._combos or new_name == old_name:
            return
        self._combos[new_name] = self._combos.pop(old_name)
        self._save()

    def delete_combo(self, name: str):
        if name in self._combos:
            del self._combos[name]
            self._save()
