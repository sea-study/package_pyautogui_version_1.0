"""
共享数据模型与常量。
支持中英双语切换，LocaleManager 切换时自动刷新。
"""
from dataclasses import dataclass, field
from utils.i18n import LocaleManager

# ── 操作键（内部标识，不变）──
ACTION_KEYS = ("left_click", "right_click", "drag", "scroll_up", "scroll_down")

# ── 可刷新的显示映射 ──
ACTIONS = {}
REPEAT_PRESETS = {}

_locale = LocaleManager()


def _refresh_locale() -> None:
    """根据当前语言刷新 ACTIONS 和 REPEAT_PRESETS 的值。"""
    ACTIONS.clear()
    for key in ACTION_KEYS:
        ACTIONS[key] = _locale.t(f"action.{key}")

    REPEAT_PRESETS.clear()
    REPEAT_PRESETS[1] = _locale.t("repeat.1")
    REPEAT_PRESETS[5] = _locale.t("repeat.5")
    REPEAT_PRESETS[0] = _locale.t("repeat.0")
    REPEAT_PRESETS["custom"] = _locale.t("repeat.custom")


_refresh_locale()
_locale.on_change(_refresh_locale)

# ── 帮助步骤（从 i18n 读取）──
from utils.i18n import HELP_STRUCTURE


def get_help_steps() -> list[tuple[str, list[str]]]:
    """返回当前语言的帮助步骤列表。"""
    result = []
    for title_key, item_keys in HELP_STRUCTURE:
        result.append((_locale.t(title_key), [_locale.t(k) for k in item_keys]))
    return result


@dataclass
class Step:
    """组合任务的一个步骤。"""
    x: int
    y: int
    action: str = "left_click"
    delay: float = 0.5
    scroll_amount: int = 3
    drag_to_x: int = 0
    drag_to_y: int = 0


@dataclass
class ComboTask:
    """组合任务：多个步骤按序执行，整体循环 repeat 次。"""
    steps: list[Step] = field(default_factory=list)
    repeat: int = 1


@dataclass
class SingleTask:
    """单一操作任务。"""
    x: int = 0
    y: int = 0
    action: str = "left_click"
    repeat: int = 1
