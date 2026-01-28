from typing import Dict, Any

from shared.crypto import CryptoService
from shared.config import FERNET_KEY, USERS_FILE
from server.core.user_repo import UserRepository
from server.core.auth_service import AuthService

class RequestRouter:
    def __init__(self):
        self.crypto = CryptoService(FERNET_KEY)
        self.users = UserRepository(USERS_FILE)
        self.auth = AuthService(self.users)

    def handle(self, req: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = req.get("type")

        if msg_type == "PING":
            return {"status": "ok", "data": {"pong": True}}

        # En REGISTER/LOGIN el payload viene cifrado en req["secure"]
        try:
            if msg_type == "REGISTER":
                secure = req.get("secure", "")
                data = self.crypto.decrypt_json(secure)
                user = self.auth.register(
                    name=data["name"],
                    lastname=data["lastname"],
                    username=data["username"],
                    password=data["password"]
                )
                return {"status": "ok", "data": user}

            if msg_type == "LOGIN":
                secure = req.get("secure", "")
                data = self.crypto.decrypt_json(secure)
                user = self.auth.login(
                    username=data["username"],
                    password=data["password"]
                )
                return {"status": "ok", "data": user}

            return {"status": "error", "error": f"Unknown type: {msg_type}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
