import pytest
from server.core.user_repo import UserRepository

def test_user_repo_create_and_find(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))

    u = repo.create_user("Julian", "Test", "julian123", "HASH")
    assert u["username"] == "julian123"

    found = repo.find_by_username("julian123")
    assert found is not None
    assert found["id"] == u["id"]

def test_user_repo_duplicate_username(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    repo.create_user("A", "B", "user", "HASH")

    with pytest.raises(ValueError):
        repo.create_user("C", "D", "user", "HASH2")

def test_user_repo_get_by_id(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    u = repo.create_user("Julian", "Test", "julian123", "HASH")

    got = repo.get_by_id(u["id"])
    assert got["username"] == "julian123"

def test_user_repo_search_by_name(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    repo.create_user("Julian", "Gomez", "jg", "H1")
    repo.create_user("Ana", "Lopez", "al", "H2")

    results = repo.search_by_name("julian g")
    assert len(results) == 1
    assert results[0]["username"] == "jg"
