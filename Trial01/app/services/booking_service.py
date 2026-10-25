from __future__ import annotations

from app.repositories.in_memory_repository import InMemoryRepository


class BookingService:
    def __init__(self, repository: InMemoryRepository):
        self.repository = repository

    def add_to_cart(self, customer_id: str, pi_info: dict[str, object]) -> str:
        if "carId" not in pi_info:
            raise ValueError("carId is required")
        if "customizations" not in pi_info:
            raise ValueError("customizations are required")
        if pi_info["carId"] not in self.repository.cars:
            raise ValueError("Car not found")
        return self.repository.add_cart_item(customer_id, pi_info)

    def trigger_booking(self, customer_id: str, car_id: str) -> str:
        if car_id not in self.repository.cars:
            raise ValueError("Car not found")
        return self.repository.add_booking(customer_id, car_id)

    def get_cart(self, cart_id: str) -> dict[str, object]:
        cart = self.repository.get_cart(cart_id)
        if cart is None:
            raise ValueError(f"Cart {cart_id} not found")
        return cart

    def get_order(self, booking_id: str) -> dict[str, object]:
        order = self.repository.get_order(booking_id)
        if order is None:
            raise ValueError(f"Order {booking_id} not found")
        return order

    def get_custom_info(self, pi_info: object) -> dict[str, object]:
        if not isinstance(pi_info, dict):
            return {
                "cartInfo": {"carId": "", "details": {}},
                "orderInfo": {"bookingId": "", "status": ""},
            }
        car_id = pi_info.get("carId", "")
        details = pi_info.get("details", {})
        booking_id = pi_info.get("bookingId", "")
        status = pi_info.get("status", "pending")
        return {
            "cartInfo": {"carId": car_id, "details": details},
            "orderInfo": {"bookingId": booking_id, "status": status},
        }
