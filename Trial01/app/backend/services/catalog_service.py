from __future__ import annotations

from app.repositories.in_memory_repository import InMemoryRepository


class CatalogService:
    def __init__(self, repository: InMemoryRepository):
        self.repository = repository

    def get_catalog(self) -> list[dict[str, object]]:
        cars = self.repository.get_catalog()
        return cars

    def get_car_detail(self, car_id: str) -> dict[str, object]:
        car = self.repository.get_car_detail(car_id)
        if car is None:
            raise ValueError(f"Car {car_id} not found")
        return {"carId": car["carId"], "details": car["details"], "images": car.get("images", [])}
