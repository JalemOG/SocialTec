import socket
import threading
from typing import Dict, Any, Callable

from shared.protocol import MessageProtocol

HandlerFn = Callable[[Dict[str, Any]], Dict[str, Any]]

class TcpServer:
    def __init__(self, host: str, port: int, handler: HandlerFn):
        self.host = host
        self.port = port
        self.handler = handler
        self._sock: socket.socket | None = None

    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen()
        print(f"[SERVER] Listening on {self.host}:{self.port}")

        while True:
            conn, addr = self._sock.accept()
            print(f"[SERVER] Client connected: {addr}")
            t = threading.Thread(target=self._client_loop, args=(conn, addr), daemon=True)
            t.start()

    def _client_loop(self, conn: socket.socket, addr) -> None:
        try:
            while True:
                req = MessageProtocol.recv(conn)
                resp = self.handler(req)
                MessageProtocol.send(conn, resp)
        except Exception as e:
            print(f"[SERVER] Client {addr} disconnected/error: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
