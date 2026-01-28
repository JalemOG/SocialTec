import socket
from typing import Dict, Any
from shared.protocol import MessageProtocol

class ApiClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def request(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        if not self.sock:
            raise RuntimeError("Not connected")
        MessageProtocol.send(self.sock, msg)
        return MessageProtocol.recv(self.sock)

    def close(self) -> None:
        if self.sock:
            self.sock.close()
            self.sock = None
