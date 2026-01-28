from client.net.api_client import ApiClient
from shared.crypto import CryptoService
from shared.config import HOST, PORT, FERNET_KEY

def main():
    c = ApiClient(HOST, PORT)
    c.connect()

    crypto = CryptoService(FERNET_KEY)

    # 1) REGISTER
    reg_payload = {
        "name": "Julian",
        "lastname": "Test",
        "username": "julian123",
        "password": "1234"
    }
    reg_msg = {"type": "REGISTER", "secure": crypto.encrypt_json(reg_payload)}
    print("REGISTER ->", c.request(reg_msg))

    # 2) LOGIN
    login_payload = {"username": "julian123", "password": "1234"}
    login_msg = {"type": "LOGIN", "secure": crypto.encrypt_json(login_payload)}
    print("LOGIN ->", c.request(login_msg))

    c.close()

if __name__ == "__main__":
    main()
