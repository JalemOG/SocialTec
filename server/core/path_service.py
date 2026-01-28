from collections import deque
from typing import List, Dict, Optional

from server.core.graph_service import GraphService

class PathService:
    def __init__(self, graph: GraphService):
        self.graph = graph

    def find_path_bfs(self, src: str, dst: str) -> List[str]:
        """
        Retorna una lista con el camino [src, ..., dst] si existe.
        Si no existe, retorna [].
        """
        if src == dst:
            return [src]

        adj: Dict[str, List[str]] = self.graph.snapshot()
        if src not in adj or dst not in adj:
            return []

        visited = set([src])
        parent: Dict[str, Optional[str]] = {src: None}
        q = deque([src])

        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    if v == dst:
                        return self._reconstruct(parent, dst)
                    q.append(v)

        return []

    def _reconstruct(self, parent: Dict[str, Optional[str]], dst: str) -> List[str]:
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        return path
    