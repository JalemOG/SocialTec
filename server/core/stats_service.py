from typing import Any, Dict, List

from server.core.graph_service import GraphService


class StatsService:
    def __init__(self, graph: GraphService):
        self.graph = graph

    def compute_stats(self) -> Dict[str, Any]:
        """
        Devuelve:
        - max_user_id, max_friends
        - min_user_id, min_friends
        - avg_friends
        """
        adj = self.graph.snapshot()
        users: List[str] = list(adj.keys())

        if not users:
            return {
                "max_user_id": None,
                "max_friends": 0,
                "min_user_id": None,
                "min_friends": 0,
                "avg_friends": 0.0,
            }

        degrees = {u: len(adj[u]) for u in users}
        max_user = max(users, key=lambda u: degrees[u])
        min_user = min(users, key=lambda u: degrees[u])
        avg = sum(degrees.values()) / len(users)

        return {
            "max_user_id": max_user,
            "max_friends": degrees[max_user],
            "min_user_id": min_user,
            "min_friends": degrees[min_user],
            "avg_friends": avg,
        }
