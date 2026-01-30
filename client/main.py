import tkinter as tk
from client.gui.client_gui import ClientGUI

def run_client_gui():
    root = tk.Tk()
    gui = ClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # Si el server ya está corriendo en otro hilo, solo iniciamos la GUI del cliente
    run_client_gui()
