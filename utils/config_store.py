"""Application configuration persistence to ~/.mouse_automator/config.json"""
import json
import os
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    skip_help_on_startup: bool = False
    window_geometry: str = "720x780"
    window_x: int = -1
    window_y: int = -1
    opacity: float = 0.9
    topmost: bool = True


class ConfigStore:
    def __init__(self) -> None:
        self._dir: str = os.path.expanduser("~/.mouse_automator")
        self._file: str = os.path.join(self._dir, "config.json")
        os.makedirs(self._dir, exist_ok=True)
        self._config: AppConfig = self._load()

    def _load(self) -> AppConfig:
        if not os.path.exists(self._file):
            return AppConfig()
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                data = json.load(f)
            valid = {k: v for k, v in data.items() if k in AppConfig.__dataclass_fields__}
            return AppConfig(**valid)
        except (json.JSONDecodeError, TypeError):
            return AppConfig()

    def save(self) -> None:
        tmp = self._file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(asdict(self._config), f, indent=2, ensure_ascii=False)
        os.replace(tmp, self._file)

    @property
    def config(self) -> AppConfig:
        return self._config
