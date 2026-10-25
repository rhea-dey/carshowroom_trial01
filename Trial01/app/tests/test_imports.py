from app.main import CarShowroomBackend
from app.services.auth_service import AuthService


def test_backend_imports():
    backend = CarShowroomBackend()
    assert backend is not None
    assert isinstance(backend.auth_service, AuthService)
