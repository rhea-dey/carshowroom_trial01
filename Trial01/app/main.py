
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.repositories.in_memory_repository import InMemoryRepository
from app.repositories.mysql_repository import MySqlRepository
from app.services.auth_service import AuthService
from app.services.booking_service import BookingService
from app.services.catalog_service import CatalogService


class CarShowroomBackend:
    """Pure Python backend service for Tkinter or other local frontends.

    This class exposes the PRD-defined functional endpoints as methods instead of
    HTTP routes, so it can be called directly from a desktop application.
    """

    def __init__(self, repository: InMemoryRepository | None = None):
        self.repository = repository or MySqlRepository()
        self.auth_service = AuthService(self.repository)
        self.catalog_service = CatalogService(self.repository)
        self.booking_service = BookingService(self.repository)

    def login(self, username: str, password: str) -> dict[str, bool | str]:
        return self.auth_service.login(username, password)

    def fetch_catalog(self) -> dict[str, list[dict[str, object]]]:
        return {"cars": self.catalog_service.get_catalog()}

    def fetch_car_detail(self, car_id: str) -> dict[str, object]:
        return self.catalog_service.get_car_detail(car_id)

    def add_to_cart(self, customer_id: str, pi_info: dict[str, object]) -> dict[str, str]:
        cart_id = self.booking_service.add_to_cart(customer_id, pi_info)
        return {"cartId": cart_id}

    def trigger_booking(self, customer_id: str, car_id: str) -> dict[str, str]:
        booking_id = self.booking_service.trigger_booking(customer_id, car_id)
        return {"bookingId": booking_id}

    def fetch_custom_info(self, pi_info: object | None = None) -> dict[str, dict[str, object]]:
        return self.booking_service.get_custom_info(pi_info)

    def fetch_cart(self, cart_id: str) -> dict[str, object]:
        return self.booking_service.get_cart(cart_id)

    def fetch_order(self, booking_id: str) -> dict[str, object]:
        return self.booking_service.get_order(booking_id)


backend = CarShowroomBackend()

__all__ = ["CarShowroomBackend", "backend"]

def test_login_function():
    payload = backend.login("salesrep1", "password123")
    assert payload["success"] is True
    assert payload["salesRepName"] == "Rhea Dey"

test_login_function()