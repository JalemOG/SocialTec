from typing import Dict, Any

from shared.crypto import CryptoService
from shared.config import FERNET_KEY, USERS_FILE, GRAPH_FILE

from server.core.user_repo import UserRepository
from server.core.auth_service import AuthService

from server.core.graph_repo import GraphRepository
from server.core.graph_service import GraphService

from server.core.path_service import PathService
from server.core.stats_service import StatsService


class RequestRouter:
    def __init__(self):
        self.crypto = CryptoService(FERNET_KEY)

        self.users = UserRepository(USERS_FILE)
        self.auth = AuthService(self.users)

        self.graph = GraphService(GraphRepository(GRAPH_FILE))
        self.path = PathService(self.graph)
        self.stats = StatsService(self.graph)

    def handle(self, req: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = req.get("type")

        try:
            # ----------------
            # Healthcheck
            # ----------------
            if msg_type == "PING":
                return {"status": "ok", "data": {"pong": True}}

            # ----------------
            # Auth (003, 006, 007)
            # ----------------
            if msg_type == "REGISTER":
                data = self.crypto.decrypt_json(req.get("secure", ""))
                user = self.auth.register(
                    name=data["name"],
                    lastname=data["lastname"],
                    username=data["username"],
                    password=data["password"],
                )
                # Asegura nodo en el grafo
                self.graph.ensure_user(user["id"])
                return {"status": "ok", "data": user}

            if msg_type == "LOGIN":
                data = self.crypto.decrypt_json(req.get("secure", ""))
                user = self.auth.login(
                    username=data["username"],
                    password=data["password"],
                )
                # Asegura nodo en el grafo
                self.graph.ensure_user(user["id"])
                return {"status": "ok", "data": user}

            # ----------------
            # Search (005)
            # ----------------
            if msg_type == "SEARCH_USER":
                payload = req.get("payload", {})
                query = payload.get("query", "")
                results = self.users.search_by_name(query)
                return {"status": "ok", "data": {"results": results}}
            
                        # ----------------
            # Get by username (exact)
            # ----------------
            if msg_type == "GET_USER_BY_USERNAME":
                payload = req.get("payload", {})
                username = (payload.get("username") or "").strip()

                if not username:
                    return {"status": "error", "error": "Missing username"}

                user = self.users.get_by_username(username)
                if not user:
                    return {"status": "ok", "data": {"user": None}}

                # devolver solo campos necesarios
                return {
                    "status": "ok",
                    "data": {
                        "user": {
                            "id": user["id"],
                            "name": user["name"],
                            "lastname": user["lastname"],
                            "username": user["username"],
                        }
                    },
                }
            # ----------------
            # Profile (008)
            # ----------------
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
                        friends.append(
                            {
                                "id": fu["id"],
                                "name": fu["name"],
                                "lastname": fu["lastname"],
                                "username": fu["username"],
                            }
                        )

                return {
                    "status": "ok",
                    "data": {
                        "me": {
                            "id": me["id"],
                            "name": me["name"],
                            "lastname": me["lastname"],
                            "username": me["username"],
                        },
                        "friends": friends,
                    },
                }

            # ----------------
            # Friendship (add/remove)
            # ----------------
            if msg_type == "ADD_FRIEND":
                payload = req.get("payload", {})
                a = payload.get("a")
                b = payload.get("b")

                if not a or not b:
                    return {"status": "error", "error": "Missing a/b"}

                if not self.users.get_by_id(a) or not self.users.get_by_id(b):
                    return {"status": "error", "error": "User not found"}

                self.graph.add_friendship(a, b)
                return {"status": "ok", "data": {"added": True}}

            if msg_type == "REMOVE_FRIEND":
                payload = req.get("payload", {})
                a = payload.get("a")
                b = payload.get("b")

                if not a or not b:
                    return {"status": "error", "error": "Missing a/b"}

                self.graph.remove_friendship(a, b)
                return {"status": "ok", "data": {"removed": True}}

            # ----------------
            # ID 010: Path between two users (server-side)
            # ----------------
            if msg_type == "PATH_BETWEEN":
                payload = req.get("payload", {})
                src = payload.get("src")
                dst = payload.get("dst")

                if not src or not dst:
                    return {"status": "error", "error": "Missing src/dst"}

                path = self.path.find_path_bfs(src, dst)
                return {"status": "ok", "data": {"exists": len(path) > 0, "path": path}}

            # ----------------
            # ID 011: Graph stats (server-side)
            # ----------------
            if msg_type == "GRAPH_STATS":
                stats = self.stats.compute_stats()
                return {"status": "ok", "data": stats}

            return {"status": "error", "error": f"Unknown type: {msg_type}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
