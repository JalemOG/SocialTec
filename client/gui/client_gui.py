# client/gui/client_gui.py
import tkinter as tk
from tkinter import ttk, messagebox

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

        # Ventanas abiertas (extra pro)
        self.profile_win = None
        self.profile_text = None

        self.friends_win = None
        self.friends_list = None

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
        ttk.Button(self.main_menu_frame, text="Buscar usuario (lista clickeable)", command=self.search_friend).pack(fill=tk.X, pady=4)
        ttk.Button(self.main_menu_frame, text="Ver mis amigos", command=self.view_friends).pack(fill=tk.X, pady=4)

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
    
    def refresh_open_views(self):
        """
        Extra pro:
        Si están abiertas las ventanas de "Mi perfil" o "Mis amigos",
        las refresca automáticamente (vuelve a pedir el perfil al server y actualiza UI).
        """
        data = self._get_profile()
        if not data:
            return

        me = data["me"]
        friends = data.get("friends", [])

        # --- refrescar ventana de perfil ---
        try:
            if self.profile_win and self.profile_win.winfo_exists() and self.profile_text:
                friends_text = "\n".join([f"@{f['username']} — {f['name']} {f['lastname']}" for f in friends]) or "(sin amigos)"
                txt = (
                    f"Usuario: @{me['username']}\n"
                    f"Nombre: {me['name']} {me['lastname']}\n\n"
                    f"Amigos:\n{friends_text}"
                )
                self.profile_text.config(state="normal")
                self.profile_text.delete("1.0", tk.END)
                self.profile_text.insert(tk.END, txt)
                self.profile_text.config(state="disabled")
        except Exception:
            pass

        # --- refrescar ventana de amigos ---
        try:
            if self.friends_win and self.friends_win.winfo_exists() and self.friends_list:
                self.friends_list.delete(0, tk.END)

                if not friends:
                    self.friends_list.insert(tk.END, "(sin amigos)")
                else:
                    friends_sorted = sorted(friends, key=lambda f: f.get("username", ""))
                    for f in friends_sorted:
                        self.friends_list.insert(tk.END, f"@{f['username']} — {f['name']} {f['lastname']}")
        except Exception:
            pass


    def _find_user_by_username_exact(self, username: str) -> dict | None:
        """
        Busca por username exacto usando endpoint dedicado.
        """
        if not self.ensure_connected():
            return None

        resp = self.client.request({"type": "GET_USER_BY_USERNAME", "payload": {"username": username}})
        if resp.get("status") != "ok":
            self._friendly_error(resp, "No se pudo buscar el usuario por username.")
            return None

        return resp["data"].get("user")

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

        # Validación: username ya existe (exact)
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

        # Si ya está abierta, traerla al frente y refrescar
        if self.profile_win and self.profile_win.winfo_exists():
            self.profile_win.lift()
            self.profile_win.focus_force()
            self.refresh_open_views()
            return

        win = tk.Toplevel(self.root)
        win.title("Mi perfil")
        win.geometry("520x420")
        win.transient(self.root)

        self.profile_win = win

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Mi perfil", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        txtw = tk.Text(frm, height=16, wrap="word")
        txtw.pack(fill=tk.BOTH, expand=True)
        self.profile_text = txtw

        def on_close():
            try:
                self.profile_win = None
                self.profile_text = None
            finally:
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        # Pintar contenido inicial usando refresh
        self.refresh_open_views()

    def view_friends(self):
        data = self._get_profile()
        if not data:
            return

        # Si ya está abierta, traerla al frente y refrescar
        if self.friends_win and self.friends_win.winfo_exists():
            self.friends_win.lift()
            self.friends_win.focus_force()
            self.refresh_open_views()
            return

        win = tk.Toplevel(self.root)
        win.title("Mis amigos")
        win.geometry("520x420")
        win.transient(self.root)

        self.friends_win = win

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Mis amigos", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        lst = tk.Listbox(frm, height=16)
        lst.pack(fill=tk.BOTH, expand=True)
        self.friends_list = lst

        def on_close():
            try:
                self.friends_win = None
                self.friends_list = None
            finally:
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        # Pintar contenido inicial usando refresh
        self.refresh_open_views()

    def search_friend(self):
        """
        Ventana de búsqueda con lista clickeable y acciones:
        - Agregar seleccionado (solo si NO es amigo ya)
        - Eliminar seleccionado (solo si YA es amigo)
        """
        if not self.ensure_connected():
            return
        if not self._require_login():
            return

        # Traer mi lista de amigos UNA sola vez para esta ventana
        profile = self._get_profile()
        if not profile:
            return

        friend_ids = {f["id"] for f in profile.get("friends", [])}

        win = tk.Toplevel(self.root)
        win.title("Buscar usuarios")
        win.geometry("560x420")
        win.transient(self.root)
        win.grab_set()

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Buscar por nombre/username (parcial):", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        top = ttk.Frame(frm)
        top.pack(fill=tk.X, pady=8)

        q_entry = ttk.Entry(top)
        q_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        results_list = tk.Listbox(frm, height=14)
        results_list.pack(fill=tk.BOTH, expand=True, pady=(6, 8))

        idx_to_user: list[dict] = []

        # botones
        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X)

        add_btn = ttk.Button(btns, text="Agregar seleccionado")
        remove_btn = ttk.Button(btns, text="Eliminar seleccionado")
        close_btn = ttk.Button(btns, text="Cerrar", command=win.destroy)

        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        close_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Estado inicial
        add_btn.state(["disabled"])
        remove_btn.state(["disabled"])

        def refresh_buttons_for_selection():
            sel = results_list.curselection()
            if not sel or sel[0] >= len(idx_to_user):
                add_btn.state(["disabled"])
                remove_btn.state(["disabled"])
                return

            u = idx_to_user[sel[0]]
            is_friend = u["id"] in friend_ids

            if is_friend:
                add_btn.state(["disabled"])
                remove_btn.state(["!disabled"])
            else:
                add_btn.state(["!disabled"])
                remove_btn.state(["disabled"])

        def do_search():
            query = q_entry.get().strip()
            results_list.delete(0, tk.END)
            idx_to_user.clear()

            add_btn.state(["disabled"])
            remove_btn.state(["disabled"])

            if not query:
                messagebox.showinfo("Buscar", "Escribí algo para buscar.")
                return

            resp = self.client.request({"type": "SEARCH_USER", "payload": {"query": query}})
            if resp.get("status") != "ok":
                self._friendly_error(resp, "No se pudo realizar la búsqueda.")
                return

            results = resp["data"].get("results", [])
            if not results:
                results_list.insert(tk.END, "(Sin resultados)")
                return

            # no mostrarte a vos mismo
            results = [u for u in results if u.get("id") != self.current_user["id"]]
            if not results:
                results_list.insert(tk.END, "(Sin resultados)")
                return

            for u in results:
                idx_to_user.append(u)
                tag = " (amigo)" if u["id"] in friend_ids else ""
                results_list.insert(tk.END, f"@{u['username']} — {u['name']} {u['lastname']}{tag}")

        def get_selected_user() -> dict | None:
            sel = results_list.curselection()
            if not sel:
                messagebox.showinfo("Seleccionar", "Seleccioná un usuario de la lista.")
                return None
            i = sel[0]
            if i >= len(idx_to_user):
                return None
            return idx_to_user[i]

        def add_selected():
            u = get_selected_user()
            if not u:
                return

            if u["id"] in friend_ids:
                messagebox.showinfo("Agregar amigo", f"@{u['username']} ya está en tu lista de amigos.")
                refresh_buttons_for_selection()
                return

            resp = self.client.request({"type": "ADD_FRIEND", "payload": {"a": self.current_user["id"], "b": u["id"]}})
            if resp.get("status") == "ok":
                messagebox.showinfo("Agregar amigo", f"Ahora sos amigo de @{u['username']}.")

                friend_ids.add(u["id"])
                
                sel = results_list.curselection()
                if sel:
                    idx = sel[0]
                    results_list.delete(idx)
                    results_list.insert(idx, f"@{u['username']} — {u['name']} {u['lastname']} (amigo)")
                    results_list.selection_set(idx)

                refresh_buttons_for_selection()
                self.refresh_open_views()
                
            else:
                self._friendly_error(resp, "No se pudo agregar al amigo.")

        def remove_selected():
            u = get_selected_user()
            if not u:
                return

            if u["id"] not in friend_ids:
                messagebox.showinfo("Eliminar amistad", f"@{u['username']} no está en tu lista de amigos.")
                refresh_buttons_for_selection()
                return

            resp = self.client.request({"type": "REMOVE_FRIEND", "payload": {"a": self.current_user["id"], "b": u["id"]}})
            if resp.get("status") == "ok":
                messagebox.showinfo("Eliminar amistad", f"Amistad eliminada con @{u['username']}.")

                friend_ids.discard(u["id"])

                sel = results_list.curselection()
                if sel:
                    idx = sel[0]
                    results_list.delete(idx)
                    results_list.insert(idx, f"@{u['username']} — {u['name']} {u['lastname']}")
                    results_list.selection_set(idx)

                refresh_buttons_for_selection()
                self.refresh_open_views()

            else:
                self._friendly_error(resp, "No se pudo eliminar la amistad.")

        add_btn.config(command=add_selected)
        remove_btn.config(command=remove_selected)

        ttk.Button(top, text="Buscar", command=do_search).pack(side=tk.LEFT, padx=8)

        q_entry.bind("<Return>", lambda _e: do_search())
        results_list.bind("<<ListboxSelect>>", lambda _e: refresh_buttons_for_selection())

        q_entry.focus_set()


def run():
    root = tk.Tk()
    ClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()