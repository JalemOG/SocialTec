from typing import Dict, Any

from shared.crypto import CryptoService
from shared.config import FERNET_KEY, USERS_FILE, GRAPH_FILE
from server.core.user_repo import UserRepository
from server.core.auth_service import AuthService
from server.core.graph_repo import GraphRepository
from server.core.graph_service import GraphService

class RequestRouter:
    def __init__(self):
        self.crypto = CryptoService(FERNET_KEY)
        self.users = UserRepository(USERS_FILE)
        self.auth = AuthService(self.users)
        self.graph = GraphService(GraphRepository(GRAPH_FILE))

    def handle(self, req: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = req.get("type")

        try:
            if msg_type == "PING":
                return {"status": "ok", "data": {"pong": True}}

            if msg_type == "REGISTER":
                data = self.crypto.decrypt_json(req.get("secure", ""))
                user = self.auth.register(data["name"], data["lastname"], data["username"], data["password"])
                self.graph.ensure_user(user["id"])
                return {"status": "ok", "data": user}

            if msg_type == "LOGIN":
                data = self.crypto.decrypt_json(req.get("secure", ""))
                user = self.auth.login(data["username"], data["password"])
                self.graph.ensure_user(user["id"])
                return {"status": "ok", "data": user}

            # ---- Search (005) ----
            if msg_type == "SEARCH_USER":
                payload = req.get("payload", {})
                query = payload.get("query", "")
                results = self.users.search_by_name(query)
                return {"status": "ok", "data": {"results": results}}

            # ---- Profile (008) ----
            if msg_type == "GET_MY_PROFILE":
                payload = req.get("payload", {})
                my_id = payload.get("user_id", "")
                me = self.users.get_by_id(my_id)
                if not me:
                    return {"status": "error", "error": "User not found"}
                friend_ids = self.graph.friends_of(my_id)
                friends = []
                for fid in friend_ids:
                    fu = self.users.get_by_id(fid)
                    if fu:
                        friends.append({"id": fu["id"], "name": fu["name"], "lastname": fu["lastname"], "username": fu["username"]})
                return {"status": "ok", "data": {"me": {"id": me["id"], "name": me["name"], "lastname": me["lastname"], "username": me["username"]}, "friends": friends}}

            # ---- Friendship (add/remove) ----
            if msg_type == "ADD_FRIEND":
                payload = req.get("payload", {})
                a = payload.get("a")
                b = payload.get("b")
                if not self.users.get_by_id(a) or not self.users.get_by_id(b):
                    return {"status": "error", "error": "User not found"}
                self.graph.add_friendship(a, b)
                return {"status": "ok", "data": {"added": True}}

            if msg_type == "REMOVE_FRIEND":
                payload = req.get("payload", {})
                a = payload.get("a")
                b = payload.get("b")
                self.graph.remove_friendship(a, b)
                return {"status": "ok", "data": {"removed": True}}

            return {"status": "error", "error": f"Unknown type: {msg_type}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
