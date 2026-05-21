"""
主应用窗口：整合坐标拾取、任务编辑、任务执行。
v8: 中英双语切换
"""
import os
import sys
import time
import tkinter as tk
from tkinter import scrolledtext, ttk

from ui.coordinate_picker import CoordinatePicker
from ui.task_editor import SingleTaskFrame, ComboTaskFrame
from ui.task_runner import TaskRunner
from ui.theme import apply_theme, COLORS, LIGHT_SUB, LIGHT_WARNING, STATUS_TIMEOUT_MS
from ui.popups import HelpWindow, FirstRunHelpWindow, AuthorWindow
from utils.background import BackgroundTiler
from utils.config_store import ConfigStore
from utils.history_store import HistoryStore, HistoryEntry
from utils.i18n import LocaleManager


def _resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)  # type: ignore[attr-defined]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


BG_IMAGE_PATH = _resource_path("pixel_bg.png")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self._locale = LocaleManager()
        self.tr = self._locale.t

        self._config_store = ConfigStore()
        cfg = self._config_store.config

        self.title(self.tr("app.title"))
        if cfg.window_x >= 0 and cfg.window_y >= 0:
            self.geometry(f"{cfg.window_geometry}+{cfg.window_x}+{cfg.window_y}")
        else:
            self.geometry(cfg.window_geometry)
        self.minsize(560, 600)
        self.attributes('-alpha', cfg.opacity)

        self.topmost_var = tk.BooleanVar(value=cfg.topmost)
        self.attributes('-topmost', cfg.topmost)

        self._bg_tiler = BackgroundTiler(BG_IMAGE_PATH)

        self.picker = CoordinatePicker()
        self.runner = TaskRunner()
        self.runner.on_state_change = self._on_runner_state_change
        self.runner.on_log = self._append_log
        self.runner.on_task_complete = self._on_task_complete

        self._history_store = HistoryStore()
        self._task_start_time: float = 0.0
        self._current_task_type: str = ""
        self._current_task_action: str = ""
        self._current_task_steps: int = 0
        self._current_task_repeat: int = 0

        self.current_x = tk.IntVar(value=0)
        self.current_y = tk.IntVar(value=0)
        self.mode_var = tk.StringVar(value="combo")
        self.status_var = tk.StringVar(value=self.tr("status.ready"))
        self._opacity_var = tk.DoubleVar(value=cfg.opacity)

        apply_theme(self)

        # i18n 刷新列表: (widget, configure_kwargs_builder)
        self._i18n_items: list = []
        self._i18n_stringvars: list[tuple[tk.StringVar, str]] = []

        self._build_ui()
        self.picker.start()

        if not self.picker.is_healthy:
            self.status_var.set(self.tr("status.f6_failed"))

        self._poll_coordinates()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<Control-Return>", lambda _e: self._start_task())
        self.bind("<Escape>", lambda _e: self._stop_task())

        # 语言切换回调
        self._locale.on_change(self._on_lang_change)

        if not cfg.skip_help_on_startup:
            self.after(300, self._show_help_on_first_run)

    # ── i18n 工具 ──

    def _i18n_label(self, widget, key: str, **kwargs) -> None:
        """标记一个 widget 需要语言刷新，设置初始文本。"""
        def _updater(w=widget, k=key, kw=kwargs):
            w.configure(text=self.tr(k, **kw))
        self._i18n_items.append(_updater)

    def _i18n_sv(self, sv: tk.StringVar, key: str, **kwargs) -> None:
        """注册一个 StringVar，语言切换时自动更新。"""
        self._i18n_stringvars.append((sv, key))

    def _on_lang_change(self) -> None:
        """语言切换时刷新所有 UI 文本。"""
        self.title(self.tr("app.title"))
        for updater in self._i18n_items:
            updater()
        for sv, key in self._i18n_stringvars:
            sv.set(self.tr(key))
        # 刷新 Notebook 标签
        self._notebook.tab(self._tab_edit, text=self.tr("tab.edit"))
        self._notebook.tab(self._tab_history, text=self.tr("tab.history"))
        self._notebook.tab(self._tab_log, text=self.tr("tab.log"))
        self._notebook.tab(self._tab_help, text=self.tr("tab.help"))
        self._notebook.tab(self._tab_author, text=self.tr("tab.author"))
        self._refresh_history_tab()

    # ── UI 构建 ──

    def _build_ui(self) -> None:
        # 背景图层
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        if self._bg_tiler.image:
            self.bg_label.configure(image=self._bg_tiler.image)

        # 主容器
        self.main_frame = tk.Frame(self, bg=COLORS["bg"])
        self.main_frame.pack(fill="both", expand=True)

        # 坐标拾取行
        coord = ttk.LabelFrame(self.main_frame)
        coord.pack(fill="x", padx=12, pady=(12, 6))
        self._i18n_label(coord, "coord.frame", **{"text": ""})  # LabelFrame text via configure

        for col in range(6):
            coord.columnconfigure(col, weight=1)

        x_lbl = ttk.Label(coord, text=self.tr("coord.x"))
        x_lbl.grid(row=0, column=0, padx=(5, 2), pady=4, sticky="e")
        self._i18n_label(x_lbl, "coord.x")

        ttk.Entry(coord, textvariable=self.current_x).grid(row=0, column=1, padx=2, sticky="ew")

        y_lbl = ttk.Label(coord, text=self.tr("coord.y"))
        y_lbl.grid(row=0, column=2, padx=(8, 2), sticky="e")
        self._i18n_label(y_lbl, "coord.y")

        ttk.Entry(coord, textvariable=self.current_y).grid(row=0, column=3, padx=2, sticky="ew")

        pick_btn = ttk.Button(coord, text=self.tr("coord.pick"), command=self._pick_coordinate)
        pick_btn.grid(row=0, column=4, padx=4, sticky="ew")
        self._i18n_label(pick_btn, "coord.pick")

        add_btn = ttk.Button(coord, text=self.tr("coord.add_step"), command=self._quick_add_step)
        add_btn.grid(row=0, column=5, padx=4, sticky="ew")
        self._i18n_label(add_btn, "coord.add_step")

        # Notebook
        self._notebook = notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True, padx=12, pady=(8, 4))
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._tab_edit = edit_tab = ttk.Frame(notebook)
        notebook.add(edit_tab, text=self.tr("tab.edit"))
        self._build_edit_tab(edit_tab)

        self._tab_history = history_tab = ttk.Frame(notebook)
        notebook.add(history_tab, text=self.tr("tab.history"))
        self._build_history_tab(history_tab)

        self._tab_log = log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text=self.tr("tab.log"))
        self.log_text = scrolledtext.ScrolledText(
            log_tab, bg=COLORS["card"], fg=COLORS["fg"], insertbackground=COLORS["fg"],
            borderwidth=0, wrap=tk.WORD, state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)
        self._write_log(self.tr("log.ready") + "\n")

        self._tab_help = help_tab = ttk.Frame(notebook)
        notebook.add(help_tab, text=self.tr("tab.help"))

        self._tab_author = author_tab = ttk.Frame(notebook)
        notebook.add(author_tab, text=self.tr("tab.author"))

        # 按钮行
        btns = ttk.Frame(self.main_frame)
        btns.pack(fill="x", padx=12, pady=(8, 4))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=0)
        self.start_btn = ttk.Button(btns, text=self.tr("btn.start"), command=self._start_task)
        self.start_btn.grid(row=0, column=0, padx=4, sticky="ew")
        self._i18n_label(self.start_btn, "btn.start")

        self.stop_btn = ttk.Button(btns, text=self.tr("btn.stop"), command=self._stop_task,
                                   style="Danger.TButton", state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=4, sticky="ew")
        self._i18n_label(self.stop_btn, "btn.stop")

        topmost_cb = ttk.Checkbutton(btns, text=self.tr("btn.topmost"),
                                     variable=self.topmost_var, command=self._toggle_topmost)
        topmost_cb.grid(row=0, column=2, padx=10, sticky="e")
        self._i18n_label(topmost_cb, "btn.topmost")

        # 语言切换按钮
        lang_btn = tk.Button(btns, text=self.tr("btn.lang"),
                             font=("Microsoft YaHei", 8, "bold"),
                             fg="white", bg=COLORS["accent"],
                             activebackground=COLORS["accent_hover"],
                             activeforeground="white", relief="flat",
                             padx=8, cursor="hand2",
                             command=self._locale.toggle)
        lang_btn.grid(row=0, column=3, padx=(4, 0))
        self._i18n_label(lang_btn, "btn.lang")

        # 状态栏
        status = ttk.Frame(self.main_frame)
        status.pack(fill="x", padx=12, pady=(0, 2))
        status_label = ttk.Label(status, textvariable=self.status_var, foreground=LIGHT_SUB)
        status_label.pack(side="left")
        self._i18n_sv(self.status_var, "status.ready")  # 基础状态词

        opacity_frame = ttk.Frame(status)
        opacity_frame.pack(side="right")
        opacity_label = ttk.Label(opacity_frame, text=self.tr("opacity.label"), foreground=LIGHT_SUB)
        opacity_label.pack(side="left", padx=2)
        self._i18n_label(opacity_label, "opacity.label")
        ttk.Scale(opacity_frame, from_=0.3, to=1.0, variable=self._opacity_var,
                  orient="horizontal", length=80, command=self._on_opacity_change).pack(side="left", padx=2)

        self._warn_label = ttk.Label(self.main_frame, text=self.tr("warn.emergency"),
                                     foreground=LIGHT_WARNING)
        self._warn_label.pack(pady=(0, 8))
        self._i18n_label(self._warn_label, "warn.emergency")

    def _build_edit_tab(self, parent: tk.Frame) -> None:
        mode = ttk.Frame(parent)
        mode.pack(fill="x", padx=0, pady=(4, 6))

        single_rb = ttk.Radiobutton(mode, text=self.tr("mode.single"), variable=self.mode_var,
                                    value="single", command=self._toggle_mode)
        single_rb.pack(side="left", padx=10)
        self._i18n_label(single_rb, "mode.single")

        combo_rb = ttk.Radiobutton(mode, text=self.tr("mode.combo"), variable=self.mode_var,
                                   value="combo", command=self._toggle_mode)
        combo_rb.pack(side="left", padx=10)
        self._i18n_label(combo_rb, "mode.combo")

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)
        self.single_frame = SingleTaskFrame(container)
        self.combo_frame = ComboTaskFrame(
            container,
            get_current_coordinates=lambda: (self.current_x.get(), self.current_y.get())
        )
        self.combo_frame.pack(fill="both", expand=True)

    def _build_history_tab(self, parent: tk.Frame) -> None:
        columns = ("time", "type", "action", "steps", "repeat", "status", "duration")
        self._history_tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        self._history_tree.heading("time", text=self.tr("history.time"))
        self._history_tree.heading("type", text=self.tr("history.type"))
        self._history_tree.heading("action", text=self.tr("history.action"))
        self._history_tree.heading("steps", text=self.tr("history.steps"))
        self._history_tree.heading("repeat", text=self.tr("history.repeat"))
        self._history_tree.heading("status", text=self.tr("history.status"))
        self._history_tree.heading("duration", text=self.tr("history.duration"))
        self._history_tree.column("time", width=130, anchor="center")
        self._history_tree.column("type", width=50, anchor="center")
        self._history_tree.column("action", width=100, anchor="center")
        self._history_tree.column("steps", width=50, anchor="center")
        self._history_tree.column("repeat", width=50, anchor="center")
        self._history_tree.column("status", width=60, anchor="center")
        self._history_tree.column("duration", width=60, anchor="center")
        self._history_tree.pack(fill="both", expand=True, padx=2, pady=2)

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", padx=2, pady=2)
        clear_btn = ttk.Button(btn_row, text=self.tr("history.clear"), command=self._clear_history)
        clear_btn.pack(side="right")
        self._i18n_label(clear_btn, "history.clear")

        self._refresh_history_tab()

    def _refresh_history_tab(self) -> None:
        for row in self._history_tree.get_children():
            self._history_tree.delete(row)
        for entry in self._history_store.get_entries():
            task_type_display = self.tr("history.type_single") if entry.task_type == "single" else self.tr("history.type_combo")
            status_display = self.tr("history.completed") if entry.status == "completed" else self.tr("history.stopped")
            self._history_tree.insert("", "end", values=(
                entry.timestamp, task_type_display, entry.action,
                entry.steps_count, entry.repeat, status_display, entry.duration_seconds
            ))
        # 更新表头
        self._history_tree.heading("time", text=self.tr("history.time"))
        self._history_tree.heading("type", text=self.tr("history.type"))
        self._history_tree.heading("action", text=self.tr("history.action"))
        self._history_tree.heading("steps", text=self.tr("history.steps"))
        self._history_tree.heading("repeat", text=self.tr("history.repeat"))
        self._history_tree.heading("status", text=self.tr("history.status"))
        self._history_tree.heading("duration", text=self.tr("history.duration"))

    def _clear_history(self) -> None:
        self._history_store.clear()
        self._refresh_history_tab()

    # ── 标签页切换 ──

    def _on_tab_changed(self, event) -> None:
        notebook = event.widget
        current = notebook.index("current")
        if current == 3:
            notebook.select(0)
            self._show_help_window()
        elif current == 4:
            notebook.select(0)
            self._show_author_window()

    # ── 弹窗 ──

    def _show_help_window(self) -> None:
        HelpWindow(self, self._bg_tiler)

    def _show_author_window(self) -> None:
        AuthorWindow(self, self._bg_tiler)

    def _show_help_on_first_run(self) -> None:
        def on_dismiss(skip: bool) -> None:
            if skip:
                self._config_store.config.skip_help_on_startup = True
                self._config_store.save()

        FirstRunHelpWindow(self, self._bg_tiler, on_dismiss)

    # ── 日志 ──

    def _append_log(self, message: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.after(0, self._write_log, f"[{ts}] {message}\n")

    def _write_log(self, line: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ── 置顶 / 模式 / 透明度 ──

    def _toggle_topmost(self) -> None:
        self.attributes('-topmost', self.topmost_var.get())

    def _toggle_mode(self) -> None:
        if self.mode_var.get() == "single":
            self.combo_frame.pack_forget()
            self.single_frame.pack(fill="both", expand=True)
        else:
            self.single_frame.pack_forget()
            self.combo_frame.pack(fill="both", expand=True)

    def _on_opacity_change(self, *_args) -> None:
        self.attributes('-alpha', self._opacity_var.get())

    # ── 坐标 ──

    def _quick_add_step(self) -> None:
        x, y = self.current_x.get(), self.current_y.get()
        if x == 0 and y == 0:
            self.status_var.set(self.tr("status.no_coord"))
            self.after(STATUS_TIMEOUT_MS, lambda: self.status_var.set(self.tr("status.ready")))
            return
        if self.mode_var.get() != "combo":
            self.mode_var.set("combo")
            self._toggle_mode()
        self.combo_frame.quick_add_step(x, y)

    def _pick_coordinate(self) -> None:
        self.status_var.set(self.tr("status.pick_hint"))
        self.after(STATUS_TIMEOUT_MS, lambda: self.status_var.set(self.tr("status.ready"))
                   if self.status_var.get() == self.tr("status.pick_hint") else None)

    def _poll_coordinates(self) -> None:
        try:
            coords = self.picker.get_coordinates()
            if coords:
                x, y = coords
                self.current_x.set(x)
                self.current_y.set(y)
                self.status_var.set(f"{self.tr('status.captured')} ({x}, {y})")
                self.after(STATUS_TIMEOUT_MS, lambda: self.status_var.set(self.tr("status.ready")))
        finally:
            self.after(100, self._poll_coordinates)

    # ── 任务执行 ──

    def _start_task(self) -> None:
        if self.runner.is_running:
            return
        self._task_start_time = time.time()
        if self.mode_var.get() == "single":
            task = self.single_frame.apply_to_task(self.current_x.get(), self.current_y.get())
            self._current_task_type = "single"
            self._current_task_action = self.tr(f"action.{task.action}")
            self._current_task_steps = 1
            self._current_task_repeat = task.repeat
            self.runner.run_single(task)
        else:
            task = self.combo_frame.get_task()
            self._current_task_type = "combo"
            self._current_task_action = f"{len(task.steps)}{self.tr('task.lines')}"
            self._current_task_steps = len(task.steps)
            self._current_task_repeat = task.repeat
            self.runner.run_combo(task)

    def _stop_task(self) -> None:
        self.runner.stop()

    def _on_runner_state_change(self, state: str) -> None:
        if state == "running":
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_var.set(self.tr("status.running"))
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_var.set(self.tr("status.ready"))

    def _on_task_complete(self, status: str) -> None:
        duration = round(time.time() - self._task_start_time, 1)
        self._history_store.add_entry(HistoryEntry(
            task_type=self._current_task_type,
            action=self._current_task_action,
            steps_count=self._current_task_steps,
            repeat=self._current_task_repeat,
            status=status,
            duration_seconds=duration,
        ))
        self.after(0, self._refresh_history_tab)

    # ── 关闭 ──

    def _on_close(self) -> None:
        cfg = self._config_store.config
        try:
            parts = self.geometry().split('+')
            cfg.window_geometry = parts[0]
            cfg.window_x = int(parts[1])
            cfg.window_y = int(parts[2])
        except (IndexError, ValueError):
            cfg.window_geometry = self.geometry().split('+')[0]
        cfg.opacity = self.attributes('-alpha')
        cfg.topmost = self.topmost_var.get()
        self._config_store.save()

        self.picker.stop()
        if self.runner.is_running:
            self.runner.stop()
        self.destroy()


def run() -> None:
    App().mainloop()
