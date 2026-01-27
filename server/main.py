from server.net.tcp_server import TcpServer
from server.core.router import RequestRouter

HOST = "127.0.0.1"
PORT = 5050

def main():
    router = RequestRouter()
    srv = TcpServer(HOST, PORT, handler=router.handle)
    srv.start()

if __name__ == "__main__":
    main()
