from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import mysql.connector

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.repositories.in_memory_repository import InMemoryRepository
from app.repositories.in_memory_repository import IMAGE_FILES
from app.services.blob_storage import BlobStorageService


class MySqlRepository(InMemoryRepository):
    """MySQL catalog repository with the existing in-memory booking data."""

    def __init__(self):
        super().__init__()
        self.image_storage = BlobStorageService()
        self.config = {
            "host": os.getenv("CARSHOWROOM_DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("CARSHOWROOM_DB_PORT", "3306")),
            "user": os.getenv("CARSHOWROOM_DB_USER", "root"),
            "password": os.getenv("CARSHOWROOM_DB_PASSWORD", "admin"),
            "database": os.getenv("CARSHOWROOM_DB_NAME", "car_showroom"),
        }
        self._create_database()
        self._create_tables()
        self._seed_cars()

    def _connect(self, include_database: bool = True):
        config = self.config.copy()
        if not include_database:
            config.pop("database")
        return mysql.connector.connect(**config)

    def _create_database(self) -> None:
        connection = self._connect(include_database=False)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}`")
        connection.commit()
        cursor.close()
        connection.close()

    def _create_tables(self) -> None:
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_id VARCHAR(20) NOT NULL UNIQUE,
                model VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL DEFAULT 0,
                engine TEXT NOT NULL,
                color VARCHAR(100) NOT NULL,
                description VARCHAR(255) NOT NULL DEFAULT '',
                category VARCHAR(100) NOT NULL,
                fuel_capacity VARCHAR(50) NOT NULL,
                dimensions TEXT NOT NULL,
                features TEXT NOT NULL,
                mileage VARCHAR(50) NOT NULL,
                highest_speed VARCHAR(50) NOT NULL
            )
            """
        )
        cursor.execute(
            "ALTER TABLE cars MODIFY COLUMN description VARCHAR(255) NOT NULL DEFAULT ''"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS car_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                car_id VARCHAR(20) NOT NULL,
                image_path VARCHAR(500) NOT NULL,
                FOREIGN KEY (car_id) REFERENCES cars(car_id)
            )
            """
        )
        connection.commit()
        cursor.close()
        connection.close()

    def _seed_cars(self) -> None:
        cars = [
            ("CR-101", "Panther GLS 130", 12500000, "Twin-Turbo V6; 6 Cylinders; Petrol; 350-500 hp", "Blue", "Sedan Sports Car", "50L-57L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Seat Warmers", "7-9 km/l", "300 km/hr"),
            ("CR-102", "RockRover RL", 24000000, "3.0L twin turbo V6 petrol engine; 7-speed automatic transmission; RWD", "Red", "Sedan Sports Car", "45L-50L", "Length: 4,500-4,600 mm; Width: 1,800-1,890 mm; Height: 1,200-1,250 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Aerodynamic body kit; ABS (anti-lock braking system)", "11-13 km/l", "310 km/hr"),
            ("CR-103", "Falcon X", 8500000, "2.5L Twin-Turbo V6; 6 Cylinders; Diesel; 320-420 hp", "Black", "Family SUV Car", "65L-67L", "Length: 4,600-4,800 mm; Width: 1,900-1,950 mm; Height: 1,700-1,780 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Panoramic sunroof", "13-14 km/l", "260 km/hr"),
            ("CR-104", "Quid Z-300", 4200000, "2.0L turbo inline-4; 4 Cylinders; Petrol; 220-310 hp", "Blue", "Family Sedan Car", "56L-60L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ample Trunk Space; Rear parking sensors", "15-16 km/l", "240 km/hr"),
            ("CR-105", "RLV Minora", 18000000, "Supercharged V8; 8 cylinders; Petrol; 600-800 hp", "White", "Sedan Sports Car", "70L-73L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ambient Lighting; Rear parking sensors", "8-10 km/l", "305 km/hr"),
            ("CR-106", "Fenty 500", 9500000, "Hybrid Powertrain; V6 + Electric Motor; Petrol + Electric; 400-600 hp", "Silver", "Family Sedan Car", "35L-40L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Charging Port; Dual-Zone AC; Ambient Lighting; Keyless Entry; Ample Trunk Space", "8-10 km/l", "200 km/hr"),
        ]
        connection = self._connect()
        cursor = connection.cursor()
        cursor.executemany(
            """
            INSERT INTO cars
            (car_id, model, price, engine, color, category, fuel_capacity, dimensions,
             features, mileage, highest_speed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                model=VALUES(model), price=VALUES(price), engine=VALUES(engine), color=VALUES(color),
                category=VALUES(category), fuel_capacity=VALUES(fuel_capacity),
                dimensions=VALUES(dimensions), features=VALUES(features),
                mileage=VALUES(mileage), highest_speed=VALUES(highest_speed)
            """,
            cars,
        )
        connection.commit()
        cursor.close()
        connection.close()

    def get_catalog(self) -> list[dict[str, Any]]:
        connection = self._connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT cars.*, car_images.image_path
            FROM cars
            LEFT JOIN car_images ON cars.car_id = car_images.car_id
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
                    "images": [],
                },
            )
            if row["image_path"]:
                car["images"].append(row["image_path"])
            elif not car["images"]:
                car["images"].append(IMAGE_FILES[row["car_id"]])
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

    def add_image(self, car_id: str, image_path: str) -> None:
        stored_path = image_path
        if not image_path.startswith(("http://", "https://")):
            stored_path = self.image_storage.upload_image(image_path, car_id)
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO car_images (car_id, image_path) VALUES (%s, %s)",
            (car_id, stored_path),
        )
        connection.commit()
        cursor.close()
        connection.close()