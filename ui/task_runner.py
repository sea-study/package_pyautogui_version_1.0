"""
任务执行引擎：在后台线程运行任务，并实现热退出（鼠标移至四角）监控。
v4: i18n 双语日志
"""
import time
import threading
from typing import Optional, Callable

import pyautogui

from ui.models import SingleTask, ComboTask
from utils.i18n import LocaleManager

SAFE_ZONE = 50
_locale = LocaleManager()


class TaskRunner:
    """负责任务执行、紧急停止的控制器。"""

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.on_state_change: Optional[Callable[[str], None]] = None
        self.on_log: Optional[Callable[[str], None]] = None
        self.on_task_complete: Optional[Callable[[str], None]] = None

    @property
    def is_running(self) -> bool:
        with self._lock:
            t = self._thread
        return t is not None and t.is_alive()

    def _log(self, message: str) -> None:
        if self.on_log:
            self.on_log(message)

    def run_single(self, task: SingleTask) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._execute_single, args=(task,), daemon=True
            )
            self._thread.start()
        self._notify("running")

    def run_combo(self, task: ComboTask) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._execute_combo, args=(task,), daemon=True
            )
            self._thread.start()
        self._notify("running")

    def stop(self) -> None:
        self._stop_event.set()

    # ── 执行逻辑 ──

    def _execute_single(self, task: SingleTask) -> None:
        tr = _locale.t
        self._log(tr("log.single_start", action=tr(f"action.{task.action}"),
                     x=str(task.x), y=str(task.y), repeat=str(task.repeat)))
        count = 0
        while not self._stop_event.is_set():
            if task.repeat != 0 and count >= task.repeat:
                break
            self._perform(task.action, task.x, task.y)
            count += 1
            self._log(tr("log.single_done", count=str(count)))
            self._safe_wait(0.5)
        status = "stopped" if self._stop_event.is_set() else "completed"
        self._log(tr("log.emergency") if status == "stopped" else tr("log.single_end"))
        if self.on_task_complete:
            self.on_task_complete(status)
        self._cleanup()

    def _execute_combo(self, task: ComboTask) -> None:
        tr = _locale.t
        self._log(tr("log.combo_start", steps=str(len(task.steps)), repeat=str(task.repeat)))
        iteration = 0
        while not self._stop_event.is_set():
            if task.repeat != 0 and iteration >= task.repeat:
                break
            self._log(tr("log.combo_round", round=str(iteration + 1)))
            for i, step in enumerate(task.steps):
                if self._stop_event.is_set():
                    break
                self._perform(step.action, step.x, step.y, step.scroll_amount,
                              step.drag_to_x, step.drag_to_y)
                self._log(tr("log.combo_step", idx=str(i + 1),
                             action=tr(f"action.{step.action}"),
                             x=str(step.x), y=str(step.y)))
                self._safe_wait(step.delay)
            iteration += 1
        status = "stopped" if self._stop_event.is_set() else "completed"
        self._log(tr("log.emergency") if status == "stopped" else tr("log.combo_end"))
        if self.on_task_complete:
            self.on_task_complete(status)
        self._cleanup()

    # ── 底层操作 ──

    def _perform(self, action: str, x: int, y: int, scroll_amount: int = 3,
                 drag_to_x: int = 0, drag_to_y: int = 0) -> None:
        pyautogui.moveTo(x, y, duration=0.1)
        if action == "left_click":
            pyautogui.click()
        elif action == "right_click":
            pyautogui.rightClick()
        elif action == "drag":
            pyautogui.dragTo(drag_to_x, drag_to_y, duration=0.5)
        elif action == "scroll_up":
            pyautogui.scroll(scroll_amount)
        elif action == "scroll_down":
            pyautogui.scroll(-scroll_amount)

    def _safe_wait(self, delay: float) -> None:
        elapsed = 0.0
        w, h = pyautogui.size()
        while elapsed < delay:
            if self._stop_event.is_set():
                return
            mx, my = pyautogui.position()
            if (mx <= SAFE_ZONE and my <= SAFE_ZONE) or \
               (mx >= w - SAFE_ZONE and my <= SAFE_ZONE):
                self._stop_event.set()
                return
            time.sleep(0.2)
            elapsed += 0.2

    def _cleanup(self) -> None:
        self._notify("stopped")

    def _notify(self, state: str) -> None:
        if self.on_state_change:
            self.on_state_change(state)
