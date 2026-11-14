from app.backend.repositories.mysql_repository import MySqlRepository

class AuthService:
    def __init__(self, repository: MySqlRepository):
        self.repository = repository

    def login(self, username: str, password: str) -> dict[str, bool | str]:
        rep_name = self.repository.validate_login(username, password)
        if rep_name is None:
            raise ValueError("Login Failure")
        return {"success": True}