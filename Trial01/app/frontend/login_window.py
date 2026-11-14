import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk

from app.backend.backend_service import backendservice
from app.frontend.main_window import MainWindow

class LoginWindow:
    def __init__(self, root: tk.Tk, icon: ImageTk.PhotoImage) -> None:
        self.root = root
        
        WIDTH, HEIGHT = 460, 400
        x = (root.winfo_screenwidth() - WIDTH) // 2
        y = (root.winfo_screenheight() - HEIGHT) // 2
        root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
        root.resizable(False, False)
        
        root.iconphoto(True, icon)
        root.title("Login")
        root.configure(bg="#101827")

        frame = tk.Frame(root, bg="#ffffff", padx=34, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=380, height=300)

        tk.Label(frame, text="RheaLasya Cars", bg="#ffffff", fg="#172033",font=("Georgia", 21, "bold"),).pack(anchor="w")
        tk.Label(frame, text="Sign in to continue", bg="#ffffff", fg="#667085",font=("Segoe UI", 10),).pack(anchor="w", pady=(5, 24))

        username_row = tk.Frame(frame, bg="#ffffff")
        username_row.pack(fill="x", pady=(0, 16))
        tk.Label(username_row, text="Username", bg="#ffffff", fg="#344054").pack(side="left", padx=(0, 12))
        self.username = ttk.Entry(username_row)
        self.username.pack(side="left", fill="x", expand=True, ipady=7)

        password_row = tk.Frame(frame, bg="#ffffff")
        password_row.pack(fill="x", pady=(0, 16))
        tk.Label(password_row, text="Password", bg="#ffffff", fg="#344054").pack(side="left", padx=(0, 12))
        self.password = ttk.Entry(password_row, show="•")
        self.password.pack(side="left", fill="x", expand=True, ipady=7)

        buttons = tk.Frame(frame, bg="#ffffff")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Sign in", command=self.open_mainwindow).pack(side="left", fill="x", expand=True, ipady=5)
        ttk.Button(buttons, text="Cancel", command=root.destroy).pack(side="left", fill="x", expand=True, ipady=5, padx=(8, 0))

        self.username.focus_set()


    def open_mainwindow(self) -> None:
        if not self.username.get().strip() or not self.password.get():
            messagebox.showwarning("Sign in", "Enter a username and password to continue.", parent=self.root)
            return
        
        try:
            backendservice.login(self.username.get().strip(), self.password.get())
        except ValueError:
            messagebox.showerror("Login failed", "Invalid username or password.", parent=self.root)
            return

        self.main_window = MainWindow(self.root)