import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path
from PIL import Image, ImageTk

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.main import backend

def validate_username(username):
    # Example: at least 4 chars, only letters/numbers
    return len(username) >= 4 and username.isalnum()

def validate_password(password):
    return len(password) >= 8

def check_entries(*args):
    username = user_var.get()
    password = pass_var.get()
    if validate_username(username) and validate_password(password):
        login_btn.config(state="normal")
    else:
        login_btn.config(state="disabled")

def login():
    try:
        result = backend.login(user_var.get(), pass_var.get())
    except ValueError:
        messagebox.showerror("Login failed", "Invalid username or password.")
        return

    from app.catalog import open_catalog

    for child in root.winfo_children():
        child.destroy()
    open_catalog(root)

root = tk.Tk()
root.title("Demo App")
root.attributes('-fullscreen', True)

background_path = Path(__file__).resolve().with_name("background.jpg")
bg_image = Image.open(background_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
bg_photo = ImageTk.PhotoImage(bg_image)

# Create background label
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

user_var, pass_var = tk.StringVar(), tk.StringVar()
user_var.trace_add("write", check_entries)
pass_var.trace_add("write", check_entries)

frame = tk.Frame(root, bg="white", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Username", font=("Arial", 18)).pack(pady=5)
tk.Label(frame, text="*Must contain atleast 4 characters", font=("Arial", 12)).pack(pady=5)
tk.Entry(frame, textvariable=user_var, font=("Arial", 16), width=25).pack(pady=10)

tk.Label(frame, text="Password", font=("Arial", 18)).pack(pady=5)
tk.Label(frame, text="*Must contain at least 8 characters", font=("Arial", 12)).pack(pady=5)
tk.Entry(frame, textvariable=pass_var, show="*", font=("Arial", 16), width=25).pack(pady=5)

login_btn = tk.Button(frame, text="Login", command=login, state="disabled", font=("Arial", 18), width=15, height=2)
login_btn.pack(pady=20)

root.mainloop()