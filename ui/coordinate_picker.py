"""
坐标拾取模块：通过全局热键 F6 捕获鼠标当前坐标。
v2: 监听器启动失败优雅降级
"""
import queue
import threading
from typing import Optional, Tuple

import pyautogui
from pynput import keyboard


class CoordinatePicker:
    """监听 F6 键，将当前鼠标位置放入队列，供 UI 线程读取。"""

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue()
        self._listener: Optional[keyboard.Listener] = None
        self._running: bool = False
        self._failed: bool = False

    @property
    def is_healthy(self) -> bool:
        return not self._failed

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        try:
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.daemon = True
            self._listener.start()
        except Exception:
            self._running = False
            self._failed = True

    def stop(self) -> None:
        self._running = False
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def get_coordinates(self) -> Optional[Tuple[int, int]]:
        try:
            x, y = self._queue.get_nowait()
            return x, y
        except queue.Empty:
            return None

    def _on_press(self, key) -> None:
        try:
            if key == keyboard.Key.f6:
                x, y = pyautogui.position()
                self._queue.put((x, y))
        except Exception:
            pass
