from client.net.api_client import ApiClient
from shared.crypto import CryptoService
from shared.config import HOST, PORT, FERNET_KEY
from client.core.mergesort import merge_sort

def main():
    c = ApiClient(HOST, PORT)
    c.connect()
    crypto = CryptoService(FERNET_KEY)

    # Crear 2 usuarios
    u1 = {"name": "Julian", "lastname": "Test", "username": "julian123", "password": "1234"}
    u2 = {"name": "Ana", "lastname": "Lopez", "username": "ana123", "password": "abcd"}

    r1 = c.request({"type": "REGISTER", "secure": crypto.encrypt_json(u1)})
    r2 = c.request({"type": "REGISTER", "secure": crypto.encrypt_json(u2)})

    # Si ya existen, logueamos
    if r1["status"] != "ok":
        r1 = c.request({"type": "LOGIN", "secure": crypto.encrypt_json({"username": u1["username"], "password": u1["password"]})})
    if r2["status"] != "ok":
        r2 = c.request({"type": "LOGIN", "secure": crypto.encrypt_json({"username": u2["username"], "password": u2["password"]})})

    id1 = r1["data"]["id"]
    id2 = r2["data"]["id"]

    # Hacer amistad
    print("ADD_FRIEND ->", c.request({"type": "ADD_FRIEND", "payload": {"a": id1, "b": id2}}))

    # Ver perfil de Julian
    prof = c.request({"type": "GET_MY_PROFILE", "payload": {"user_id": id1}})
    print("GET_MY_PROFILE raw ->", prof)

    friends = prof["data"]["friends"]
    friends_sorted = merge_sort(friends, key=lambda f: f"{f['name']} {f['lastname']}".lower())
    print("Friends sorted (MergeSort) ->", friends_sorted)

    c.close()

if __name__ == "__main__":
    main()
