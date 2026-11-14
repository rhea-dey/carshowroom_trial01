import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

from app.frontend.login_screen import LoginWindow

ICON_PATH = Path(__file__).resolve().parent / "app" / "images" / "rl.ico"

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, ImageTk.PhotoImage(Image.open(ICON_PATH)))
    root.mainloop()