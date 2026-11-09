
from app.repositories.in_memory_repository import InMemoryRepository


class AuthService:
    def __init__(self, repository: InMemoryRepository):
        self.repository = repository

    def login(self, username: str, password: str) -> dict[str, bool | str]:
        rep_name = self.repository.validate_login(username, password)
        if rep_name is None:
            raise ValueError("Invalid username or password")
        return {"success": True, "salesRepName": rep_name}
