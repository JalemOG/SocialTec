from server.core.graph_repo import GraphRepository
from server.core.graph_service import GraphService
from server.core.path_service import PathService

def test_path_exists(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    gs.add_friendship("A", "B")
    gs.add_friendship("B", "C")
    gs.add_friendship("C", "D")

    ps = PathService(gs)
    path = ps.find_path_bfs("A", "D")
    assert path == ["A", "B", "C", "D"]

def test_path_not_exists(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    gs.ensure_user("A")
    gs.ensure_user("D")

    ps = PathService(gs)
    path = ps.find_path_bfs("A", "D")
    assert path == []

def test_path_same_node(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    gs.ensure_user("A")

    ps = PathService(gs)
    assert ps.find_path_bfs("A", "A") == ["A"]
