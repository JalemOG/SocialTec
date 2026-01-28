import json
import struct
from typing import Any, Dict

class MessageProtocol:
    """
    [4 bytes length big-endian][JSON utf-8]
    """
    HEADER = 4

    @staticmethod
    def send(sock, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg, ensure_ascii=False).encode("utf-8")
        sock.sendall(struct.pack(">I", len(data)) + data)

    @staticmethod
    def recv(sock) -> Dict[str, Any]:
        header = MessageProtocol._recv_exact(sock, MessageProtocol.HEADER)
        if not header:
            raise ConnectionError("Disconnected")
        (length,) = struct.unpack(">I", header)
        payload = MessageProtocol._recv_exact(sock, length)
        if not payload:
            raise ConnectionError("Disconnected")
        return json.loads(payload.decode("utf-8"))

    @staticmethod
    def _recv_exact(sock, n: int) -> bytes:
        chunks = []
        got = 0
        while got < n:
            chunk = sock.recv(n - got)
            if not chunk:
                return b""
            chunks.append(chunk)
            got += len(chunk)
        return b"".join(chunks)
