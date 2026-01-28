from server.core.graph_repo import GraphRepository
from server.core.graph_service import GraphService
from server.core.stats_service import StatsService

def test_stats_basic(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))

    # A tiene 2 amigos, B tiene 1, C tiene 1
    gs.add_friendship("A", "B")
    gs.add_friendship("A", "C")

    stats = StatsService(gs).compute_stats()

    assert stats["max_user_id"] == "A"
    assert stats["max_friends"] == 2

    # min puede ser B o C, ambos con 1
    assert stats["min_friends"] == 1
    assert stats["avg_friends"] == (2 + 1 + 1) / 3

def test_stats_empty(tmp_graph_file):
    gs = GraphService(GraphRepository(str(tmp_graph_file)))
    stats = StatsService(gs).compute_stats()
    assert stats["max_user_id"] is None
    assert stats["avg_friends"] == 0.0
