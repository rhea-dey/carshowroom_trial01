"""Initialize missing MySQL repository databases and tables."""

import mysql.connector

from app.backend.repositories.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


TABLE_DEFINITIONS = {
    "cars": """
        CREATE TABLE cars (
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
    """,
    "users": """
        CREATE TABLE users (
            username VARCHAR(100) PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL
        )
    """,
    "carts": """
        CREATE TABLE carts (
            cart_id VARCHAR(100) PRIMARY KEY,
            customer_id VARCHAR(100) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "cart_items": """
        CREATE TABLE cart_items (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            cart_id VARCHAR(100) NOT NULL,
            car_id VARCHAR(20) NOT NULL,
            customizations TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            UNIQUE KEY uq_cart_car (cart_id, car_id),
            FOREIGN KEY (cart_id) REFERENCES carts (cart_id) ON DELETE CASCADE,
            FOREIGN KEY (car_id) REFERENCES cars (car_id)
        )
    """,
    "orders": """
        CREATE TABLE orders (
            booking_id VARCHAR(100) PRIMARY KEY,
            customer_id VARCHAR(100) NOT NULL,
            car_id VARCHAR(20) NOT NULL,
            status VARCHAR(50) NOT NULL,
            confirmation_date VARCHAR(40) NOT NULL,
            FOREIGN KEY (car_id) REFERENCES cars (car_id)
        )
    """,
}

CARS = [
    ("CR-101", "Panther GLS 130", 12500000, "Twin-Turbo V6; 6 Cylinders; Petrol; 350-500 hp", "Blue", "Sedan Sports Car", "50L-57L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Seat Warmers", "7-9 km/l", "300 km/hr"),
    ("CR-102", "RockRover RL", 24000000, "3.0L twin turbo V6 petrol engine; 7-speed automatic transmission; RWD", "Red", "Sedan Sports Car", "45L-50L", "Length: 4,500-4,600 mm; Width: 1,800-1,890 mm; Height: 1,200-1,250 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Aerodynamic body kit; ABS (anti-lock braking system)", "11-13 km/l", "310 km/hr"),
    ("CR-103", "Falcon X", 8500000, "2.5L Twin-Turbo V6; 6 Cylinders; Diesel; 320-420 hp", "Black", "Family SUV Car", "65L-67L", "Length: 4,600-4,800 mm; Width: 1,900-1,950 mm; Height: 1,700-1,780 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Panoramic sunroof", "13-14 km/l", "260 km/hr"),
    ("CR-104", "Quid Z-300", 4200000, "2.0L turbo inline-4; 4 Cylinders; Petrol; 220-310 hp", "Blue", "Family Sedan Car", "56L-60L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ample Trunk Space; Rear parking sensors", "15-16 km/l", "240 km/hr"),
    ("CR-105", "RLV Minora", 18000000, "Supercharged V8; 8 cylinders; Petrol; 600-800 hp", "White", "Sedan Sports Car", "70L-73L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ambient Lighting; Rear parking sensors", "8-10 km/l", "305 km/hr"),
    ("CR-106", "Fenty 500", 9500000, "Hybrid Powertrain; V6 + Electric Motor; Petrol + Electric; 400-600 hp", "Silver", "Family Sedan Car", "35L-40L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Charging Port; Dual-Zone AC; Ambient Lighting; Keyless Entry; Ample Trunk Space", "8-10 km/l", "200 km/hr"),
]


def _create_missing_tables(cursor, existing_tables: set[str]) -> set[str]:
    missing_tables = {
        table_name
        for table_name in TABLE_DEFINITIONS
        if table_name not in existing_tables
    }
    for table_name, definition in TABLE_DEFINITIONS.items():
        if table_name in missing_tables:
            cursor.execute(definition)
    return missing_tables


def _seed_cars(cursor) -> None:
    cursor.executemany(
        """
        INSERT INTO cars
        (car_id, model, price, engine, color, category, fuel_capacity, dimensions,
         features, mileage, highest_speed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        CARS,
    )


def _seed_users(cursor) -> None:
    cursor.executemany(
        "INSERT INTO users (username, password, name) VALUES (%s, %s, %s)",
        [
            ("salesrep1", "password123", "Rhea Dey"),
            ("salesrep2", "password456", "Sumit Dey"),
        ],
    )


def _seed_cart(cursor) -> None:
    cursor.execute(
        "INSERT IGNORE INTO carts (cart_id, customer_id) VALUES (%s, %s)",
        ("cart-001", "CUST-1001"),
    )
    cursor.execute(
        """
        INSERT IGNORE INTO cart_items
            (cart_id, car_id, customizations, price)
        VALUES (%s, %s, %s, %s)
        """,
        (
            "cart-001",
            "CR-101",
            '{"engine": "2.0L Turbo", "color": "Midnight Blue"}',
            24999.0,
        ),
    )


def _seed_order(cursor) -> None:
    cursor.execute(
        """
        INSERT IGNORE INTO orders
            (booking_id, customer_id, car_id, status, confirmation_date)
        VALUES (%s, %s, %s, %s, %s)
        """,
        ("booking-001", "CUST-1001", "CR-101", "confirmed", "2026-08-16T00:00:00Z"),
    )


def setup_repository() -> bool:
    """Create missing database objects and seed defaults for newly created tables."""
    server_config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    connection = mysql.connector.connect(**server_config)
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = %s",
                (DB_NAME,),
            )
            database_created = cursor.fetchone() is None
            if database_created:
                cursor.execute(f"CREATE DATABASE `{DB_NAME}`")
                connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()

    connection = mysql.connector.connect(**{**server_config, "database": DB_NAME})
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SHOW TABLES")
            existing_tables = {row[0] for row in cursor.fetchall()}
            missing_tables = _create_missing_tables(cursor, existing_tables)

            if "cars" in missing_tables:
                _seed_cars(cursor)
            if "users" in missing_tables:
                _seed_users(cursor)
            if {"carts", "cart_items"} & missing_tables:
                _seed_cart(cursor)
            if "orders" in missing_tables:
                _seed_order(cursor)

            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()

    return database_created or bool(missing_tables)


if __name__ == "__main__":
    if setup_repository():
        print(f"Repository database '{DB_NAME}' initialized or updated.")
    else:
        print(f"Database '{DB_NAME}' and all repository tables already exist.")
