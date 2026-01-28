import json
import os
import uuid
from typing import Dict, Any, Optional, List

class UserRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, users: List[Dict[str, Any]]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        users = self._load()
        for u in users:
            if u["username"].lower() == username.lower():
                return u
        return None

    def create_user(self, name: str, lastname: str, username: str, password_hash: str) -> Dict[str, Any]:
        users = self._load()
        if self.find_by_username(username) is not None:
            raise ValueError("Username already exists")

        user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "lastname": lastname,
            "username": username,
            "password_hash": password_hash,
            "photo_path": ""  # luego lo usamos
        }
        users.append(user)
        self._save(users)
        return user
