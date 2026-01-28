import json
from cryptography.fernet import Fernet
from typing import Dict, Any

class CryptoService:
    def __init__(self, key: bytes):
        self.f = Fernet(key)

    def encrypt_json(self, obj: Dict[str, Any]) -> str:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        token = self.f.encrypt(raw)
        return token.decode("utf-8")

    def decrypt_json(self, token_str: str) -> Dict[str, Any]:
        token = token_str.encode("utf-8")
        raw = self.f.decrypt(token)
        return json.loads(raw.decode("utf-8"))
