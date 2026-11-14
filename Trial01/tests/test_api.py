from app.backend.backend_service import backendservice
from app.backend.backend_service import CarShowroomBackend
from app.backend.services.auth_service import AuthService

def test_login_function():
    payload = backendservice.login("salesrep1", "password123")
    assert payload["success"] is True
    assert payload["salesRepName"] == "Rhea Dey"


def test_catalog_function():
    payload = backendservice.fetch_catalog()
    assert "cars" in payload
    assert len(payload["cars"]) > 0
    assert all(
        car["images"] and isinstance(car["images"][0], bytes)
        for car in payload["cars"]
    )
    assert all(
        car["customImages"] and isinstance(car["customImages"][0], bytes)
        for car in payload["cars"]
    )


def test_cardetail_function():
    payload = backendservice.fetch_car_detail("CR-101")
    assert payload["carId"] == "CR-101"
    assert "details" in payload


def test_cart_and_booking_functions():
    cart_payload = backendservice.add_to_cart(
        "CUST-1001",
        {
            "carId": "CR-101",
            "customizations": {"engine": "2.0L Turbo", "color": "Midnight Blue"},
        },
    )
    assert "cartId" in cart_payload
    cart = backendservice.fetch_cart(cart_payload["cartId"])
    assert cart["customerId"] == "CUST-1001"
    assert cart["items"][0]["customizations"]["color"] == "Midnight Blue"

    booking_payload = backendservice.trigger_booking("CUST-1001", "CR-101")
    assert "bookingId" in booking_payload
    order = backendservice.fetch_order(booking_payload["bookingId"])
    assert order["carId"] == "CR-101"
    assert order["status"] == "pending"


def test_lookup_functions():
    cart_payload = backendservice.fetch_cart("cart-001")
    assert cart_payload["cartId"] == "cart-001"

    order_payload = backendservice.fetch_order("booking-001")
    assert order_payload["bookingId"] == "booking-001"


def test_backend_imports():
    backend_instance = CarShowroomBackend()
    assert backend_instance is not None
    assert isinstance(backend_instance.auth_service, AuthService)