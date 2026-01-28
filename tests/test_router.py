import importlib
import pytest
from cryptography.fernet import Fernet
from shared.crypto import CryptoService

def test_router_register_login_ok(tmp_path, monkeypatch):
    # 1) Creamos key dinámica
    key = Fernet.generate_key()
    crypto = CryptoService(key)

    # 2) Parchear shared.config para que el router use archivos temporales
    import shared.config as cfg
    monkeypatch.setattr(cfg, "FERNET_KEY", key, raising=False)
    monkeypatch.setattr(cfg, "USERS_FILE", str(tmp_path / "users.json"), raising=False)
    monkeypatch.setattr(cfg, "GRAPH_FILE", str(tmp_path / "graph.json"), raising=False)

    # 3) Reimportar el router para que tome el config parcheado
    import server.core.router as router_module
    importlib.reload(router_module)

    router = router_module.RequestRouter()

    reg_payload = {"name":"Julian","lastname":"Test","username":"julian123","password":"1234"}
    reg_req = {"type":"REGISTER","secure": crypto.encrypt_json(reg_payload)}
    reg_resp = router.handle(reg_req)
    assert reg_resp["status"] == "ok"

    login_payload = {"username":"julian123","password":"1234"}
    login_req = {"type":"LOGIN","secure": crypto.encrypt_json(login_payload)}
    login_resp = router.handle(login_req)
    assert login_resp["status"] == "ok"

def test_router_unknown_type(tmp_path, monkeypatch):
    import shared.config as cfg
    monkeypatch.setattr(cfg, "USERS_FILE", str(tmp_path / "users.json"), raising=False)
    monkeypatch.setattr(cfg, "GRAPH_FILE", str(tmp_path / "graph.json"), raising=False)

    import server.core.router as router_module
    importlib.reload(router_module)

    router = router_module.RequestRouter()
    resp = router.handle({"type":"NOPE"})
    assert resp["status"] == "error"
