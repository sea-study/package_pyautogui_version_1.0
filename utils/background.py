"""Shared pixel-art background tiling for windows and canvases."""
import os
import tkinter as tk
from typing import Optional


class BackgroundTiler:
    """Loads a background image once and tiles it onto target widgets."""

    def __init__(self, image_path: str) -> None:
        self._path: str = image_path
        self._image: Optional[tk.PhotoImage] = None
        if os.path.exists(image_path):
            self._image = tk.PhotoImage(file=image_path)

    @property
    def image(self) -> Optional[tk.PhotoImage]:
        return self._image

    def apply_to_canvas(self, canvas: tk.Canvas, tag: str = "bg") -> None:
        """Tile the background image onto an existing Canvas. Re-tiles on Configure."""
        if self._image is None:
            return
        iw, ih = self._image.width(), self._image.height()
        if iw <= 0 or ih <= 0:
            return

        def _redraw(_event: Optional[tk.Event] = None) -> None:
            canvas.delete(tag)
            cw = canvas.winfo_width() or 600
            ch = canvas.winfo_height() or 600
            for y in range(0, ch + ih, ih):
                for x in range(0, cw + iw, iw):
                    canvas.create_image(x, y, image=self._image, anchor="nw", tags=tag)
            canvas.tag_lower(tag)

        canvas.bind("<Configure>", _redraw, add="+")
        canvas.after(50, _redraw)

    def apply_to_window(self, window: tk.Toplevel) -> tk.Canvas:
        """Create a full-window Canvas with tiled background. Returns the Canvas."""
        bg_canvas = tk.Canvas(window, highlightthickness=0, bg="#F0F3F8")
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        window._bg_tiler_image = self._image  # pin reference to prevent GC
        self.apply_to_canvas(bg_canvas)
        return bg_canvas
