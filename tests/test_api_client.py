import threading
import socket
from shared.protocol import MessageProtocol
from client.net.api_client import ApiClient

def test_api_client_request_response():
    host = "127.0.0.1"

    # servidor mínimo fake
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.bind((host, 0))
    srv_sock.listen()
    port = srv_sock.getsockname()[1]

    def server_thread():
        conn, _ = srv_sock.accept()
        try:
            req = MessageProtocol.recv(conn)
            MessageProtocol.send(conn, {"status":"ok", "data":req})
        finally:
            conn.close()
            srv_sock.close()

    t = threading.Thread(target=server_thread, daemon=True)
    t.start()

    client = ApiClient(host, port)
    client.connect()
    resp = client.request({"type":"PING","payload":{"x":1}})
    client.close()

    assert resp["status"] == "ok"
    assert resp["data"]["type"] == "PING"
