import threading
from server.core.graph_repo import GraphRepository
from server.core.graph_service import GraphService

def test_graph_service_add_remove_and_friends(tmp_graph_file):
    repo = GraphRepository(str(tmp_graph_file))
    gs = GraphService(repo)

    gs.ensure_user("A")
    gs.ensure_user("B")

    gs.add_friendship("A", "B")
    assert "B" in gs.friends_of("A")
    assert "A" in gs.friends_of("B")

    gs.remove_friendship("A", "B")
    assert "B" not in gs.friends_of("A")
    assert "A" not in gs.friends_of("B")

def test_graph_service_snapshot(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    gs.add_friendship("A", "B")
    snap = gs.snapshot()
    assert snap["A"] == ["B"]
    assert snap["B"] == ["A"]

def test_graph_service_thread_safety_smoke(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    gs.ensure_user("A")
    gs.ensure_user("B")

    def worker():
        for _ in range(50):
            gs.add_friendship("A", "B")
            gs.remove_friendship("A", "B")

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

    # Debe seguir siendo consistente (sin explotar) y terminar en estado válido
    friendsA = gs.friends_of("A")
    assert isinstance(friendsA, list)
