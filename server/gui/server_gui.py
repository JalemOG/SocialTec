import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from server.core.graph_service import GraphService
from server.core.path_service import PathService
from server.core.stats_service import StatsService
from server.core.user_repo import UserRepository


class ServerGUI:
    def __init__(
        self,
        root: tk.Tk,
        graph: GraphService,
        path_service: PathService,
        stats_service: StatsService,
        users: UserRepository,
    ):
        self.root = root
        self.graph = graph
        self.path_service = path_service
        self.stats_service = stats_service
        self.users = users

        # Mapeo: texto mostrado -> user_id real
        self.user_choices: List[str] = []
        self.choice_to_id: Dict[str, str] = {}

        self.root.title("SocialTec - Server")
        self.root.geometry("1050x680")

        self._build_layout()
        self.refresh_users()  # carga inicial

    def _build_layout(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ===== Usuarios (refresh) =====
        users_frame = ttk.LabelFrame(left, text="Usuarios", padding=10)
        users_frame.pack(fill=tk.X, pady=5)

        ttk.Button(users_frame, text="Actualizar lista de usuarios", command=self.refresh_users).pack(fill=tk.X)

        # ===== PATH (ID 010) =====
        path_frame = ttk.LabelFrame(left, text="ID 010 - Path entre usuarios", padding=10)
        path_frame.pack(fill=tk.X, pady=10)

        ttk.Label(path_frame, text="SRC:").pack(anchor="w")
        self.src_combo = ttk.Combobox(path_frame, values=self.user_choices, state="readonly")
        self.src_combo.pack(fill=tk.X, pady=2)

        ttk.Label(path_frame, text="DST:").pack(anchor="w")
        self.dst_combo = ttk.Combobox(path_frame, values=self.user_choices, state="readonly")
        self.dst_combo.pack(fill=tk.X, pady=2)

        btns = ttk.Frame(path_frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Buscar path (BFS)", command=self.on_find_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btns, text="Limpiar salida", command=self.on_clear).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        # ===== STATS (ID 011) =====
        stats_frame = ttk.LabelFrame(left, text="ID 011 - Estadísticas", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)

        ttk.Button(stats_frame, text="Calcular estadísticas", command=self.on_stats).pack(fill=tk.X, pady=4)

        # ===== GRAFO (ID 002) =====
        graph_frame = ttk.LabelFrame(left, text="ID 002 - Grafo completo", padding=10)
        graph_frame.pack(fill=tk.X, pady=5)

        ttk.Button(graph_frame, text="Renderizar grafo", command=self.on_render_graph).pack(fill=tk.X, pady=4)

        # ===== Output =====
        out_frame = ttk.LabelFrame(right, text="Salida", padding=10)
        out_frame.pack(fill=tk.BOTH, expand=False)

        self.output = tk.Text(out_frame, height=16)
        self.output.pack(fill=tk.BOTH, expand=False)

        # ===== Canvas grafo =====
        viz_frame = ttk.LabelFrame(right, text="Visualización del grafo", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------- Helpers ----------
    def _log(self, msg: str):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    def on_clear(self):
        self.output.delete("1.0", tk.END)

    def _label_for_user(self, u: Dict[str, Any]) -> str:
        short = u["id"][:6]
        username = u.get("username", "?")
        name = u.get("name", "")
        lastname = u.get("lastname", "")
        return f"{username} — {name} {lastname} ({short}...)"


    def _user_label(self, user_id: str) -> str:
        u = self.users.get_by_id(user_id)
        if not u:
            return user_id
        return f"{u.get('username','?')} — {u.get('name','')} {u.get('lastname','')} ({user_id[:6]}...)"



    # ---------- New: refresh users ----------
    def refresh_users(self):
        # Leemos todos los usuarios desde users.json (UserRepository)
        # UserRepository no tiene list_all() todavía; la hacemos aquí leyendo _load() si existe.
        # Mejor: agregá list_all() al repo (abajo te dejo el cambio).
        try:
            all_users = self.users.list_all()
        except AttributeError:
            # fallback por si todavía no agregaste list_all()
            all_users = self.users._load()  # type: ignore

        # Ordenar por nombre/apellido para UX
        all_users = sorted(all_users, key=lambda u: (u.get("name", ""), u.get("lastname", "")))

        self.choice_to_id.clear()
        self.user_choices = []

        for u in all_users:
            label = self._label_for_user(u)
            self.user_choices.append(label)
            self.choice_to_id[label] = u["id"]

        self.src_combo["values"] = self.user_choices
        self.dst_combo["values"] = self.user_choices

        # Autoselección
        if self.user_choices:
            if not self.src_combo.get():
                self.src_combo.current(0)
            if not self.dst_combo.get():
                self.dst_combo.current(min(1, len(self.user_choices) - 1))

        self._log(f"[USERS] Cargados {len(self.user_choices)} usuarios.")

    # ---------- Events ----------
    def on_find_path(self):
        src_label = self.src_combo.get().strip()
        dst_label = self.dst_combo.get().strip()

        if not src_label or not dst_label:
            self._log("[PATH] Error: seleccioná SRC y DST.")
            return

        src = self.choice_to_id.get(src_label)
        dst = self.choice_to_id.get(dst_label)

        if not src or not dst:
            self._log("[PATH] Error: selección inválida.")
            return

        path = self.path_service.find_path_bfs(src, dst)
        if not path:
            self._log(f"[PATH] No existe camino entre {self._user_label(src)} y {self._user_label(dst)}")
            return

        pretty = " -> ".join(self._user_label(x) for x in path)
        self._log(f"[PATH] Camino encontrado ({len(path)-1} saltos): {pretty}")

    def on_stats(self):
        stats = self.stats_service.compute_stats()
        self._log("[STATS] Resultados:")
        self._log(f"  - max_user_id: {stats['max_user_id']}  (amigos: {stats['max_friends']})")
        self._log(f"  - min_user_id: {stats['min_user_id']}  (amigos: {stats['min_friends']})")
        self._log(f"  - avg_friends: {stats['avg_friends']:.2f}")

    def on_render_graph(self):
        snap = self.graph.snapshot()

        G = nx.Graph()
        for u in snap.keys():
            G.add_node(u)

        for u, friends in snap.items():
            for v in friends:
                if u != v:
                    G.add_edge(u, v)

        self.ax.clear()
        self.ax.axis("off")

        if len(G.nodes) == 0:
            self._log("[GRAFO] Grafo vacío.")
            self.canvas.draw()
            return

        labels = {}
        for node in G.nodes:
            u = self.users.get_by_id(node)
            if u:
                labels[node] = f"{u['name']} {u['lastname'][:1]}."
            else:
                labels[node] = node[:6]

        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx(G, pos=pos, ax=self.ax, labels=labels, font_size=8, node_size=900)

        self.canvas.draw()
        self._log(f"[GRAFO] Renderizado: {len(G.nodes)} nodos, {len(G.edges)} aristas.")
