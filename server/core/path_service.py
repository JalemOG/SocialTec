from collections import deque
from typing import Dict, List, Optional

from server.core.graph_service import GraphService


class PathService:
    def __init__(self, graph: GraphService):
        self.graph = graph

    def find_path_bfs(self, src: str, dst: str) -> List[str]:
        """
        Retorna [src, ..., dst] si existe camino.
        Si no existe, retorna [].
        """
        if src == dst:
            return [src]

        adj: Dict[str, List[str]] = self.graph.snapshot()
        if src not in adj or dst not in adj:
            return []

        q = deque([src])
        visited = {src}
        parent: Dict[str, Optional[str]] = {src: None}

        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if v in visited:
                    continue
                visited.add(v)
                parent[v] = u
                if v == dst:
                    return self._reconstruct(parent, dst)
                q.append(v)

        return []

    def _reconstruct(self, parent: Dict[str, Optional[str]], dst: str) -> List[str]:
        path = []
        cur: Optional[str] = dst
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        return path
