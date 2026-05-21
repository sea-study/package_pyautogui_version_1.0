# 鼠标自由托管助手 (Mouse Automator)

Windows 桌面鼠标自动化工具，支持录制和执行鼠标点击、拖拽、滚轮等操作序列。

## 功能

- 5 种操作类型：左键单击、右键单击、拖拽、上滚、下滚
- 单步任务 / 组合任务模式
- 拖拽排序步骤
- F6 快捷键拾取坐标
- 鼠标移到屏幕角落紧急停止
- 窗口置顶 / 透明度调节
- 运行历史记录
- 中英文双语切换

## 环境要求

- Python 3.9+
- Windows

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 打包

```bash
pyinstaller mouse_automator.spec
```
