from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


def _format_rupees(amount: int | float) -> str:
    text = str(int(amount))
    if len(text) <= 3:
        return f"₹{text}"
    last_three = text[-3:]
    remaining = text[:-3]
    groups: list[str] = []
    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    return f"₹{','.join(groups + [last_three])}"


IMAGE_FILES = {
    "CR-101": "images/panther-gls-130.png",
    "CR-102": "images/rockrover-rl.png",
    "CR-103": "images/falcon-x.png",
    "CR-104": "images/quid-z-300.png",
    "CR-105": "images/rlv-minora.png",
    "CR-106": "images/fenty-500.png",
}


def _default_cars() -> dict[str, dict[str, Any]]:
    cars = [
        ("CR-101", "Panther GLS 130", 12500000, "Sedan Sports Car", "50L-57L", "Blue", "Twin-Turbo V6; 6 Cylinders; Petrol; 350-500 hp", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Seat Warmers", "7-9 km/l", "300 km/hr", "panther-gls-130.png"),
        ("CR-102", "RockRover RL", 24000000, "Sedan Sports Car", "45L-50L", "Red", "3.0L twin turbo V6 petrol engine; 7-speed automatic transmission; RWD", "Length: 4,500-4,600 mm; Width: 1,800-1,890 mm; Height: 1,200-1,250 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Aerodynamic body kit; ABS (anti-lock braking system)", "11-13 km/l", "310 km/hr", "rockrover-rl.png"),
        ("CR-103", "Falcon X", 8500000, "Family SUV Car", "65L-67L", "Black", "2.5L Twin-Turbo V6; 6 Cylinders; Diesel; 320-420 hp", "Length: 4,600-4,800 mm; Width: 1,900-1,950 mm; Height: 1,700-1,780 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Panoramic sunroof", "13-14 km/l", "260 km/hr", "falcon-x.png"),
        ("CR-104", "Quid Z-300", 4200000, "Family Sedan Car", "56L-60L", "Blue", "2.0L turbo inline-4; 4 Cylinders; Petrol; 220-310 hp", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ample Trunk Space; Rear parking sensors", "15-16 km/l", "240 km/hr", "quid-z-300.png"),
        ("CR-105", "RLV Minora", 18000000, "Sedan Sports Car", "70L-73L", "White", "Supercharged V8; 8 cylinders; Petrol; 600-800 hp", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ambient Lighting; Rear parking sensors", "8-10 km/l", "305 km/hr", "rlv-minora.png"),
        ("CR-106", "Fenty 500", 9500000, "Family Sedan Car", "35L-40L", "Silver", "Hybrid Powertrain; V6 + Electric Motor; Petrol + Electric; 400-600 hp", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Charging Port; Dual-Zone AC; Ambient Lighting; Keyless Entry; Ample Trunk Space", "8-10 km/l", "200 km/hr", "fenty-500.png"),
    ]
    return {
        car_id: {
            "carId": car_id,
            "model": model,
            "price": price,
            "displayPrice": _format_rupees(price),
            "category": category,
            "fuelCapacity": fuel_capacity,
            "specs": {"engine": engine, "color": colour},
            "dimensions": dimensions,
            "features": features.split("; "),
            "mileage": mileage,
            "highestSpeed": highest_speed,
            "details": {
                "category": category,
                "fuelCapacity": fuel_capacity,
                "dimensions": dimensions,
                "features": features.split("; "),
                "engine": engine,
                "mileage": mileage,
                "highestSpeed": highest_speed,
            },
            "images": [
                f"{os.getenv('AZURE_STORAGE_PUBLIC_BASE_URL', '').rstrip('/')}/{car_id}/{image_name}"
            ] if os.getenv("AZURE_STORAGE_PUBLIC_BASE_URL") else [IMAGE_FILES[car_id]],
        }
        for car_id, model, price, category, fuel_capacity, colour, engine, dimensions, features, mileage, highest_speed, image_name in cars
    }


@dataclass
class InMemoryRepository:
    """Repository abstraction for future database swap-in.

    The current implementation uses an in-memory store to satisfy the PRD contracts
    without requiring a live database connection.
    """

    users: dict[str, dict[str, str]] = field(
        default_factory=lambda: {
            "salesrep1": {"password": "password123", "name": "Rhea Dey"},
            "salesrep2": {"password": "password456", "name": "Sumit Dey"},
        }
    )

    cars: dict[str, dict[str, Any]] = field(default_factory=_default_cars)

    carts: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "cart-001": {
                "cartId": "cart-001",
                "customerId": "CUST-1001",
                "items": [
                    {
                        "carId": "CR-101",
                        "customizations": {"engine": "2.0L Turbo", "color": "Midnight Blue"},
                        "price": 24999.0,
                    }
                ],
            }
        }
    )

    orders: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "booking-001": {
                "bookingId": "booking-001",
                "carId": "CR-101",
                "customerId": "CUST-1001",
                "status": "confirmed",
                "confirmationDate": "2026-08-16T00:00:00Z",
            }
        }
    )

    def validate_login(self, username: str, password: str) -> str | None:
        user = self.users.get(username)
        if not user:
            return None
        if user["password"] != password:
            return None
        return user["name"]

    def get_catalog(self) -> list[dict[str, Any]]:
        return list(self.cars.values())

    def get_car_detail(self, car_id: str) -> dict[str, Any] | None:
        return self.cars.get(car_id)

    def add_cart_item(self, customer_id: str, pi_info: dict[str, Any]) -> str:
        cart_id = f"cart-{len(self.carts) + 1:03d}"
        item = {
            "carId": pi_info["carId"],
            "customizations": pi_info["customizations"],
            "price": self.cars[pi_info["carId"]]["price"],
        }
        self.carts[cart_id] = {
            "cartId": cart_id,
            "customerId": customer_id,
            "items": [item],
        }
        return cart_id

    def get_cart(self, cart_id: str) -> dict[str, Any] | None:
        return self.carts.get(cart_id)

    def add_booking(self, customer_id: str, car_id: str) -> str:
        booking_id = f"booking-{len(self.orders) + 1:03d}"
        self.orders[booking_id] = {
            "bookingId": booking_id,
            "carId": car_id,
            "customerId": customer_id,
            "status": "pending",
            "confirmationDate": "2026-08-16T00:00:00Z",
        }
        return booking_id

    def get_order(self, booking_id: str) -> dict[str, Any] | None:
        return self.orders.get(booking_id)
