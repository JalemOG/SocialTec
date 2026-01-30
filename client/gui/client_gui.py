# client/gui/client_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from shared.crypto import CryptoService
from shared.config import FERNET_KEY, HOST, PORT
from client.net.api_client import ApiClient


class ClientGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SocialTec - Cliente")
        self.root.geometry("520x460")

        self.client = ApiClient(HOST, PORT)
        self.crypto = CryptoService(FERNET_KEY)

        self.current_user = None

        # cerrar socket al cerrar ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_layout()
        self.show_login()  # pantalla inicial

        # intenta conectar una vez al iniciar (si falla, la GUI igual abre)
        self.ensure_connected()

    # -----------------------
    # Conexión / lifecycle
    # -----------------------
    def ensure_connected(self) -> bool:
        """
        Intenta conectar si no está conectado.
        Retorna True si hay conexión, False si falla.
        """
        try:
            # ApiClient normalmente guarda el socket en self.sock
            if not getattr(self.client, "sock", None):
                self.client.connect()
            return True
        except Exception as e:
            messagebox.showerror(
                "Servidor no disponible",
                f"No se pudo conectar al servidor ({HOST}:{PORT}).\n\nDetalle: {e}\n\nAsegurate de correr:\npython -m server.main"
            )
            return False

    def on_close(self):
        try:
            self.client.close()
        except Exception:
            pass
        self.root.destroy()

    # -----------------------
    # UI
    # -----------------------
    def _build_layout(self):
        self.main_frame = ttk.Frame(self.root, padding=12)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(self.main_frame, text="SocialTec", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 10))

        self.container = ttk.Frame(self.main_frame)
        self.container.pack(fill=tk.BOTH, expand=True)

        # -------- REGISTER FRAME --------
        self.register_frame = ttk.Frame(self.container)

        ttk.Label(self.register_frame, text="Registro", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        ttk.Label(self.register_frame, text="Nombre:").pack(anchor="w")
        self.name_entry = ttk.Entry(self.register_frame)
        self.name_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.register_frame, text="Apellido:").pack(anchor="w")
        self.lastname_entry = ttk.Entry(self.register_frame)
        self.lastname_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.register_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(self.register_frame)
        self.username_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.register_frame, text="Contraseña:").pack(anchor="w")
        self.password_entry = ttk.Entry(self.register_frame, show="*")
        self.password_entry.pack(fill=tk.X, pady=2)

        self.register_button = ttk.Button(self.register_frame, text="Registrar", command=self.on_register)
        self.register_button.pack(fill=tk.X, pady=(10, 4))

        ttk.Button(self.register_frame, text="Ya tengo cuenta → Iniciar sesión", command=self.show_login).pack(fill=tk.X)

        # -------- LOGIN FRAME --------
        self.login_frame = ttk.Frame(self.container)

        ttk.Label(self.login_frame, text="Iniciar sesión", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        ttk.Label(self.login_frame, text="Username:").pack(anchor="w")
        self.login_username_entry = ttk.Entry(self.login_frame)
        self.login_username_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.login_frame, text="Contraseña:").pack(anchor="w")
        self.login_password_entry = ttk.Entry(self.login_frame, show="*")
        self.login_password_entry.pack(fill=tk.X, pady=2)

        self.login_button = ttk.Button(self.login_frame, text="Entrar", command=self.on_login)
        self.login_button.pack(fill=tk.X, pady=(10, 4))

        ttk.Button(self.login_frame, text="No tengo cuenta → Registrarme", command=self.show_register).pack(fill=tk.X)

        # -------- MAIN MENU FRAME --------
        self.main_menu_frame = ttk.Frame(self.container)

        self.welcome_lbl = ttk.Label(self.main_menu_frame, text="", font=("Segoe UI", 12, "bold"))
        self.welcome_lbl.pack(anchor="w", pady=(0, 10))

        ttk.Button(self.main_menu_frame, text="Ver mi perfil", command=self.view_profile).pack(fill=tk.X, pady=4)
        ttk.Button(self.main_menu_frame, text="Buscar usuario", command=self.search_friend).pack(fill=tk.X, pady=4)
        ttk.Button(self.main_menu_frame, text="Ver mis amigos", command=self.view_friends).pack(fill=tk.X, pady=4)
        ttk.Button(self.main_menu_frame, text="Agregar amigo por username", command=self.add_friend_by_username).pack(fill=tk.X, pady=4)
        ttk.Button(self.main_menu_frame, text="Eliminar amistad por username", command=self.remove_friend).pack(fill=tk.X, pady=4)

        ttk.Separator(self.main_menu_frame).pack(fill=tk.X, pady=10)

        ttk.Button(self.main_menu_frame, text="Cerrar sesión", command=self.logout).pack(fill=tk.X)

    def _show_only(self, frame: ttk.Frame):
        for child in (self.register_frame, self.login_frame, self.main_menu_frame):
            child.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def show_register(self):
        self._show_only(self.register_frame)

    def show_login(self):
        self._show_only(self.login_frame)

    def show_main_menu(self):
        name = self.current_user.get("name", "")
        username = self.current_user.get("username", "")
        self.welcome_lbl.config(text=f"Bienvenido: {name} (@{username})")
        self._show_only(self.main_menu_frame)

    # -----------------------
    # Helpers
    # -----------------------
    def _require_login(self) -> bool:
        if not self.current_user:
            messagebox.showerror("Error", "Primero tenés que iniciar sesión.")
            return False
        return True

    def _friendly_error(self, resp: dict, default="Ocurrió un error."):
        err = resp.get("error") or default
        messagebox.showerror("Error", err)

    def _get_profile(self) -> dict | None:
        """Devuelve data del perfil (me + friends) o None."""
        if not self.ensure_connected():
            return None
        if not self._require_login():
            return None

        msg = {"type": "GET_MY_PROFILE", "payload": {"user_id": self.current_user["id"]}}
        resp = self.client.request(msg)
        if resp.get("status") != "ok":
            self._friendly_error(resp, "No se pudo obtener el perfil.")
            return None
        return resp["data"]

    def _find_user_by_username_exact(self, username: str) -> dict | None:
        """
        Usa SEARCH_USER (que busca por nombre/substring) y filtra por username exacto.
        Devuelve el user dict o None.
        """
        if not self.ensure_connected():
            return None

        resp = self.client.request({"type": "SEARCH_USER", "payload": {"query": username}})
        if resp.get("status") != "ok":
            self._friendly_error(resp, "No se pudo buscar el usuario.")
            return None

        for u in resp["data"].get("results", []):
            if u.get("username", "").lower() == username.lower():
                return u
        return None

    # -----------------------
    # Actions
    # -----------------------
    def on_register(self):
        if not self.ensure_connected():
            return

        name = self.name_entry.get().strip()
        lastname = self.lastname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not name or not lastname or not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return

        # Validación: username ya existe
        existing = self._find_user_by_username_exact(username)
        if existing:
            messagebox.showerror("Error", "El nombre de usuario ya está registrado.")
            return

        payload = {"name": name, "lastname": lastname, "username": username, "password": password}
        msg = {"type": "REGISTER", "secure": self.crypto.encrypt_json(payload)}

        self.register_button.config(state="disabled")
        try:
            resp = self.client.request(msg)
        finally:
            self.register_button.config(state="normal")

        if resp.get("status") == "ok":
            messagebox.showinfo("Registro exitoso", "Te registraste correctamente. Ahora iniciá sesión.")
            self.show_login()
        else:
            self._friendly_error(resp, "No se pudo registrar el usuario.")

    def on_login(self):
        if not self.ensure_connected():
            return

        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return

        payload = {"username": username, "password": password}
        msg = {"type": "LOGIN", "secure": self.crypto.encrypt_json(payload)}

        self.login_button.config(state="disabled")
        try:
            resp = self.client.request(msg)
        finally:
            self.login_button.config(state="normal")

        if resp.get("status") == "ok":
            self.current_user = resp["data"]
            self.show_main_menu()
        else:
            self._friendly_error(resp, "Credenciales incorrectas.")

    def logout(self):
        self.current_user = None
        messagebox.showinfo("Sesión", "Se cerró la sesión.")
        self.show_login()

    def view_profile(self):
        data = self._get_profile()
        if not data:
            return

        me = data["me"]
        friends = data.get("friends", [])

        friends_text = "\n".join([f"@{f['username']} — {f['name']} {f['lastname']}" for f in friends]) or "(sin amigos)"
        txt = (
            f"Usuario: @{me['username']}\n"
            f"Nombre: {me['name']} {me['lastname']}\n\n"
            f"Amigos:\n{friends_text}"
        )
        messagebox.showinfo("Mi perfil", txt)

    def view_friends(self):
        data = self._get_profile()
        if not data:
            return

        friends = data.get("friends", [])
        if not friends:
            messagebox.showinfo("Mis amigos", "No tenés amigos todavía.")
            return

        # Si querés ordenar por username aquí, lo hacemos simple (ya ordenás con MergeSort en client/main)
        friends_sorted = sorted(friends, key=lambda f: f.get("username", ""))

        txt = "\n".join([f"@{f['username']} — {f['name']} {f['lastname']}" for f in friends_sorted])
        messagebox.showinfo("Mis amigos", txt)

    def search_friend(self):
        if not self.ensure_connected():
            return
        if not self._require_login():
            return

        query = simpledialog.askstring("Buscar usuario", "Buscá por nombre/username:")
        if not query:
            return

        resp = self.client.request({"type": "SEARCH_USER", "payload": {"query": query}})
        if resp.get("status") != "ok":
            self._friendly_error(resp, "No se pudo realizar la búsqueda.")
            return

        results = resp["data"].get("results", [])
        if not results:
            messagebox.showinfo("Resultados", "No se encontraron usuarios.")
            return

        txt = "\n".join([f"@{u['username']} — {u['name']} {u['lastname']}" for u in results])
        messagebox.showinfo("Resultados", txt)

    def add_friend_by_username(self):
        if not self.ensure_connected():
            return
        if not self._require_login():
            return

        uname = simpledialog.askstring("Agregar amigo", "Username exacto (ej: ana123):")
        if not uname:
            return

        friend = self._find_user_by_username_exact(uname)
        if not friend:
            messagebox.showinfo("Agregar amigo", "No se encontró ese username.")
            return

        if friend["id"] == self.current_user["id"]:
            messagebox.showerror("Error", "No podés agregarte a vos mismo.")
            return

        resp = self.client.request(
            {"type": "ADD_FRIEND", "payload": {"a": self.current_user["id"], "b": friend["id"]}}
        )

        if resp.get("status") == "ok":
            messagebox.showinfo("Agregar amigo", f"Ahora sos amigo de @{friend['username']}.")
        else:
            self._friendly_error(resp, "No se pudo agregar al amigo.")

    def remove_friend(self):
        if not self.ensure_connected():
            return
        if not self._require_login():
            return

        uname = simpledialog.askstring("Eliminar amistad", "Username exacto a eliminar (ej: ana123):")
        if not uname:
            return

        friend = self._find_user_by_username_exact(uname)
        if not friend:
            messagebox.showinfo("Eliminar amistad", "No se encontró ese username.")
            return

        resp = self.client.request(
            {"type": "REMOVE_FRIEND", "payload": {"a": self.current_user["id"], "b": friend["id"]}}
        )

        if resp.get("status") == "ok":
            messagebox.showinfo("Eliminar amistad", f"Amistad eliminada con @{friend['username']}.")
        else:
            self._friendly_error(resp, "No se pudo eliminar la amistad.")


def run():
    root = tk.Tk()
    ClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()