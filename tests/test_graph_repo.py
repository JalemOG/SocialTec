from server.core.graph_repo import GraphRepository

def test_graph_repo_save_load(tmp_graph_file):
    repo = GraphRepository(str(tmp_graph_file))

    adj = {"u1": ["u2"], "u2": ["u1", "u3"], "u3": ["u2"]}
    repo.save(adj)

    loaded = repo.load()
    assert loaded == adj
