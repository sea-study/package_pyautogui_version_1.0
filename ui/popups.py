"""Popup windows: help, first-run help, author info. v2: i18n support."""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from ui.theme import COLORS, LIGHT_ACCENT, LIGHT_ACCENT_HOVER, LIGHT_SUB, LIGHT_FG
from ui.models import get_help_steps
from utils.background import BackgroundTiler
from utils.i18n import LocaleManager

_locale = LocaleManager()


class HelpWindow(tk.Toplevel):
    """Reusable help popup with scrollable content and tiled background."""

    def __init__(self, parent: tk.Tk, tiler: BackgroundTiler) -> None:
        super().__init__(parent)
        self.title(_locale.t("popup.help_title"))
        self.geometry("480x520")
        self.resizable(True, True)
        self.minsize(360, 300)
        self.attributes('-topmost', True)
        self.transient(parent)

        tiler.apply_to_window(self)

        scroll_container = tk.Frame(self, bd=0, bg="#FAFBFC")
        scroll_container.place(relx=0.5, rely=0.5, anchor="center",
                               relwidth=0.9, relheight=0.85)

        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FAFBFC")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event: tk.Event) -> None:
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        self.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<MouseWheel>", _on_mousewheel)

        steps = get_help_steps()
        for i, (title, items) in enumerate(steps):
            tk.Label(scrollable_frame, text=f"{i + 1}. {title}",
                     font=("Microsoft YaHei", 10, "bold"),
                     fg=LIGHT_FG, bg="#FAFBFC",
                     anchor="w").pack(fill="x", padx=16, pady=(10 if i == 0 else 6, 2))
            for item in items:
                tk.Label(scrollable_frame, text=f"   • {item}",
                         font=("Microsoft YaHei", 9),
                         fg="#475569", bg="#FAFBFC",
                         anchor="w", justify="left").pack(fill="x", padx=16, pady=1)

        tk.Button(self, text=_locale.t("popup.close"),
                  font=("Microsoft YaHei", 9, "bold"),
                  fg="white", bg=LIGHT_ACCENT,
                  activebackground=LIGHT_ACCENT_HOVER,
                  activeforeground="white", relief="flat",
                  padx=20, pady=4, cursor="hand2",
                  command=self.destroy).pack(side="bottom", pady=(0, 12))

        self._center_on(parent)

    def _center_on(self, parent: tk.Tk) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class FirstRunHelpWindow(tk.Toplevel):
    """Help popup shown on first run, with 'don't show again' checkbox."""

    def __init__(self, parent: tk.Tk, tiler: BackgroundTiler,
                 on_dismiss: Callable[[bool], None]) -> None:
        super().__init__(parent)
        self.title(_locale.t("popup.first_help_title"))
        self.geometry("480x520")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.transient(parent)
        self._on_dismiss = on_dismiss

        tk.Label(self, text=_locale.t("popup.first_help_subtitle"),
                 font=("Microsoft YaHei", 16, "bold"),
                 fg=LIGHT_ACCENT).pack(pady=(16, 4))
        tk.Label(self, text=_locale.t("popup.first_help_title"),
                 font=("Microsoft YaHei", 10),
                 fg=LIGHT_SUB).pack(pady=(0, 12))

        scroll_container = tk.Frame(self, bd=1, relief="solid",
                                    highlightbackground=COLORS["border"], highlightthickness=1)
        scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FAFBFC")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        tiler.apply_to_canvas(canvas)

        def _on_mousewheel(event: tk.Event) -> None:
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        self.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<MouseWheel>", _on_mousewheel)

        steps = get_help_steps()
        for i, (title, items) in enumerate(steps):
            tk.Label(scrollable_frame, text=f"{i + 1}. {title}",
                     font=("Microsoft YaHei", 10, "bold"),
                     fg=LIGHT_FG, bg="#FAFBFC",
                     anchor="w").pack(fill="x", padx=16, pady=(10 if i == 0 else 6, 2))
            for item in items:
                tk.Label(scrollable_frame, text=f"   • {item}",
                         font=("Microsoft YaHei", 9),
                         fg="#475569", bg="#FAFBFC",
                         anchor="w", justify="left").pack(fill="x", padx=16, pady=1)

        self._no_show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text=_locale.t("popup.no_show"),
                       variable=self._no_show_var,
                       font=("Microsoft YaHei", 9),
                       fg=LIGHT_SUB,
                       selectcolor=COLORS["card"],
                       activebackground="white").pack(pady=(0, 4))

        tk.Button(self, text=_locale.t("popup.got_it"),
                  font=("Microsoft YaHei", 10, "bold"),
                  fg="white", bg=LIGHT_ACCENT,
                  activebackground=LIGHT_ACCENT_HOVER,
                  activeforeground="white",
                  relief="flat", padx=30, pady=6,
                  cursor="hand2",
                  command=self._close).pack(pady=(0, 16))

        self._center_on(parent)

    def _close(self) -> None:
        self._on_dismiss(self._no_show_var.get())
        self.destroy()

    def _center_on(self, parent: tk.Tk) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class AuthorWindow(tk.Toplevel):
    """Author info popup with contact details."""

    def __init__(self, parent: tk.Tk, tiler: BackgroundTiler) -> None:
        super().__init__(parent)
        self.title(_locale.t("popup.author_title"))
        self.geometry("480x400")
        self.resizable(True, True)
        self.minsize(360, 280)
        self.attributes('-topmost', True)
        self.transient(parent)

        tiler.apply_to_window(self)

        card = tk.Frame(self, bg="#FFFFFF", bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.9, relheight=0.9)

        tk.Label(card, text=_locale.t("popup.author_label"),
                 font=("Microsoft YaHei", 14, "bold"),
                 fg=LIGHT_ACCENT, bg="#FFFFFF").pack(pady=(14, 8))

        text_frame = tk.Frame(card, bd=0)
        text_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        author_text = tk.Text(text_frame, font=("Microsoft YaHei", 10),
                              fg="#1E293B", bg="#F8FAFC", wrap="word",
                              borderwidth=0, padx=10, pady=8,
                              relief="flat", highlightthickness=1,
                              highlightbackground="#CBD5E1")
        author_text.pack(fill="both", expand=True)
        author_text.insert("1.0", _locale.t("popup.author_content"))

        tk.Button(card, text=_locale.t("popup.close"),
                  font=("Microsoft YaHei", 9, "bold"),
                  fg="white", bg=LIGHT_ACCENT,
                  activebackground=LIGHT_ACCENT_HOVER,
                  activeforeground="white", relief="flat",
                  padx=20, pady=4, cursor="hand2",
                  command=self.destroy).pack(pady=(0, 12))

        self._center_on(parent)

    def _center_on(self, parent: tk.Tk) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
