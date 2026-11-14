"""Initialize the MySQL repository database on first use."""
import mysql.connector

from app.repositories.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

def _create_tables(cursor) -> None:
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


def _seed_cars(cursor) -> None:
    cars = [
        ("CR-101", "Panther GLS 130", 12500000, "Twin-Turbo V6; 6 Cylinders; Petrol; 350-500 hp", "Blue", "Sedan Sports Car", "50L-57L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Seat Warmers", "7-9 km/l", "300 km/hr"),
        ("CR-102", "RockRover RL", 24000000, "3.0L twin turbo V6 petrol engine; 7-speed automatic transmission; RWD", "Red", "Sedan Sports Car", "45L-50L", "Length: 4,500-4,600 mm; Width: 1,800-1,890 mm; Height: 1,200-1,250 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Aerodynamic body kit; ABS (anti-lock braking system)", "11-13 km/l", "310 km/hr"),
        ("CR-103", "Falcon X", 8500000, "2.5L Twin-Turbo V6; 6 Cylinders; Diesel; 320-420 hp", "Black", "Family SUV Car", "65L-67L", "Length: 4,600-4,800 mm; Width: 1,900-1,950 mm; Height: 1,700-1,780 mm", "Digital Screen; Charging port; Ambient Lighting; Reclinalbe Seats; Ample Trunk Space; Panoramic sunroof", "13-14 km/l", "260 km/hr"),
        ("CR-104", "Quid Z-300", 4200000, "2.0L turbo inline-4; 4 Cylinders; Petrol; 220-310 hp", "Blue", "Family Sedan Car", "56L-60L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ample Trunk Space; Rear parking sensors", "15-16 km/l", "240 km/hr"),
        ("CR-105", "RLV Minora", 18000000, "Supercharged V8; 8 cylinders; Petrol; 600-800 hp", "White", "Sedan Sports Car", "70L-73L", "Length: 4,300-4,600 mm; Width: 1,800-1,900 mm; Height: 1,200-1,300 mm", "Digital Screen; Keyless entry; Dual-zone AC; Reclinalbe Seats; Ambient Lighting; Rear parking sensors", "8-10 km/l", "305 km/hr"),
        ("CR-106", "Fenty 500", 9500000, "Hybrid Powertrain; V6 + Electric Motor; Petrol + Electric; 400-600 hp", "Silver", "Family Sedan Car", "35L-40L", "Length: 4,600-4,700 mm; Width: 1,800-1,810 mm; Height: 1,400-1,455 mm", "Digital Screen; Charging Port; Dual-Zone AC; Ambient Lighting; Keyless Entry; Ample Trunk Space", "8-10 km/l", "200 km/hr"),
    ]
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


def setup_repository() -> bool:
    """Create and seed the database only when it does not already exist."""
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
            if cursor.fetchone() is not None:
                return False
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()

    database_config = {**server_config, "database": DB_NAME}
    connection = mysql.connector.connect(**database_config)
    try:
        cursor = connection.cursor()
        try:
            _create_tables(cursor)
            _seed_cars(cursor)
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()
    return True


if __name__ == "__main__":
    if setup_repository():
        print(f"Created and initialized database '{DB_NAME}'.")
    else:
        print(f"Database '{DB_NAME}' already exists; setup skipped.")