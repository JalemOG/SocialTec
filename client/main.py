from client.net.api_client import ApiClient

HOST = "127.0.0.1"
PORT = 5050

def main():
    c = ApiClient(HOST, PORT)
    c.connect()

    resp = c.request({"type": "PING", "payload": {"msg": "hola"}})
    print(resp)

    c.close()

if __name__ == "__main__":
    main()
