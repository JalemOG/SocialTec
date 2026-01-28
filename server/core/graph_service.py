import threading
from typing import Dict, List, Set
from server.core.graph_repo import GraphRepository

class GraphService:
    def __init__(self, repo: GraphRepository):
        self._repo = repo
        self._lock = threading.Lock()

        # adj: user_id -> set(friend_ids)
        raw = self._repo.load()
        self._adj: Dict[str, Set[str]] = {k: set(v) for k, v in raw.items()}

    def _persist(self) -> None:
        raw = {k: sorted(list(v)) for k, v in self._adj.items()}
        self._repo.save(raw)

    def ensure_user(self, user_id: str) -> None:
        with self._lock:
            if user_id not in self._adj:
                self._adj[user_id] = set()
                self._persist()

    def add_friendship(self, a: str, b: str) -> None:
        if a == b:
            raise ValueError("Cannot friend yourself")
        with self._lock:
            self._adj.setdefault(a, set()).add(b)
            self._adj.setdefault(b, set()).add(a)
            self._persist()

    def remove_friendship(self, a: str, b: str) -> None:
        with self._lock:
            if a in self._adj:
                self._adj[a].discard(b)
            if b in self._adj:
                self._adj[b].discard(a)
            self._persist()

    def friends_of(self, user_id: str) -> List[str]:
        with self._lock:
            return sorted(list(self._adj.get(user_id, set())))

    def snapshot(self) -> Dict[str, List[str]]:
        with self._lock:
            return {k: sorted(list(v)) for k, v in self._adj.items()}
