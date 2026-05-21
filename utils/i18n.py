"""国际化：中英文双语支持，全局单例 LocaleManager。"""
from __future__ import annotations
from typing import Dict, Optional, Callable


STRINGS: Dict[str, Dict[str, str]] = {
    # ── 窗口标题 ──
    "app.title": {
        "zh": "🖱️鼠标自由托管助手--回味",
        "en": "🖱️ Mouse Auto Hosting Assistant",
    },
    # ── 坐标拾取 ──
    "coord.frame":       {"zh": "📍 坐标拾取",        "en": "📍 Coordinate Picker"},
    "coord.x":           {"zh": "X:",                 "en": "X:"},
    "coord.y":           {"zh": "Y:",                 "en": "Y:"},
    "coord.pick":        {"zh": "🎯 拾取 (F6)",       "en": "🎯 Pick (F6)"},
    "coord.add_step":    {"zh": "➕ 添加为步骤",       "en": "➕ Add as Step"},
    # ── Notebook 标签 ──
    "tab.edit":          {"zh": "任务编辑",            "en": "Task Editor"},
    "tab.history":       {"zh": "历史记录",            "en": "History"},
    "tab.log":           {"zh": "运行日志",            "en": "Run Log"},
    "tab.help":          {"zh": "📖 使用说明",         "en": "📖 Help"},
    "tab.author":        {"zh": "✍️ 作者的话",         "en": "✍️ Author"},
    # ── 模式 ──
    "mode.single":       {"zh": "单一操作",            "en": "Single Action"},
    "mode.combo":        {"zh": "组合操作",            "en": "Combo Action"},
    # ── 任务编辑 ──
    "task.single_frame": {"zh": "⚙️ 单一操作",        "en": "⚙️ Single Action"},
    "task.combo_frame":  {"zh": "🔗 组合操作",         "en": "🔗 Combo Action"},
    "task.action":       {"zh": "操作:",              "en": "Action:"},
    "task.repeat":       {"zh": "频率:",              "en": "Repeat:"},
    "task.custom":       {"zh": "自定义",             "en": "Custom"},
    "task.add_btn":      {"zh": "+ 添加步骤",          "en": "+ Add Step"},
    "task.del_btn":      {"zh": "🗑️ 删除选中步骤",    "en": "🗑️ Delete Selected"},
    "task.saved":        {"zh": "已保存:",            "en": "Saved:"},
    "task.load":         {"zh": "加载",               "en": "Load"},
    "task.save":         {"zh": "保存当前",            "en": "Save Current"},
    "task.rename":       {"zh": "重命名",             "en": "Rename"},
    "task.delete":       {"zh": "删除",               "en": "Delete"},
    "task.loop":         {"zh": "循环次数:",          "en": "Loop Count:"},
    "task.loop_hint":    {"zh": "(0=死循环)",         "en": "(0=Infinite)"},
    "task.delay":        {"zh": "延时(秒):",          "en": "Delay(s):"},
    "task.scroll_amt":   {"zh": "滚动量:",            "en": "Scroll Amt:"},
    "task.lines":        {"zh": "行",                 "en": "lines"},
    "task.drag_x":       {"zh": "终点X:",             "en": "End X:"},
    "task.drag_y":       {"zh": "终点Y:",             "en": "End Y:"},
    "task.confirm":      {"zh": "确定",               "en": "OK"},
    "task.cancel":       {"zh": "取消",               "en": "Cancel"},
    # ── 表格列头 ──
    "tree.seq":          {"zh": "序号",               "en": "#"},
    "tree.x":            {"zh": "X",                  "en": "X"},
    "tree.y":            {"zh": "Y",                  "en": "Y"},
    "tree.action":       {"zh": "操作",               "en": "Action"},
    "tree.delay":        {"zh": "延时(s)",            "en": "Delay(s)"},
    # ── 操作名称 ──
    "action.left_click":  {"zh": "左键单击",          "en": "Left Click"},
    "action.right_click": {"zh": "右键单击",          "en": "Right Click"},
    "action.drag":        {"zh": "拖拽",              "en": "Drag"},
    "action.scroll_up":   {"zh": "向上滚动",          "en": "Scroll Up"},
    "action.scroll_down": {"zh": "向下滚动",          "en": "Scroll Down"},
    # ── 频率 ──
    "repeat.1":          {"zh": "一次",               "en": "Once"},
    "repeat.5":          {"zh": "五次",               "en": "5 Times"},
    "repeat.0":          {"zh": "死循环",             "en": "Infinite"},
    "repeat.custom":     {"zh": "自定义",             "en": "Custom"},
    # ── 按钮 ──
    "btn.start":         {"zh": "▶ 开始",             "en": "▶ Start"},
    "btn.stop":          {"zh": "⏹ 停止",             "en": "⏹ Stop"},
    "btn.topmost":       {"zh": "📌 窗口置顶",        "en": "📌 Always on Top"},
    # ── 状态栏 ──
    "status.ready":      {"zh": "就绪",               "en": "Ready"},
    "status.running":    {"zh": "任务运行中...",       "en": "Task running..."},
    "status.pick_hint":  {"zh": "请按 F6 捕获鼠标位置...",  "en": "Press F6 to capture position..."},
    "status.captured":   {"zh": "已捕获坐标",          "en": "Captured"},
    "status.no_coord":   {"zh": "请先拾取坐标再添加步骤", "en": "Pick coordinates first"},
    "status.f6_failed":  {"zh": "⚠ 全局热键监听启动失败，坐标拾取不可用",
                          "en": "⚠ Global hotkey listener failed, coordinate picking unavailable"},
    # ── 透明度 ──
    "opacity.label":     {"zh": "透明度:",            "en": "Opacity:"},
    # ── 紧急停止提示 ──
    "warn.emergency":    {"zh": "⚠️ 移动鼠标到屏幕左上角或右上角紧急停止 | Ctrl+Enter 开始 | Esc 停止",
                          "en": "⚠️ Move mouse to top-left or top-right corner for emergency stop | Ctrl+Enter Start | Esc Stop"},
    # ── 历史 ──
    "history.time":      {"zh": "时间",               "en": "Time"},
    "history.type":      {"zh": "类型",               "en": "Type"},
    "history.action":    {"zh": "操作",               "en": "Action"},
    "history.steps":     {"zh": "步骤数",             "en": "Steps"},
    "history.repeat":    {"zh": "循环",               "en": "Repeat"},
    "history.status":    {"zh": "状态",               "en": "Status"},
    "history.duration":  {"zh": "耗时(s)",            "en": "Dur(s)"},
    "history.clear":     {"zh": "清空历史",            "en": "Clear History"},
    "history.empty":     {"zh": "暂无历史记录",        "en": "No history yet"},
    "history.type_single": {"zh": "单一",             "en": "Single"},
    "history.type_combo":  {"zh": "组合",             "en": "Combo"},
    "history.completed":   {"zh": "已完成",           "en": "Completed"},
    "history.stopped":     {"zh": "已停止",           "en": "Stopped"},
    # ── 语言切换 ──
    "btn.lang":          {"zh": "EN",                 "en": "中文"},
    # ── 日志 ──
    "log.ready":         {"zh": "日志就绪",            "en": "Log ready"},
    "log.single_start":  {"zh": "开始单一操作: {action}, 坐标({x},{y}), 重复{repeat}次",
                          "en": "Single action started: {action}, pos({x},{y}), repeat {repeat}"},
    "log.single_done":   {"zh": "第{count}次操作完成",  "en": "Action #{count} done"},
    "log.single_end":    {"zh": "单一操作完成",         "en": "Single action complete"},
    "log.combo_start":   {"zh": "开始组合操作: {steps}步, 循环{repeat}次",
                          "en": "Combo started: {steps} steps, loop {repeat}"},
    "log.combo_round":   {"zh": "第{round}轮",         "en": "Round #{round}"},
    "log.combo_step":    {"zh": "步骤{idx} ({action}, {x},{y}) 完成",
                          "en": "Step {idx} ({action}, {x},{y}) done"},
    "log.combo_end":     {"zh": "组合操作完成",         "en": "Combo complete"},
    "log.emergency":     {"zh": "任务被紧急停止",       "en": "Task emergency-stopped"},
    # ── 弹窗 ──
    "popup.help_title":  {"zh": "📖 使用说明",         "en": "📖 Help"},
    "popup.first_help_title": {"zh": "使用说明",       "en": "Help"},
    "popup.first_help_subtitle": {"zh": "🖱️ 鼠标自由托管助手", "en": "🖱️ Mouse Auto Hosting Assistant"},
    "popup.author_title": {"zh": "✍️ 作者的话",        "en": "✍️ Author's Note"},
    "popup.author_label": {"zh": "✍️ 作者的话",        "en": "✍️ Author's Note"},
    "popup.author_content": {
        "zh": ("感谢您的使用！\n\n"
               "这个软件是我通过 vibe coding 方式制作的，"
               "旨在帮我们完成鼠标自动托管的任务。\n\n"
               "软件还有许多需要改进的地方，欢迎提出您宝贵的意见：\n\n"
               "  QQ：1347644192\n"
               "  微信：a18617453127\n"
               "  GitHub：@wy"),
        "en": ("Thank you for using this tool!\n\n"
               "This software was built through vibe coding "
               "to help automate mouse tasks.\n\n"
               "There's still room for improvement — feedback is welcome:\n\n"
               "  QQ: 1347644192\n"
               "  WeChat: a18617453127\n"
               "  GitHub: @wy"),
    },
    "popup.close":       {"zh": "关闭",               "en": "Close"},
    "popup.got_it":      {"zh": "我知道了",            "en": "Got it"},
    "popup.no_show":     {"zh": "下次不再显示",        "en": "Don't show again"},
    # ── 帮助步骤 ──
    "help.coord_title":  {"zh": "📍 坐标拾取",        "en": "📍 Coordinate Picking"},
    "help.coord_1":      {"zh": "将鼠标移动到目标位置，按 F6 捕获坐标",
                          "en": "Move the mouse to the target and press F6 to capture"},
    "help.coord_2":      {"zh": "或在 X / Y 输入框中手动输入坐标值",
                          "en": "Or manually enter coordinates in the X / Y fields"},
    "help.single_title": {"zh": "⚙️ 单一操作",        "en": "⚙️ Single Action"},
    "help.single_1":     {"zh": "选择操作类型（左键单击 / 右键单击 / 拖拽 / 滚动）",
                          "en": "Select action type (left click / right click / drag / scroll)"},
    "help.single_2":     {"zh": "设置重复次数，点击「▶ 开始」执行",
                          "en": "Set repeat count, press Start to execute"},
    "help.combo_title":  {"zh": "🔗 组合操作（默认）",  "en": "🔗 Combo Action (default)"},
    "help.combo_1":      {"zh": "点击「+ 添加步骤」逐个添加操作步骤",
                          "en": "Click Add Step to add actions one by one"},
    "help.combo_2":      {"zh": "双击步骤行可修改 X / Y / 操作 / 延时等",
                          "en": "Double-click a step row to edit X/Y/action/delay etc."},
    "help.combo_3":      {"zh": "按住步骤行拖拽可调整执行顺序",
                          "en": "Drag step rows to reorder execution"},
    "help.combo_4":      {"zh": "点击「加载」可读取已保存的方案",
                          "en": "Click Load to open a saved combo"},
    "help.combo_5":      {"zh": "点击「保存当前」可将当前步骤保存为方案",
                          "en": "Click Save Current to store steps as a combo"},
    "help.combo_6":      {"zh": "设置循环次数后点击「▶ 开始」执行",
                          "en": "Set loop count then press Start to execute"},
    "help.stop_title":   {"zh": "⏹ 紧急停止",         "en": "⏹ Emergency Stop"},
    "help.stop_1":       {"zh": "任务运行期间，将鼠标移至屏幕",
                          "en": "While a task is running, move mouse to the"},
    "help.stop_2":       {"zh": "左上角 或 右上角 即可立即停止",
                          "en": "top-left or top-right corner to stop immediately"},
    "help.topmost_title": {"zh": "📌 窗口置顶",        "en": "📌 Always on Top"},
    "help.topmost_1":    {"zh": "默认勾选，窗口始终显示在最前",
                          "en": "Checked by default, window stays on top"},
    "help.topmost_2":    {"zh": "取消勾选后可被其他窗口遮挡",
                          "en": "Uncheck to allow other windows to cover it"},
    # ── 对话/弹窗消息 ──
    "dlg.save_title":    {"zh": "保存组合",            "en": "Save Combo"},
    "dlg.save_prompt":   {"zh": "请输入组合名称:",      "en": "Enter combo name:"},
    "dlg.overwrite_title": {"zh": "覆盖确认",          "en": "Overwrite Confirm"},
    "dlg.overwrite_msg": {"zh": "名称「{name}」已存在，是否覆盖？",
                          "en": "Name '{name}' already exists, overwrite?"},
    "dlg.no_steps":      {"zh": "当前组合没有步骤",     "en": "No steps in current combo"},
    "dlg.select_combo":  {"zh": "请先选择一个已保存的组合", "en": "Select a saved combo first"},
    "dlg.rename_title":  {"zh": "重命名组合",          "en": "Rename Combo"},
    "dlg.rename_prompt": {"zh": "请输入新名称:",        "en": "Enter new name:"},
    "dlg.duplicate":     {"zh": "该名称已存在，请使用其他名称", "en": "Name already exists, use another"},
    "dlg.delete_title":  {"zh": "删除确认",            "en": "Delete Confirm"},
    "dlg.delete_msg":    {"zh": "确定要删除组合「{name}」吗？",
                          "en": "Are you sure you want to delete '{name}'?"},
    "dlg.input_error":   {"zh": "请检查坐标和延时格式",  "en": "Check coordinate/delay format"},
    "dlg.drag_error":    {"zh": "请输入有效的拖拽终点坐标", "en": "Enter valid drag destination coordinates"},
    "dlg.edit_step":     {"zh": "编辑步骤 {idx}",      "en": "Edit Step {idx}"},
}

