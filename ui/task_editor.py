"""
任务编辑 UI：单一操作 / 组合操作的配置面板。
v6: i18n 双语支持
"""
from typing import Callable, Optional

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from ui.models import ACTIONS, REPEAT_PRESETS, Step, ComboTask, SingleTask
from utils.combo_store import ComboStore
from utils.i18n import LocaleManager

_locale = LocaleManager()


class SingleTaskFrame(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.task = SingleTask()
        self._repeat_reverse = {v: k for k, v in REPEAT_PRESETS.items()}

        self._i18n_items: list = []

        self._info_label = ttk.Label(self)
        self._info_label.grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self._i18n_items.append(lambda: self._info_label.configure(text=_locale.t("task.action")))
        self._info_label.configure(text=_locale.t("task.action"))

        self.action_var = tk.StringVar(value="left_click")
        self._action_menu = ttk.OptionMenu(
            self, self.action_var, "left_click",
            *ACTIONS.keys(), command=self._on_action_change
        )
        self._action_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        self._repeat_label = ttk.Label(self)
        self._repeat_label.grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self._i18n_items.append(lambda: self._repeat_label.configure(text=_locale.t("task.repeat")))
        self._repeat_label.configure(text=_locale.t("task.repeat"))

        self.repeat_var = tk.StringVar(value=REPEAT_PRESETS[1])
        self._repeat_menu = ttk.OptionMenu(
            self, self.repeat_var, REPEAT_PRESETS[1],
            *REPEAT_PRESETS.values(), command=self._on_repeat_preset
        )
        self._repeat_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        self.custom_entry = ttk.Entry(self, width=8)
        self.custom_entry.insert(0, "1")
        self.custom_entry.grid(row=1, column=2, padx=5, pady=4)
        self.custom_entry.configure(state="disabled")

        self.configure(text=_locale.t("task.single_frame"))

        def _refresh_single():
            self.configure(text=_locale.t("task.single_frame"))
            for fn in self._i18n_items:
                fn()
            # 刷新 OptionMenu 选项文本
            self._refresh_option_menus()

        _locale.on_change(_refresh_single)

    def _refresh_option_menus(self):
        """重建 OptionMenu 选项以反映语言切换。"""
        current_action = self.action_var.get()
        current_repeat = self.repeat_var.get()
        # 重建 action menu
        menu = self._action_menu["menu"]
        menu.delete(0, "end")
        for key in ACTIONS:
            menu.add_command(label=ACTIONS[key],
                           command=tk._setit(self.action_var, key, self._on_action_change))
        # 重建 repeat menu
        menu = self._repeat_menu["menu"]
        menu.delete(0, "end")
        for val in REPEAT_PRESETS.values():
            menu.add_command(label=val,
                           command=tk._setit(self.repeat_var, val, self._on_repeat_preset))
        # 恢复选中项
        self.action_var.set(current_action)
        self.repeat_var.set(current_repeat)

    def _on_action_change(self, value):
        self.task.action = value

    def _on_repeat_preset(self, choice):
        self.custom_entry.configure(state="normal" if choice == _locale.t("task.custom") else "disabled")

    def apply_to_task(self, x: int, y: int) -> SingleTask:
        self.task.x = x
        self.task.y = y
        self.task.action = self.action_var.get()
        preset = self.repeat_var.get()
        if preset == _locale.t("task.custom"):
            try:
                self.task.repeat = int(self.custom_entry.get())
            except ValueError:
                self.task.repeat = 1
        else:
            self.task.repeat = self._repeat_reverse.get(preset, 1)
        return self.task


class ComboTaskFrame(ttk.LabelFrame):
    def __init__(self, parent, get_current_coordinates: Optional[Callable[[], tuple[int, int]]] = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.get_current_coordinates = get_current_coordinates
        self.steps: list[Step] = []
        self.store = ComboStore()
        self._drag_item: Optional[str] = None
        self._drag_idx: int = -1
        self._i18n_items: list = []

        tr = _locale.t
        self.configure(text=tr("task.combo_frame"))

        columns = ("#", "x", "y", "action", "delay")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6, selectmode="browse")
        self.tree.heading("#", text=tr("tree.seq"))
        self.tree.heading("x", text=tr("tree.x"))
        self.tree.heading("y", text=tr("tree.y"))
        self.tree.heading("action", text=tr("tree.action"))
        self.tree.heading("delay", text=tr("tree.delay"))
        self.tree.column("#", width=40, anchor="center")
        self.tree.column("x", width=60, anchor="center")
        self.tree.column("y", width=60, anchor="center")
        self.tree.column("action", width=80, anchor="center")
        self.tree.column("delay", width=70, anchor="center")
        self.tree.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=4)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)

        self.tree.tag_configure("drag_target", background="#DBEAFE")

        btn_row = ttk.Frame(self)
        btn_row.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
        self.add_btn = ttk.Button(btn_row, text=tr("task.add_btn"), command=self.open_add_step_form)
        self.add_btn.pack(side="left", padx=2)
        self._i18n_items.append(lambda: self.add_btn.configure(text=tr("task.add_btn")))

        self.delete_btn = ttk.Button(btn_row, text=tr("task.del_btn"), command=self.delete_selected_step)
        self.delete_btn.pack(side="left", padx=6)
        self._i18n_items.append(lambda: self.delete_btn.configure(text=tr("task.del_btn")))

        saved_row = ttk.Frame(self)
        saved_row.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=4)
        self._saved_label = ttk.Label(saved_row, text=tr("task.saved"))
        self._saved_label.pack(side="left", padx=2)
        self._i18n_items.append(lambda: self._saved_label.configure(text=tr("task.saved")))

        self.saved_combo_var = tk.StringVar()
        self.saved_combo_cb = ttk.Combobox(saved_row, textvariable=self.saved_combo_var,
                                           state="readonly", width=15)
        self.saved_combo_cb.pack(side="left", padx=2)

        btn_texts = [("task.load", self._load_selected_combo),
                     ("task.save", self._save_current_combo),
                     ("task.rename", self._rename_selected_combo),
                     ("task.delete", self._delete_selected_combo)]
        self._saved_btns: list[tuple[ttk.Button, str]] = []
        for key, cmd in btn_texts:
            btn = ttk.Button(saved_row, text=tr(key), command=cmd)
            btn.pack(side="left", padx=2)
            self._saved_btns.append((btn, key))

        self._refresh_saved_list()

        loop_row = ttk.Frame(self)
        loop_row.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=4)
        self._loop_label = ttk.Label(loop_row, text=tr("task.loop"))
        self._loop_label.pack(side="left", padx=2)
        self._i18n_items.append(lambda: self._loop_label.configure(text=tr("task.loop")))

        self.repeat_entry = ttk.Entry(loop_row, width=8)
        self.repeat_entry.insert(0, "1")
        self.repeat_entry.pack(side="left", padx=2)

        self._loop_hint = ttk.Label(loop_row, text=tr("task.loop_hint"))
        self._loop_hint.pack(side="left", padx=2)
        self._i18n_items.append(lambda: self._loop_hint.configure(text=tr("task.loop_hint")))

        self.add_form_frame = ttk.Frame(self)
        self.add_form_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=4)
        self.add_form_frame.grid_remove()

        self._form_x_label = ttk.Label(self.add_form_frame, text=tr("coord.x"))
        self._form_x_label.grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.form_x_var = tk.StringVar()
        self.form_x_entry = ttk.Entry(self.add_form_frame, textvariable=self.form_x_var, width=10)
        self.form_x_entry.grid(row=0, column=1, padx=2)

        self._form_y_label = ttk.Label(self.add_form_frame, text=tr("coord.y"))
        self._form_y_label.grid(row=0, column=2, padx=2, pady=2, sticky="e")
        self.form_y_var = tk.StringVar()
        self.form_y_entry = ttk.Entry(self.add_form_frame, textvariable=self.form_y_var, width=10)
        self.form_y_entry.grid(row=0, column=3, padx=2)

        self._form_action_label = ttk.Label(self.add_form_frame, text=tr("task.action"))
        self._form_action_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.form_action_var = tk.StringVar(value="left_click")
        self._form_action_menu = ttk.OptionMenu(self.add_form_frame, self.form_action_var, "left_click",
                                                *ACTIONS.keys(), command=self._on_form_action_change)
        self._form_action_menu.grid(row=1, column=1, columnspan=2, sticky="ew", padx=2)

        self._form_delay_label = ttk.Label(self.add_form_frame, text=tr("task.delay"))
        self._form_delay_label.grid(row=1, column=3, padx=2, pady=2, sticky="e")
        self.form_delay_entry = ttk.Entry(self.add_form_frame, width=10)
        self.form_delay_entry.insert(0, "0.5")
        self.form_delay_entry.grid(row=1, column=4, padx=2)

        # 滚动量行
        self.scroll_row_frame = ttk.Frame(self.add_form_frame)
        self.scroll_row_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=2, pady=2)
        self.scroll_row_frame.grid_remove()
        self._scroll_label = ttk.Label(self.scroll_row_frame, text=tr("task.scroll_amt"))
        self._scroll_label.pack(side="left", padx=2)
        self.form_scroll_var = tk.StringVar(value="3")
        ttk.Entry(self.scroll_row_frame, textvariable=self.form_scroll_var, width=6).pack(side="left", padx=2)
        self._scroll_unit = ttk.Label(self.scroll_row_frame, text=tr("task.lines"))
        self._scroll_unit.pack(side="left")
        scroll_tip = ttk.Label(self.scroll_row_frame, text="[?]", foreground="blue", cursor="hand2")
        scroll_tip.pack(side="left", padx=2)
        scroll_tip.bind("<Enter>", self._show_scroll_tooltip)
        scroll_tip.bind("<Leave>", self._hide_scroll_tooltip)

        # 拖拽终点行
        self.drag_row_frame = ttk.Frame(self.add_form_frame)
        self.drag_row_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=2, pady=2)
        self.drag_row_frame.grid_remove()
        self._drag_x_label = ttk.Label(self.drag_row_frame, text=tr("task.drag_x"))
        self._drag_x_label.pack(side="left", padx=2)
        self.form_drag_x_var = tk.StringVar(value="")
        ttk.Entry(self.drag_row_frame, textvariable=self.form_drag_x_var, width=8).pack(side="left", padx=2)
        self._drag_y_label = ttk.Label(self.drag_row_frame, text=tr("task.drag_y"))
        self._drag_y_label.pack(side="left", padx=(8, 2))
        self.form_drag_y_var = tk.StringVar(value="")
        ttk.Entry(self.drag_row_frame, textvariable=self.form_drag_y_var, width=8).pack(side="left", padx=2)

        form_btn_row = ttk.Frame(self.add_form_frame)
        form_btn_row.grid(row=3, column=0, columnspan=5, pady=(6, 0))
        self._confirm_btn = ttk.Button(form_btn_row, text=tr("task.confirm"), command=self._confirm_add_step)
        self._confirm_btn.pack(side="left", padx=4)
        self._cancel_btn = ttk.Button(form_btn_row, text=tr("task.cancel"), command=self._cancel_add_step)
        self._cancel_btn.pack(side="left", padx=4)

        # 注册语言切换回调
        def _refresh():
            self.configure(text=tr("task.combo_frame"))
            self.tree.heading("#", text=tr("tree.seq"))
            self.tree.heading("x", text=tr("tree.x"))
            self.tree.heading("y", text=tr("tree.y"))
            self.tree.heading("action", text=tr("tree.action"))
            self.tree.heading("delay", text=tr("tree.delay"))
            for fn in self._i18n_items:
                fn()
            for btn, key in self._saved_btns:
                btn.configure(text=tr(key))
            self._form_x_label.configure(text=tr("coord.x"))
            self._form_y_label.configure(text=tr("coord.y"))
            self._form_action_label.configure(text=tr("task.action"))
            self._form_delay_label.configure(text=tr("task.delay"))
            self._scroll_label.configure(text=tr("task.scroll_amt"))
            self._scroll_unit.configure(text=tr("task.lines"))
            self._drag_x_label.configure(text=tr("task.drag_x"))
            self._drag_y_label.configure(text=tr("task.drag_y"))
            self._refresh_form_action_menu()
            self._confirm_btn.configure(text=tr("task.confirm"))
            self._cancel_btn.configure(text=tr("task.cancel"))
            self._refresh_tree()

        _locale.on_change(_refresh)

    def _refresh_form_action_menu(self):
        """重建表单的 OptionMenu 选项。"""
        menu = self._form_action_menu["menu"]
        menu.delete(0, "end")
        for key in ACTIONS:
            menu.add_command(label=ACTIONS[key],
                           command=tk._setit(self.form_action_var, key, self._on_form_action_change))

    # ── 保存/加载 ──

    def _refresh_saved_list(self):
        names = self.store.get_all_names()
        self.saved_combo_cb["values"] = names
        self.saved_combo_var.set(names[0] if names else "")

    def _load_selected_combo(self):
        name = self.saved_combo_var.get()
        if not name:
            messagebox.showwarning(_locale.t("dlg.select_combo"), _locale.t("dlg.select_combo"), parent=self)
            return
        combo = self.store.get_combo(name)
        if combo is None:
            return
        self.steps = combo.steps.copy()
        self.repeat_entry.delete(0, "end")
        self.repeat_entry.insert(0, str(combo.repeat))
        self._refresh_tree()

    def _save_current_combo(self):
        if not self.steps:
            messagebox.showwarning(_locale.t("dlg.no_steps"), _locale.t("dlg.no_steps"), parent=self)
            return
        name = simpledialog.askstring(_locale.t("dlg.save_title"), _locale.t("dlg.save_prompt"), parent=self)
        if not name:
            return
        if name in self.store.get_all_names():
            msg = _locale.t("dlg.overwrite_msg", name=name)
            if not messagebox.askyesno(_locale.t("dlg.overwrite_title"), msg, parent=self):
                return
        self.store.save_combo(name, self.get_task())
        self._refresh_saved_list()
        self.saved_combo_var.set(name)

    def _rename_selected_combo(self):
        old_name = self.saved_combo_var.get()
        if not old_name:
            return
        new_name = simpledialog.askstring(_locale.t("dlg.rename_title"), _locale.t("dlg.rename_prompt"),
                                          initialvalue=old_name, parent=self)
        if not new_name or new_name == old_name:
            return
        if new_name in self.store.get_all_names():
            messagebox.showwarning(_locale.t("dlg.duplicate"), _locale.t("dlg.duplicate"), parent=self)
            return
        self.store.rename_combo(old_name, new_name)
        self._refresh_saved_list()
        self.saved_combo_var.set(new_name)

    def _delete_selected_combo(self):
        name = self.saved_combo_var.get()
        if not name:
            return
        msg = _locale.t("dlg.delete_msg", name=name)
        if not messagebox.askyesno(_locale.t("dlg.delete_title"), msg, parent=self):
            return
        self.store.delete_combo(name)
        self._refresh_saved_list()

    # ── 表单控制 ──

    def show_add_form(self, x: Optional[int] = None, y: Optional[int] = None):
        self.add_form_frame.grid_remove()
        if x is not None and y is not None:
            self.form_x_var.set(str(x))
            self.form_y_var.set(str(y))
            self.form_x_entry.configure(state="readonly")
            self.form_y_entry.configure(state="readonly")
        else:
            ax, ay = (0, 0)
            if self.get_current_coordinates:
                ax, ay = self.get_current_coordinates()
            self.form_x_var.set(str(ax) if ax or ay else "")
            self.form_y_var.set(str(ay) if ax or ay else "")
            self.form_x_entry.configure(state="normal")
            self.form_y_entry.configure(state="normal")
        self.form_action_var.set("left_click")
        self.form_delay_entry.delete(0, "end")
        self.form_delay_entry.insert(0, "0.5")
        self.form_scroll_var.set("3")
        self.scroll_row_frame.grid_remove()
        self.form_drag_x_var.set("")
        self.form_drag_y_var.set("")
        self.drag_row_frame.grid_remove()
        self.add_form_frame.grid()

    def hide_add_form(self):
        self.add_form_frame.grid_remove()

    def open_add_step_form(self):
        self.show_add_form()

    def quick_add_step(self, x: int, y: int):
        self.show_add_form(x, y)

    # ── 拖拽排序 ──

    def _on_drag_start(self, event):
        sel = self.tree.identify_row(event.y)
        if sel:
            self._drag_item = sel
            self._drag_idx = int(self.tree.item(sel, "values")[0]) - 1
            self.tree.bind("<B1-Motion>", self._on_drag_motion)
            self.tree.bind("<ButtonRelease-1>", self._on_drag_drop)
        else:
            self._drag_item = None
            self._drag_idx = -1

    def _on_drag_motion(self, event):
        target = self.tree.identify_row(event.y)
        for item in self.tree.get_children():
            tags = list(self.tree.item(item, "tags"))
            if "drag_target" in tags:
                tags.remove("drag_target")
                self.tree.item(item, tags=tags)
        if target and target != self._drag_item:
            self.tree.item(target, tags=("drag_target",))

    def _on_drag_drop(self, event):
        self.tree.unbind("<B1-Motion>")
        self.tree.unbind("<ButtonRelease-1>")
        for item in self.tree.get_children():
            tags = list(self.tree.item(item, "tags"))
            if "drag_target" in tags:
                tags.remove("drag_target")
                self.tree.item(item, tags=tags)

        if self._drag_item is None:
            return
        target = self.tree.identify_row(event.y)
        if not target or target == self._drag_item:
            self._drag_item = None
            self._drag_idx = -1
            return

        target_idx = int(self.tree.item(target, "values")[0]) - 1
        src = self._drag_idx
        if src == target_idx:
            self._drag_item = None
            self._drag_idx = -1
            return

        step = self.steps.pop(src)
        self.steps.insert(target_idx, step)
        self._refresh_tree()
        children = self.tree.get_children()
        if target_idx < len(children):
            self.tree.selection_set(children[target_idx])
        self._drag_item = None
        self._drag_idx = -1

    # ── 就地编辑 ──

    def _on_tree_double_click(self, event):
        self._drag_item = None
        self._drag_idx = -1
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if not values or not values[0].isdigit():
            return
        idx = int(values[0]) - 1
        if not (0 <= idx < len(self.steps)):
            return
        self._open_edit_dialog(idx)

    def _open_edit_dialog(self, idx: int):
        step = self.steps[idx]
        tr = _locale.t
        win = tk.Toplevel(self)
        win.title(f"{tr('dlg.edit_step', idx=str(idx + 1))}")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=tr("coord.x")).grid(row=0, column=0, padx=4, pady=4, sticky="e")
        ex_var = tk.StringVar(value=str(step.x))
        ttk.Entry(frm, textvariable=ex_var, width=10).grid(row=0, column=1, padx=4)
        ttk.Label(frm, text=tr("coord.y")).grid(row=0, column=2, padx=4, pady=4, sticky="e")
        ey_var = tk.StringVar(value=str(step.y))
        ttk.Entry(frm, textvariable=ey_var, width=10).grid(row=0, column=3, padx=4)

        ttk.Label(frm, text=tr("task.action")).grid(row=1, column=0, padx=4, pady=4, sticky="e")
        ea_var = tk.StringVar(value=step.action)
        action_names = list(ACTIONS.keys())
        action_menu = ttk.OptionMenu(frm, ea_var, step.action, *action_names,
                                      command=lambda *_: _toggle_extra_rows())
        action_menu.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4)

        ttk.Label(frm, text=tr("task.delay")).grid(row=1, column=3, padx=4, pady=4, sticky="e")
        ed_var = tk.StringVar(value=str(step.delay))
        ttk.Entry(frm, textvariable=ed_var, width=10).grid(row=1, column=4, padx=4)

        scroll_frm = ttk.Frame(frm)
        scroll_frm.grid(row=2, column=0, columnspan=5, sticky="ew", padx=4, pady=4)
        ttk.Label(scroll_frm, text=tr("task.scroll_amt")).pack(side="left", padx=2)
        es_var = tk.StringVar(value=str(step.scroll_amount))
        ttk.Entry(scroll_frm, textvariable=es_var, width=6).pack(side="left", padx=2)
        ttk.Label(scroll_frm, text=tr("task.lines")).pack(side="left")

        drag_frm = ttk.Frame(frm)
        drag_frm.grid(row=2, column=0, columnspan=5, sticky="ew", padx=4, pady=4)
        ttk.Label(drag_frm, text=tr("task.drag_x")).pack(side="left", padx=2)
        edx_var = tk.StringVar(value=str(step.drag_to_x))
        ttk.Entry(drag_frm, textvariable=edx_var, width=8).pack(side="left", padx=2)
        ttk.Label(drag_frm, text=tr("task.drag_y")).pack(side="left", padx=(8, 2))
        edy_var = tk.StringVar(value=str(step.drag_to_y))
        ttk.Entry(drag_frm, textvariable=edy_var, width=8).pack(side="left", padx=2)

        def _toggle_extra_rows():
            action = ea_var.get()
            if action in ("scroll_up", "scroll_down"):
                scroll_frm.grid()
                drag_frm.grid_remove()
            elif action == "drag":
                scroll_frm.grid_remove()
                drag_frm.grid()
            else:
                scroll_frm.grid_remove()
                drag_frm.grid_remove()

        if step.action in ("scroll_up", "scroll_down"):
            drag_frm.grid_remove()
        elif step.action == "drag":
            scroll_frm.grid_remove()
        else:
            scroll_frm.grid_remove()
            drag_frm.grid_remove()

        def _save_edit():
            try:
                x = int(ex_var.get())
                y = int(ey_var.get())
                delay = float(ed_var.get())
            except ValueError:
                messagebox.showwarning(tr("dlg.input_error"), tr("dlg.input_error"), parent=win)
                return
            action = ea_var.get()
            scroll_amount = step.scroll_amount
            if action in ("scroll_up", "scroll_down"):
                try:
                    scroll_amount = int(es_var.get())
                except ValueError:
                    scroll_amount = 3
            drag_to_x, drag_to_y = step.drag_to_x, step.drag_to_y
            if action == "drag":
                try:
                    drag_to_x = int(edx_var.get())
                    drag_to_y = int(edy_var.get())
                except ValueError:
                    messagebox.showwarning(tr("dlg.input_error"), tr("dlg.drag_error"), parent=win)
                    return
            self.steps[idx] = Step(x=x, y=y, action=action, delay=delay,
                                    scroll_amount=scroll_amount, drag_to_x=drag_to_x, drag_to_y=drag_to_y)
            self._refresh_tree()
            win.destroy()

        def _cancel_edit():
            win.destroy()

        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=3, column=0, columnspan=5, pady=(8, 0))
        ttk.Button(btn_frm, text=tr("task.confirm"), command=_save_edit).pack(side="left", padx=6)
        ttk.Button(btn_frm, text=tr("task.cancel"), command=_cancel_edit).pack(side="left", padx=6)

        win.update_idletasks()
        win.geometry(f"+{self.winfo_rootx() + 40}+{self.winfo_rooty() + 40}")

    def _confirm_add_step(self):
        tr = _locale.t
        try:
            x = int(self.form_x_var.get())
            y = int(self.form_y_var.get())
            delay = float(self.form_delay_entry.get())
        except ValueError:
            messagebox.showwarning(tr("dlg.input_error"), tr("dlg.input_error"), parent=self)
            return
        action = self.form_action_var.get()
        scroll_amount = 3
        if action in ("scroll_up", "scroll_down"):
            try:
                scroll_amount = int(self.form_scroll_var.get())
            except ValueError:
                scroll_amount = 3
        drag_to_x, drag_to_y = 0, 0
        if action == "drag":
            try:
                drag_to_x = int(self.form_drag_x_var.get())
                drag_to_y = int(self.form_drag_y_var.get())
            except ValueError:
                messagebox.showwarning(tr("dlg.input_error"), tr("dlg.drag_error"), parent=self)
                return
        self.steps.append(Step(x=x, y=y, action=action, delay=delay,
                                scroll_amount=scroll_amount, drag_to_x=drag_to_x, drag_to_y=drag_to_y))
        self._refresh_tree()
        self.hide_add_form()

    def _cancel_add_step(self):
        self.hide_add_form()

    def _on_form_action_change(self, *_):
        action = self.form_action_var.get()
        if action in ("scroll_up", "scroll_down"):
            self.scroll_row_frame.grid()
            self.drag_row_frame.grid_remove()
        elif action == "drag":
            self.scroll_row_frame.grid_remove()
            self.drag_row_frame.grid()
        else:
            self.scroll_row_frame.grid_remove()
            self.drag_row_frame.grid_remove()

    def _show_scroll_tooltip(self, event):
        x = event.widget.winfo_rootx() + 20
        y = event.widget.winfo_rooty() + 20
        self._tooltip = tk.Toplevel(event.widget)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x}+{y}")
        ttk.Label(self._tooltip,
                  text="Scroll amount: lines per wheel tick.\nPositive = up, negative = down.\n1 line ≈ 120 pixels on Windows.",
                  background="#FFFFE0", relief="solid", borderwidth=1,
                  padding=6, justify="left").pack()

    def _hide_scroll_tooltip(self, *_):
        if hasattr(self, '_tooltip') and self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

    # ── 表格操作 ──

    def delete_selected_step(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if values and values[0].isdigit():
            idx = int(values[0]) - 1
            if 0 <= idx < len(self.steps):
                del self.steps[idx]
                self._refresh_tree()

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, step in enumerate(self.steps):
            action_text = ACTIONS[step.action]
            if step.action in ("scroll_up", "scroll_down"):
                action_text += f" {step.scroll_amount}"
            elif step.action == "drag":
                action_text += f" →({step.drag_to_x},{step.drag_to_y})"
            self.tree.insert("", "end",
                             values=(idx + 1, step.x, step.y, action_text, step.delay))

    def get_task(self) -> ComboTask:
        try:
            repeat = int(self.repeat_entry.get())
        except ValueError:
            repeat = 1
        return ComboTask(steps=self.steps.copy(), repeat=repeat)
