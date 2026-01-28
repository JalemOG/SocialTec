import pytest
from server.core.user_repo import UserRepository
from server.core.auth_service import AuthService

def test_auth_register_and_login_ok(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    auth = AuthService(repo)

    reg = auth.register("Julian", "Test", "julian123", "1234")
    assert reg["username"] == "julian123"

    logged = auth.login("julian123", "1234")
    assert logged["id"] == reg["id"]

def test_auth_login_wrong_password(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    auth = AuthService(repo)
    auth.register("Julian", "Test", "julian123", "1234")

    with pytest.raises(ValueError):
        auth.login("julian123", "wrong")

def test_auth_login_unknown_user(tmp_users_file):
    repo = UserRepository(str(tmp_users_file))
    auth = AuthService(repo)

    with pytest.raises(ValueError):
        auth.login("noexiste", "1234")