# ── 帮助步骤结构（key 引用）──
HELP_STRUCTURE: list[tuple[str, list[str]]] = [
    ("help.coord_title",  ["help.coord_1", "help.coord_2"]),
    ("help.single_title",  ["help.single_1", "help.single_2"]),
    ("help.combo_title",   ["help.combo_1", "help.combo_2", "help.combo_3",
                            "help.combo_4", "help.combo_5", "help.combo_6"]),
    ("help.stop_title",    ["help.stop_1", "help.stop_2"]),
    ("help.topmost_title", ["help.topmost_1", "help.topmost_2"]),
]


class LocaleManager:
    """全局语言管理器（单例）。"""

    _instance: Optional["LocaleManager"] = None

    def __new__(cls) -> "LocaleManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._locale = "zh"
            cls._instance._listeners: list[Callable[[], None]] = []
        return cls._instance

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def is_chinese(self) -> bool:
        return self._locale == "zh"

    def t(self, key: str, **kwargs) -> str:
        """Get the translated string for the given key. Supports format kwargs."""
        entry = STRINGS.get(key, {})
        text = entry.get(self._locale, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def toggle(self) -> None:
        self._locale = "en" if self._locale == "zh" else "zh"
        for listener in self._listeners:
            listener()

    def on_change(self, callback: Callable[[], None]) -> None:
        self._listeners.append(callback)


# Convenience function
def tr(key: str, **kwargs) -> str:
    return LocaleManager().t(key, **kwargs)
