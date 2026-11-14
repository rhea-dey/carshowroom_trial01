from __future__ import annotations

from pathlib import Path
import tkinter as tk

from PIL import Image, ImageOps, ImageTk

from app.frontend.catalog import CatalogPage

BACKGROUND_IMAGE = Path(__file__).resolve().parent.parent / "images" / "background.jpg"

class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.load()

    def load(self) -> None:
        self.root.withdraw()
        self.window = tk.Toplevel(self.root)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = screen_width - 100
        height = screen_height - 100
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 40
        self.window.geometry(f"{width}x{height}+{x}+{y}")        
        self.window.resizable(False, False)

        self.window.title("RheaLasya Cars")
        self.window.configure(bg="#101827")
        self.window.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.background = tk.Label(self.window, bg="#101827")
        self.background.place(x=0, y=0, relwidth=1, relheight=1)

        with Image.open(BACKGROUND_IMAGE) as image:
            fitted = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(fitted)
        self.background.configure(image=self.photo)
        self.load_catalog()

    def load_catalog(self) -> None:
        self.catalog = CatalogPage(self.window)
        self.catalog.place(x=0, y=0, relwidth=1, relheight=1)
