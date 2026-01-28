import threading
import tkinter as tk

from shared.config import HOST, PORT
from server.net.tcp_server import TcpServer
from server.core.router import RequestRouter

from server.gui.server_gui import ServerGUI


def main():
    router = RequestRouter()

    # Server TCP en thread aparte
    srv = TcpServer(HOST, PORT, handler=router.handle)
    t = threading.Thread(target=srv.start, daemon=True)
    t.start()

    # GUI del server (ID 002, 010, 011)
    root = tk.Tk()
    gui = ServerGUI(
        root=root,
        graph=router.graph,
        path_service=router.path,
        stats_service=router.stats,
        users=router.users,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
