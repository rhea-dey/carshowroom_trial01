from app.main import backend


def test_login_function():
    payload = backend.login("salesrep1", "password123")
    assert payload["success"] is True
    assert payload["salesRepName"] == "Alice Johnson"


def test_catalog_function():
    payload = backend.fetch_catalog()
    assert "cars" in payload
    assert len(payload["cars"]) > 0


def test_cardetail_function():
    payload = backend.fetch_car_detail("CR-101")
    assert payload["carId"] == "CR-101"
    assert "details" in payload


def test_cart_and_booking_functions():
    cart_payload = backend.add_to_cart(
        "CUST-1001",
        {
            "carId": "CR-101",
            "customizations": {"engine": "2.0L Turbo", "color": "Midnight Blue"},
        },
    )
    assert "cartId" in cart_payload

    booking_payload = backend.trigger_booking("CUST-1001", "CR-101")
    assert "bookingId" in booking_payload


def test_lookup_functions():
    cart_payload = backend.fetch_cart("cart-001")
    assert cart_payload["cartId"] == "cart-001"

    order_payload = backend.fetch_order("booking-001")
    assert order_payload["bookingId"] == "booking-001"
