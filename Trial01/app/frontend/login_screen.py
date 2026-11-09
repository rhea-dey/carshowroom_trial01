from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from app.backend.main import backend
from app.frontend.catalog import open_catalog


def validate_username(username: str) -> bool:
    return len(username) >= 4 and username.isalnum()


def validate_password(password: str) -> bool:
    return len(password) >= 8


def run() -> None:
    root = tk.Tk()
    root.title("Demo App")
    root.attributes("-fullscreen", True)

    background_path = Path(__file__).resolve().parents[1] / "images" / "background.jpg"
    bg_image = Image.open(background_path)
    bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    user_var, pass_var = tk.StringVar(), tk.StringVar()
    login_btn: tk.Button

    def check_entries(*_args: str) -> None:
        is_valid = validate_username(user_var.get()) and validate_password(pass_var.get())
        login_btn.config(state="normal" if is_valid else "disabled")

    def login() -> None:
        try:
            backend.login(user_var.get(), pass_var.get())
        except ValueError:
            messagebox.showerror("Login failed", "Invalid username or password.")
            return

        for child in root.winfo_children():
            child.destroy()
        open_catalog(root)

    user_var.trace_add("write", check_entries)
    pass_var.trace_add("write", check_entries)

    frame = tk.Frame(root, bg="white", padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Username", font=("Arial", 18)).pack(pady=5)
    tk.Label(frame, text="*Must contain at least 4 characters", font=("Arial", 12)).pack(pady=5)
    tk.Entry(frame, textvariable=user_var, font=("Arial", 16), width=25).pack(pady=10)

    tk.Label(frame, text="Password", font=("Arial", 18)).pack(pady=5)
    tk.Label(frame, text="*Must contain at least 8 characters", font=("Arial", 12)).pack(pady=5)
    tk.Entry(frame, textvariable=pass_var, show="*", font=("Arial", 16), width=25).pack(pady=5)

    login_btn = tk.Button(
        frame,
        text="Login",
        command=login,
        state="disabled",
        font=("Arial", 18),
        width=15,
        height=2,
    )
    login_btn.pack(pady=20)

    root.mainloop()
