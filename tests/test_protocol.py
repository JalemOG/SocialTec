import socket
import pytest
from shared.protocol import MessageProtocol

def test_protocol_send_recv_roundtrip():
    a, b = socket.socketpair()
    try:
        msg = {"type": "PING", "payload": {"x": 1, "y": "hola"}}
        MessageProtocol.send(a, msg)
        received = MessageProtocol.recv(b)
        assert received == msg
    finally:
        a.close()
        b.close()

def test_protocol_recv_disconnect_raises():
    a, b = socket.socketpair()
    try:
        a.close()  # fuerza disconnect del otro lado
        with pytest.raises(Exception):
            MessageProtocol.recv(b)
    finally:
        try: b.close()
        except: pass
