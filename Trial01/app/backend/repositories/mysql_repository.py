from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import mysql.connector

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.backend.repositories.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from app.backend.repositories.setup_repo import setup_repository


IMAGE_FILES = {
    "CR-101": "images/panther-gls-130.png",
    "CR-102": "images/rockrover-rl.png",
    "CR-103": "images/falcon-x.png",
    "CR-104": "images/quid-z-300.png",
    "CR-105": "images/rlv-minora.png",
    "CR-106": "images/fenty-500.png",
}


class MySqlRepository:
    """MySQL-backed repository for showroom data."""

    def __init__(self) -> None:
        self.config = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME,
        }
        setup_repository()

    def _connect(self):
        return mysql.connector.connect(**self.config)

    def validate_login(self, username: str, password: str) -> str | None:
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT name FROM users WHERE username = %s AND password = %s",
                (username, password),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            connection.close()

    def get_catalog(self) -> list[dict[str, Any]]:
        connection = self._connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT cars.*
                FROM cars
                ORDER BY cars.id
                """
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        catalog: dict[str, dict[str, Any]] = {}
        for row in rows:
            car = catalog.setdefault(
                row["car_id"],
                {
                    "carId": row["car_id"],
                    "model": row["model"],
                    "price": row["price"],
                    "displayPrice": self._format_price(row["price"]),
                    "specs": {"engine": row["engine"], "color": row["color"]},
                    "description": row["category"],
                    "category": row["category"],
                    "fuelCapacity": row["fuel_capacity"],
                    "dimensions": row["dimensions"],
                    "features": row["features"].split("; "),
                    "mileage": row["mileage"],
                    "highestSpeed": row["highest_speed"],
                    "details": {
                        "category": row["category"],
                        "fuelCapacity": row["fuel_capacity"],
                        "dimensions": row["dimensions"],
                        "features": row["features"].split("; "),
                        "engine": row["engine"],
                        "mileage": row["mileage"],
                        "highestSpeed": row["highest_speed"],
                    },
                    "images": [IMAGE_FILES[row["car_id"]]],
                },
            )
        return list(catalog.values())

    def add_cart_item(self, customer_id: str, pi_info: dict[str, Any]) -> str:
        car_id = str(pi_info["carId"])
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT price FROM cars WHERE car_id = %s", (car_id,))
            car = cursor.fetchone()
            if car is None:
                raise ValueError("Car not found")

            cart_id = f"cart-{uuid4().hex}"
            cursor.execute(
                "INSERT INTO carts (cart_id, customer_id) VALUES (%s, %s)",
                (cart_id, customer_id),
            )
            cursor.execute(
                """
                INSERT INTO cart_items
                    (cart_id, car_id, customizations, price)
                VALUES (%s, %s, %s, %s)
                """,
                (cart_id, car_id, json.dumps(pi_info["customizations"]), car[0]),
            )
            connection.commit()
            return cart_id
        finally:
            cursor.close()
            connection.close()

    def get_cart(self, cart_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cart_id, customer_id FROM carts WHERE cart_id = %s",
                (cart_id,),
            )
            cart = cursor.fetchone()
            if cart is None:
                return None

            cursor.execute(
                """
                SELECT car_id, customizations, price
                FROM cart_items
                WHERE cart_id = %s
                ORDER BY id
                """,
                (cart_id,),
            )
            items = [
                {
                    "carId": row["car_id"],
                    "customizations": json.loads(row["customizations"]),
                    "price": float(row["price"]),
                }
                for row in cursor.fetchall()
            ]
            return {
                "cartId": cart["cart_id"],
                "customerId": cart["customer_id"],
                "items": items,
            }
        finally:
            cursor.close()
            connection.close()

    def add_booking(self, customer_id: str, car_id: str) -> str:
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM cars WHERE car_id = %s", (car_id,))
            if cursor.fetchone() is None:
                raise ValueError("Car not found")

            booking_id = f"booking-{uuid4().hex}"
            confirmation_date = (
                datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            )
            cursor.execute(
                """
                INSERT INTO orders
                    (booking_id, customer_id, car_id, status, confirmation_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (booking_id, customer_id, car_id, "pending", confirmation_date),
            )
            connection.commit()
            return booking_id
        finally:
            cursor.close()
            connection.close()

    def get_order(self, booking_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT booking_id, customer_id, car_id, status, confirmation_date
                FROM orders
                WHERE booking_id = %s
                """,
                (booking_id,),
            )
            order = cursor.fetchone()
            if order is None:
                return None
            return {
                "bookingId": order["booking_id"],
                "carId": order["car_id"],
                "customerId": order["customer_id"],
                "status": order["status"],
                "confirmationDate": order["confirmation_date"],
            }
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _format_price(price: Any) -> str:
        if price is None:
            return "Price unavailable"
        numeric_price = float(price)
        text = str(int(numeric_price))
        if len(text) <= 3:
            return f"₹{text}"
        last_three = text[-3:]
        remaining = text[:-3]
        groups: list[str] = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        return f"₹{','.join(groups + [last_three])}"

    def get_car_detail(self, car_id: str) -> dict[str, Any] | None:
        return next((car for car in self.get_catalog() if car["carId"] == car_id), None)
