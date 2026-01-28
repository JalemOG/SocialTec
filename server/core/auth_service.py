from typing import Dict, Any
from passlib.hash import pbkdf2_sha256
from server.core.user_repo import UserRepository

class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, name: str, lastname: str, username: str, password: str) -> Dict[str, Any]:
        password_hash = pbkdf2_sha256.hash(password)
        user = self.repo.create_user(name, lastname, username, password_hash)
        return {"id": user["id"], "name": user["name"], "lastname": user["lastname"], "username": user["username"]}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        user = self.repo.find_by_username(username)
        if not user:
            raise ValueError("Invalid credentials")
        if not pbkdf2_sha256.verify(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        return {"id": user["id"], "name": user["name"], "lastname": user["lastname"], "username": user["username"]}
