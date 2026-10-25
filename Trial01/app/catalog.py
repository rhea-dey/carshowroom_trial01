from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from io import BytesIO
from pathlib import Path
from typing import Any, Callable
from urllib.request import urlopen

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageTk

from app.main import backend
from app.repositories.in_memory_repository import IMAGE_FILES


ACCENT = "#35b4ef"
PANEL = "#fff2b8"
BORDER = "#111111"
CUSTOMIZATION_FILES = {
    "CR-101": "images/customization/panther-gls-130-custom.png",
    "CR-102": "images/customization/rockrover-rl-custom.png",
    "CR-103": "images/customization/falcon-x-custom.png",
    "CR-104": "images/customization/custom-z-custom.png",
    "CR-105": "images/customization/rlv-minora-custom.png",
    "CR-106": "images/customization/fenty-500-custom.png",
}


class CatalogPage(tk.Frame):
    """Scrollable catalog and car customization detail view."""

    def __init__(self, parent: tk.Misc, on_logout: Callable[[], None] | None = None):
        super().__init__(parent, bg="white")
        self.on_logout = on_logout
        self.catalog: list[dict[str, Any]] = backend.fetch_catalog()["cars"]
        self.visible_cars = self.catalog[:]
        self.current_car: dict[str, Any] | None = None
        self.selections: list[dict[str, Any]] = []
        self.image_references: list[ImageTk.PhotoImage] = []
        self._build_header()
        self.show_catalog()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=ACCENT, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="RheaLaysa",
            bg=ACCENT,
            fg="white",
            font=("Georgia", 20, "italic"),
        ).pack(side="left", padx=18)
        self.selection_button = tk.Button(
            header,
            text="Compare selection (0/3)",
            font=("Arial", 14, "bold"),
            bg="#66d9e8",
            relief="flat",
            padx=14,
            pady=6,
            command=self.show_comparison,
            state="disabled",
        )
        self.selection_button.pack(side="right", padx=8, pady=7)
        tk.Button(
            header,
            text="Help",
            font=("Arial", 14),
            bg="#66d9e8",
            relief="flat",
            padx=18,
            command=self._show_help,
        ).pack(side="right", padx=8, pady=7)

    def _show_help(self) -> None:
        messagebox.showinfo(
            "Help",
            "Search for a car, then select a card to view its specifications and customize it.",
        )

    def show_catalog(self) -> None:
        self.current_car = None
        for child in self.winfo_children():
            if getattr(child, "view_area", False):
                child.destroy()

        view = tk.Frame(self, bg="white")
        view.view_area = True
        view.pack(fill="both", expand=True)

        search_frame = tk.Frame(view, bg="white")
        search_frame.pack(fill="x", padx=90, pady=(28, 16))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 16),
            relief="solid",
            bd=2,
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(
            search_frame,
            text="Search",
            font=("Arial", 13),
            bg=ACCENT,
            relief="flat",
            padx=18,
            command=self._filter_catalog,
        ).pack(side="left", padx=(8, 0), ipady=7)
        search_entry.bind("<KeyRelease>", lambda _event: self._filter_catalog())

        canvas_frame = tk.Frame(view, bg="white")
        canvas_frame.pack(fill="both", expand=True, padx=55, pady=(0, 18))
        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.cards_frame = tk.Frame(canvas, bg="white")
        window_id = canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.catalog_canvas = canvas

        def resize_cards(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())

        self.cards_frame.bind("<Configure>", resize_cards)
        canvas.bind("<Configure>", resize_cards)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"))
        self._render_cards()

    def _filter_catalog(self) -> None:
        query = self.search_var.get().strip().lower()
        self.visible_cars = [
            car for car in self.catalog if query in self._car_text(car).lower()
        ]
        self._render_cards()

    def _render_cards(self) -> None:
        for child in self.cards_frame.winfo_children():
            child.destroy()
        self.image_references.clear()
        for index, car in enumerate(self.visible_cars):
            row, column = divmod(index, 3)
            self._create_card(car, row, column)
        for column in range(3):
            self.cards_frame.grid_columnconfigure(column, weight=1)

    def _create_card(self, car: dict[str, Any], row: int, column: int) -> None:
        card = tk.Frame(self.cards_frame, bg="white", bd=2, relief="solid", cursor="hand2")
        card.grid(row=row, column=column, padx=20, pady=20, sticky="nsew")
        card.configure(width=310, height=350)
        image_box = tk.Frame(card, bg="#e9f7fc", width=300, height=190)
        image_box.pack(fill="x", padx=10, pady=(10, 6))
        image_box.pack_propagate(False)
        photo = self._load_image(car, size=(300, 190))
        if photo:
            image_label = tk.Button(
                image_box,
                image=photo,
                bg="#e9f7fc",
                activebackground="#e9f7fc",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda selected=car: self.show_detail(selected),
            )
            image_label.image = photo
            image_label.pack(fill="both", expand=True)

        values = [
            (car.get("model", "Unknown model"), 14, "bold"),
            (car.get("displayPrice", self._format_price(car.get("price", ""))), 12, "bold"),
            (car.get("category", "Car"), 11, "normal"),
        ]
        for text, size, weight in values:
            tk.Label(card, text=text, anchor="w", bg="white", font=("Arial", size, weight)).pack(fill="x", padx=10, pady=3)
        self._bind_click(card, lambda selected=car: self.show_detail(selected))

    def _bind_click(self, widget: tk.Widget, callback: Callable[[], None]) -> None:
        widget.bind("<Button-1>", lambda _event: callback())
        for child in widget.winfo_children():
            self._bind_click(child, callback)

    def show_detail(self, car: dict[str, Any]) -> None:
        self.current_car = car
        for child in self.winfo_children():
            if getattr(child, "view_area", False):
                child.destroy()

        view = tk.Frame(self, bg="white")
        view.view_area = True
        view.pack(fill="both", expand=True)
        tk.Button(view, text="<- Back to catalog", font=("Arial", 12), command=self.show_catalog).pack(anchor="w", padx=18, pady=12)

        content = tk.Frame(view, bg="white")
        content.pack(fill="both", expand=True)
        main = tk.Frame(content, bg="white")
        main.pack(side="left", fill="both", expand=True)
        specs = tk.Frame(content, bg=PANEL, width=300, padx=18, pady=18)
        specs.pack(side="right", fill="y")
        specs.pack_propagate(False)

        tk.Label(main, text=str(car.get("model", "Car")).upper(), font=("Arial", 28, "bold"), bg="white").pack(anchor="w", padx=24, pady=(10, 4))
        image_box = tk.Frame(main, bg="white", height=620)
        image_box.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        image_box.pack_propagate(False)
        self.detail_image_box = image_box
        self.selected_colour = str(car.get("specs", {}).get("color", "Black"))
        photo = self._load_image(car, size=(1100, 620), colour=self.selected_colour)
        if photo:
            self._set_detail_image(photo)

        customization = tk.Frame(main, bg=PANEL, padx=24, pady=14, height=190)
        customization.pack(fill="x", side="bottom", padx=24, pady=(10, 0))
        customization.pack_propagate(False)
        tk.Label(customization, text="CUSTOMIZING PANEL", font=("Arial", 22, "bold"), bg=PANEL).pack()
        controls = tk.Frame(customization, bg=PANEL)
        controls.pack(fill="x", pady=8)
        self.selected_seat_colour = "Black"
        self.selected_tyre_size = "16 Inch"
        self._add_options(
            controls,
            "CAR COLOUR",
            self._car_colours(car),
            0,
            on_change=self._change_car_colour,
            selected_value=self.selected_colour,
        )
        self._add_options(
            controls,
            "SEAT COLOUR",
            ["Black", "White", "Tan"],
            1,
            on_change=self._change_seat_colour,
            selected_value=self.selected_seat_colour,
        )
        self._add_options(
            controls,
            "TYRE SIZE",
            ["16 Inch", "17 Inch"],
            2,
            radio=True,
            on_change=self._change_tyre_size,
            selected_value=self.selected_tyre_size,
        )
        actions = tk.Frame(customization, bg=PANEL)
        actions.pack()
        tk.Button(
            actions,
            text="Make selection",
            font=("Arial", 14, "bold"),
            bg="#76d65b",
            padx=18,
            pady=6,
            command=self._book_current_selection,
        ).pack(side="left", padx=8)
        tk.Button(
            actions,
            text="Add to selection",
            font=("Arial", 16, "bold"),
            bg=ACCENT,
            padx=22,
            pady=8,
            command=self._add_current_selection,
        ).pack(side="left", padx=8)

        self._render_specs(specs, car)

    def _add_options(
        self,
        parent: tk.Frame,
        title: str,
        options: list[str],
        column: int,
        radio: bool = False,
        on_change: Callable[[str], None] | None = None,
        selected_value: str | None = None,
    ) -> None:
        section = tk.Frame(parent, bg=PANEL)
        section.grid(row=0, column=column, padx=20, sticky="n")
        tk.Label(section, text=title, font=("Arial", 14), bg=PANEL).pack(anchor="w")
        variable = tk.StringVar(value=selected_value or options[0])
        for option in options:
            if radio:
                tk.Radiobutton(
                    section,
                    text=option,
                    variable=variable,
                    value=option,
                    bg=PANEL,
                    activebackground=PANEL,
                    command=lambda value=option: self._select_option(variable, value, on_change),
                ).pack(anchor="w")
            else:
                swatch = tk.Button(
                    section,
                    text="",
                    width=4,
                    height=2,
                    bg=self._colour_value(option),
                    activebackground=self._colour_value(option),
                    relief="raised",
                    command=lambda value=option: self._select_option(variable, value, on_change),
                )
                swatch.pack(side="left", padx=3, pady=8)
                swatch.bind("<Enter>", lambda _event, value=option: self._show_status(value))

    @staticmethod
    def _select_option(variable: tk.StringVar, value: str, on_change: Callable[[str], None] | None) -> None:
        variable.set(value)
        if on_change:
            on_change(value)

    def _change_car_colour(self, colour: str) -> None:
        self.selected_colour = colour
        photo = self._load_image(self.current_car or {}, size=(1100, 620), colour=colour)
        if photo:
            self._set_detail_image(photo)

    def _change_seat_colour(self, colour: str) -> None:
        self.selected_seat_colour = colour

    def _change_tyre_size(self, size: str) -> None:
        self.selected_tyre_size = size

    def _add_current_selection(self) -> None:
        car = self.current_car
        if car is None:
            return
        if any(selection["car"].get("carId") == car.get("carId") for selection in self.selections):
            messagebox.showinfo("Already selected", "This car is already in your comparison selection.")
            return
        if len(self.selections) >= 3:
            messagebox.showinfo("Selection full", "You can compare up to 3 cars. Remove one before adding another.")
            return
        self.selections.append(self._current_configuration())
        self._update_selection_button()
        self.show_comparison()

    def _current_configuration(self) -> dict[str, Any]:
        if self.current_car is None:
            raise ValueError("There is no car selected.")
        return {
            "car": self.current_car,
            "carColour": self.selected_colour,
            "seatColour": self.selected_seat_colour,
            "tyreSize": self.selected_tyre_size,
        }

    def _update_selection_button(self) -> None:
        self.selection_button.configure(
            text=f"Compare selection ({len(self.selections)}/3)",
            state="normal" if self.selections else "disabled",
        )

    def show_comparison(self) -> None:
        self.current_car = None
        self._clear_view()
        view = self._new_view()
        tk.Label(view, text="COMPARE YOUR SELECTION", font=("Arial", 30, "bold"), bg="white").pack(
            anchor="w", padx=24, pady=(16, 8)
        )
        tk.Label(
            view,
            text=f"Compare up to 3 cars. Selected: {len(self.selections)}/3",
            font=("Arial", 16),
            bg="white",
        ).pack(anchor="w", padx=24, pady=(0, 12))
        tk.Button(view, text="<- Back to catalog", font=("Arial", 14), command=self.show_catalog).pack(
            anchor="w", padx=24, pady=(0, 12)
        )
        if not self.selections:
            tk.Label(view, text="No cars selected yet.", font=("Arial", 18), bg="white").pack(pady=30)
            return

        table = tk.Frame(view, bg="white")
        table.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        labels = [
            "CRITERIAS",
            "CAR COLOUR",
            "SEAT COLOUR",
            "TYRE SIZE",
            "DIMENSIONS (mm)",
            "FEATURES",
            "ENGINE TYPE",
            "MILEAGE",
            "HIGHEST SPEED",
            "PRICE",
            "TYPE OF CAR",
        ]
        for row, title in enumerate(labels):
            tk.Label(
                table,
                text=title,
                font=("Arial", 15, "bold" if row == 0 else "normal"),
                bg=ACCENT if row == 0 else "white",
                relief="solid",
                bd=1,
                padx=10,
                pady=12,
                wraplength=220,
            ).grid(row=row, column=0, sticky="nsew")
        table.grid_columnconfigure(0, weight=1, minsize=190)
        for column, selection in enumerate(self.selections, start=1):
            car = selection["car"]
            values = [
                str(car.get("model", "Car")).upper(),
                selection["carColour"],
                selection["seatColour"],
                selection["tyreSize"],
                str(car.get("dimensions", car.get("details", {}).get("dimensions", "Not listed"))),
                ", ".join(str(feature) for feature in car.get("features", car.get("details", {}).get("features", []))),
                str(car.get("specs", {}).get("engine", car.get("details", {}).get("engine", "Not listed"))),
                str(car.get("mileage", car.get("details", {}).get("mileage", "Not listed"))),
                str(car.get("highestSpeed", car.get("details", {}).get("highestSpeed", "Not listed"))),
                str(car.get("displayPrice", self._format_price(car.get("price", "")))),
                str(car.get("category", car.get("details", {}).get("category", "Not listed"))),
            ]
            for row, value in enumerate(values):
                tk.Label(
                    table,
                    text=value,
                    font=("Arial", 15 if row == 0 else 14, "bold" if row == 0 else "normal"),
                    bg=ACCENT if row == 0 else "white",
                    relief="solid",
                    bd=1,
                    padx=10,
                    pady=12,
                    wraplength=340,
                    justify="center",
                ).grid(row=row, column=column, sticky="nsew")
            table.grid_columnconfigure(column, weight=2, minsize=220)
            tk.Button(
                table,
                text="BOOK",
                font=("Arial", 10, "bold"),
                bg="#76d65b",
                command=lambda selected=selection: self._book_selection(selected),
            ).grid(row=len(labels), column=column, padx=8, pady=3)
            tk.Button(
                table,
                text="Remove",
                font=("Arial", 11),
                command=lambda selected=selection: self._remove_selection(selected),
            ).grid(row=len(labels) + 1, column=column, padx=8, pady=3)
        for row in range(len(labels)):
            table.grid_rowconfigure(row, weight=1, uniform="comparison-data")

    def _remove_selection(self, selection: dict[str, Any]) -> None:
        self.selections.remove(selection)
        self._update_selection_button()
        self.show_comparison()

    def _book_current_selection(self) -> None:
        if self.current_car is not None:
            self._book_selection(self._current_configuration())

    def _book_selection(self, selection: dict[str, Any]) -> None:
        car = selection["car"]
        try:
            result = backend.trigger_booking("CUST-1001", str(car["carId"]))
        except ValueError as error:
            messagebox.showerror("Booking failed", str(error))
            return
        self.show_order_summary(selection, result["bookingId"])

    def show_order_summary(self, selection: dict[str, Any], booking_id: str) -> None:
        self.current_car = None
        self._clear_view()
        view = self._new_view()
        tk.Label(view, text="ORDER SUMMARY", font=("Arial", 36, "bold"), bg="white").pack(
            anchor="w", padx=24, pady=(14, 10)
        )
        content = tk.Frame(view, bg="white")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        car = selection["car"]
        car_panel = tk.Frame(content, bg="white")
        car_panel.pack(side="left", fill="both", expand=True, padx=(0, 28))
        photo = self._load_image(
            car,
            size=(520, 350),
            colour=selection["carColour"],
        )
        if photo:
            image_label = tk.Label(car_panel, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(fill="both", expand=True)
        tk.Label(car_panel, text=str(car.get("model", "Car")), font=("Arial", 24), bg="white").pack(pady=8)
        tk.Label(
            car_panel,
            text=f"CONFIGURATION ID: {booking_id}",
            font=("Arial", 17, "bold"),
            bg=PANEL,
            padx=10,
            pady=8,
        ).pack(pady=8)
        tk.Label(
            car_panel,
            text="Your selection is ready for billing. Payment processing is not configured in this demo.",
            font=("Arial", 14),
            bg="white",
            wraplength=480,
            justify="center",
        ).pack(pady=8)
        specs_panel = tk.Frame(content, bg="white")
        specs_panel.pack(side="right", fill="both", expand=True)
        self._render_configuration_table(specs_panel, selection)
        actions = tk.Frame(view, bg="white")
        actions.pack(fill="x", padx=24, pady=(0, 18))
        tk.Button(
            actions,
            text="Back to comparison",
            font=("Arial", 14),
            command=self.show_comparison,
        ).pack(side="left")
        tk.Button(
            actions,
            text="Back to catalog",
            font=("Arial", 14),
            command=self.show_catalog,
        ).pack(side="right")

    def _render_configuration_table(self, parent: tk.Frame, selection: dict[str, Any]) -> None:
        car = selection["car"]
        rows = [
            ("CRITERIAS", str(car.get("model", "Car")).upper()),
            ("CAR COLOUR", selection["carColour"]),
            ("SEAT COLOUR", selection["seatColour"]),
            ("TYRE SIZE", selection["tyreSize"]),
            ("DIMENSIONS (mm)", str(car.get("dimensions", car.get("details", {}).get("dimensions", "Not listed")))),
            ("FEATURES", ", ".join(str(feature) for feature in car.get("features", car.get("details", {}).get("features", [])))),
            ("ENGINE TYPE", str(car.get("specs", {}).get("engine", car.get("details", {}).get("engine", "Not listed")))),
            ("MILEAGE", str(car.get("mileage", car.get("details", {}).get("mileage", "Not listed")))),
            ("HIGHEST SPEED", str(car.get("highestSpeed", car.get("details", {}).get("highestSpeed", "Not listed")))),
            ("PRICE", str(car.get("displayPrice", self._format_price(car.get("price", ""))))),
            ("TYPE OF CAR", str(car.get("category", car.get("details", {}).get("category", "Not listed")))),
        ]
        for row, (label, value) in enumerate(rows):
            for column, text in enumerate((label, value)):
                tk.Label(
                    parent,
                    text=text,
                    font=("Arial", 13 if label in {"FEATURES", "DIMENSIONS (mm)", "ENGINE TYPE"} else 16),
                    bg=ACCENT if row == 0 else "white",
                    relief="solid",
                    bd=1,
                    padx=12,
                    pady=12,
                    wraplength=340,
                    justify="center",
                ).grid(row=row, column=column, sticky="nsew")
            parent.grid_rowconfigure(row, weight=1, uniform="summary-data")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=2)

    def _clear_view(self) -> None:
        for child in self.winfo_children():
            if getattr(child, "view_area", False):
                child.destroy()

    def _new_view(self) -> tk.Frame:
        view = tk.Frame(self, bg="white")
        view.view_area = True
        view.pack(fill="both", expand=True)
        return view

    def _set_detail_image(self, photo: ImageTk.PhotoImage) -> None:
        for child in self.detail_image_box.winfo_children():
            child.destroy()
        label = tk.Label(self.detail_image_box, image=photo, bg="white")
        label.image = photo
        label.pack(fill="both", expand=True)

    def _show_status(self, value: str) -> None:
        self.configure(cursor="arrow")

    @staticmethod
    def _car_colours(car: dict[str, Any]) -> list[str]:
        return {
            "CR-101": ["Black", "Red", "Silver", "Purple", "Pink", "Blue"],
            "CR-102": ["Black", "Red", "Blue", "Silver", "Yellow", "Turquoise"],
            "CR-103": ["Black", "Red", "Blue", "White", "Silver", "Burgundy"],
            "CR-104": ["Black", "Orange", "Blue", "Silver", "White", "Brown"],
            "CR-105": ["Black", "Red", "White", "Blue", "Silver", "Pink"],
            "CR-106": ["Black", "Green", "Red", "Blue", "Silver", "Yellow"],
        }.get(str(car.get("carId", "")), ["Black", "Red", "Blue", "White", "Silver", "Yellow"])

    @staticmethod
    def _colour_value(value: str) -> str:
        return {
            "Black": "#111111",
            "Red": "#ff2633",
            "Blue": "#2110b5",
            "White": "#f4f4f4",
            "Silver": "#c9c9c9",
            "Yellow": "#ffd957",
            "Tan": "#b8733f",
            "Purple": "#3c267d",
            "Green": "#16b95b",
            "Pink": "#d61d8d",
            "Cyan": "#32c8bd",
            "Turquoise": "#36c8ba",
            "Orange": "#f59b54",
            "Brown": "#a54f2c",
            "Burgundy": "#7d111d",
        }.get(value, "#dddddd")

    @staticmethod
    def _format_price(price: object) -> str:
        if isinstance(price, str) and price:
            return price
        if isinstance(price, (int, float)):
            text = str(int(price))
            if len(text) <= 3:
                return f"₹{text}"
            last_three = text[-3:]
            remaining = text[:-3]
            groups: list[str] = []
            while remaining:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            return f"₹{','.join(groups + [last_three])}"
        return "Price unavailable"

    def _render_specs(self, parent: tk.Frame, car: dict[str, Any]) -> None:
        details = car.get("details", {})
        tk.Label(parent, text="Specifications", font=("Arial", 21, "bold"), bg=PANEL).pack(anchor="w", pady=(0, 12))
        rows = [
            ("Engine", car.get("specs", {}).get("engine", details.get("engine", "Not listed"))),
            ("Colour", car.get("specs", {}).get("color", "Not listed")),
            ("Dimensions", car.get("dimensions", details.get("dimensions", "Not listed"))),
            ("Mileage", car.get("mileage", details.get("mileage", "Not listed"))),
            ("Highest speed", car.get("highestSpeed", details.get("highestSpeed", "Not listed"))),
        ]
        for label, value in rows:
            tk.Label(parent, text=label, font=("Arial", 14, "bold"), bg=PANEL).pack(anchor="w", pady=(8, 0))
            tk.Label(parent, text=str(value), font=("Arial", 13), bg=PANEL, wraplength=235, justify="left").pack(anchor="w")
        features = car.get("features", details.get("features", []))
        if features:
            tk.Label(parent, text="Features", font=("Arial", 14, "bold"), bg=PANEL).pack(anchor="w", pady=(10, 0))
            tk.Label(parent, text="\n".join(f"- {feature}" for feature in features), font=("Arial", 13), bg=PANEL, justify="left", wraplength=235).pack(anchor="w")

    def _load_image(
        self,
        car: dict[str, Any],
        size: tuple[int, int] = (230, 125),
        colour: str | None = None,
    ) -> ImageTk.PhotoImage | None:
        images = car.get("images", [])
        local_fallback = IMAGE_FILES.get(str(car.get("carId", "")))
        image_references = []
        customization_path = CUSTOMIZATION_FILES.get(str(car.get("carId", "")))
        customization_reference = None
        if colour and customization_path:
            customization_reference = str(Path(__file__).resolve().parent / customization_path)
            image_references.append(customization_reference)
        if local_fallback:
            image_references.append(
                str(Path(__file__).resolve().parent / local_fallback)
            )
        image_references.extend(
            str(reference)
            for reference in images
            if str(reference) != local_fallback
        )

        image = None
        for image_reference in image_references:
            try:
                if image_reference.startswith(("http://", "https://")):
                    with urlopen(image_reference, timeout=5) as response:
                        candidate = Image.open(BytesIO(response.read()))
                        candidate.load()
                else:
                    path = Path(image_reference)
                    if not path.is_absolute():
                        path = Path(__file__).resolve().parent / path
                    if not path.exists():
                        for extension in (".png", ".jpg", ".jpeg", ".webp"):
                            alternative = path.with_suffix(extension)
                            if alternative.exists():
                                path = alternative
                                break
                    candidate = Image.open(path)
                    candidate.load()
                image = candidate
                break
            except (OSError, ValueError, TimeoutError):
                continue

        if image is None:
            return None
        if colour and customization_reference == image_reference:
            colours = self._car_colours(car)
            if colour in colours:
                index = colours.index(colour)
                width, height = image.size
                content_height = int(height * 0.84)
                image = image.crop(
                    ((index % 2) * width // 2, (index // 2) * content_height // 3,
                     (index % 2 + 1) * width // 2, (index // 2 + 1) * content_height // 3)
                )
                image = self._trim_image_margins(image)
        if colour and customization_reference == image_reference:
            image = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
            image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=125, threshold=3))
        else:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image, master=self.winfo_toplevel())
        self.image_references.append(photo)
        return photo

    @staticmethod
    def _trim_image_margins(image: Image.Image) -> Image.Image:
        background = Image.new("RGB", image.size, "white")
        difference = ImageChops.difference(image.convert("RGB"), background)
        mask = difference.convert("L").point(lambda value: 255 if value > 10 else 0)
        bounds = mask.getbbox()
        if not bounds:
            return image
        left, top, right, bottom = bounds
        padding = 8
        return image.crop(
            (max(0, left - padding), max(0, top - padding),
             min(image.width, right + padding), min(image.height, bottom + padding))
        )

    @staticmethod
    def _car_text(car: dict[str, Any]) -> str:
        return " ".join(str(value) for value in car.values())


def open_catalog(root: tk.Tk) -> CatalogPage:
    page = CatalogPage(root)
    page.pack(fill="both", expand=True)
    return page
