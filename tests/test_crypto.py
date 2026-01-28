import pytest
from cryptography.fernet import Fernet
from shared.crypto import CryptoService

def test_crypto_encrypt_decrypt_json():
    key = Fernet.generate_key()
    crypto = CryptoService(key)

    data = {"username": "julian123", "password": "1234", "n": 5}
    token = crypto.encrypt_json(data)
    out = crypto.decrypt_json(token)

    assert out == data

def test_crypto_wrong_key_fails():
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    c1 = CryptoService(key1)
    c2 = CryptoService(key2)

    token = c1.encrypt_json({"a": 1})
    with pytest.raises(Exception):
        c2.decrypt_json(token)
