from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import mysql.connector

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.repositories.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from app.repositories.in_memory_repository import InMemoryRepository
from app.repositories.in_memory_repository import IMAGE_FILES
from app.repositories.setup_repo import setup_repository


class MySqlRepository(InMemoryRepository):
    """MySQL catalog repository with the existing in-memory booking data."""

    def __init__(self):
        super().__init__()
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

    def get_catalog(self) -> list[dict[str, Any]]:
        connection = self._connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT cars.*
            FROM cars
            ORDER BY cars.id
            """
        )
        rows = cursor.fetchall()
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
