"""Light theme color constants and ttk style setup."""
import tkinter as tk
from tkinter import ttk

# ── Color palette ──
LIGHT_BG = "#F0F3F8"
LIGHT_CARD = "#FFFFFF"
LIGHT_FG = "#1E293B"
LIGHT_SUB = "#64748B"
LIGHT_BORDER = "#D9E0E8"
LIGHT_ACCENT = "#3B82F6"
LIGHT_ACCENT_HOVER = "#2563EB"
LIGHT_WARNING = "#D97706"
LIGHT_DANGER = "#DC2626"

COLORS = {
    "bg": LIGHT_BG,
    "card": LIGHT_CARD,
    "fg": LIGHT_FG,
    "sub": LIGHT_SUB,
    "border": LIGHT_BORDER,
    "accent": LIGHT_ACCENT,
    "accent_hover": LIGHT_ACCENT_HOVER,
    "warning": LIGHT_WARNING,
    "danger": LIGHT_DANGER,
}

STATUS_TIMEOUT_MS = 3000


def apply_theme(root: tk.Tk) -> None:
    """Apply the light theme to a tkinter root and its ttk styles."""
    c = COLORS
    root.configure(bg=c["bg"])

    s = ttk.Style(root)
    s.configure(".", background=c["bg"], foreground=c["fg"],
                fieldbackground=c["card"])
    s.configure("TLabel", background=c["bg"], foreground=c["fg"])
    s.configure("TFrame", background=c["bg"])
    s.configure("TLabelframe", background=c["bg"], foreground=c["fg"],
                bordercolor=c["border"])
    s.configure("TLabelframe.Label", background=c["bg"],
                foreground=c["accent"])
    s.configure("TButton", background=c["card"], foreground=c["fg"],
                borderwidth=1)
    s.map("TButton",
          background=[("active", c["accent_hover"]),
                      ("disabled", "#3A3A4A")],
          foreground=[("active", "#FFF"), ("disabled", "#777")])
    s.configure("Danger.TButton", background=c["danger"], foreground="#FFF")
    s.map("Danger.TButton",
          background=[("active", "#B91C1C"), ("disabled", "#3A3A4A")])
    s.configure("TEntry", fieldbackground=c["card"], foreground=c["fg"],
                insertcolor=c["fg"], borderwidth=1)
    s.configure("TOptionMenu", background=c["card"], foreground=c["fg"])
    s.configure("Treeview", background=c["card"], foreground=c["fg"],
                fieldbackground=c["card"])
    s.configure("Treeview.Heading", background=c["bg"],
                foreground=c["accent"])
    s.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
    s.map("TCheckbutton", foreground=[("active", c["accent_hover"])])
    s.configure("TRadiobutton", background=c["bg"], foreground=c["fg"])
    s.map("TRadiobutton", foreground=[("active", c["accent_hover"])])
    s.configure("TNotebook", background=c["bg"], borderwidth=0)
    s.configure("TNotebook.Tab", background=c["card"],
                foreground=c["fg"], padding=(12, 4))
    s.map("TNotebook.Tab",
          background=[("selected", c["bg"]), ("active", c["accent"])],
          foreground=[("selected", c["accent"]), ("active", "#FFF")])
    s.configure("TScale", background=c["bg"])
