"""Application configuration and environment settings."""

import os
from pathlib import Path


def _load_environment_file(path: Path) -> None:
    if not path.is_file():
        return

    with path.open(encoding="utf-8-sig") as environment_file:
        for line_number, line in enumerate(environment_file, start=1):
            entry = line.strip()
            if not entry or entry.startswith("#"):
                continue

            key, separator, value = entry.partition("=")
            key = key.strip()
            invalid_key = (
                not key
                or not key.replace("_", "a").isalnum()
                or key[0].isdigit()
            )
            if not separator or invalid_key:
                raise ValueError(f"Invalid environment entry in {path} at line {line_number}")

            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            os.environ.setdefault(key, value)


_load_environment_file(Path(__file__).resolve().parents[1] / ".env")

APP_NAME = "CarShowRoom API"
APP_VERSION = "1.0.0"
DB_HOST = os.getenv("CARSHOWROOM_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("CARSHOWROOM_DB_PORT", "3306"))
DB_USER = os.getenv("CARSHOWROOM_DB_USER", "root")
DB_PASSWORD = os.getenv("CARSHOWROOM_DB_PASSWORD", "")
DB_NAME = os.getenv("CARSHOWROOM_DB_NAME", "car_showroom")
