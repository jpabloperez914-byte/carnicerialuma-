import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.producto_controller import ProductoController
from ..controllers.desposte_controller import DesposteController

class StockView(ttk.Frame):
    """
    Vista rediseñada para la gestión de stock, dividida en pestañas.
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.producto_controller = ProductoController()
        self.desposte_controller = DesposteController()

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña 1: Gestión de Media Res
        self.tab_media_res = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_media_res, text="Gestión de Media Res")
        self.create_media_res_tab(self.tab_media_res)

        # Pestaña 2: Stock de Cortes
        self.tab_cortes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cortes, text="Stock de Cortes")
        self.create_cortes_tab(self.tab_cortes)

    def create_media_res_tab(self, tab):
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        controls_frame = ttk.Frame(tab, padding=(10, 10))
        controls_frame.grid(row=0, column=0, sticky="ew")

        ttk.Button(controls_frame, text="Registrar Nueva Media Res", command=self.open_new_arrival_dialog).pack(side="left")
        ttk.Button(controls_frame, text="Realizar Desposte", command=self.open_butcher_dialog).pack(side="left", padx=10)
        ttk.Button(controls_frame, text="Refrescar", command=self.load_media_res).pack(side="right")

        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("id", "fecha", "proveedor", "peso_inicial", "costo", "peso_despostado", "merma")
        self.media_res_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.media_res_tree.heading(col, text=col.replace("_", " ").title())
        self.media_res_tree.pack(fill="both", expand=True)
        self.load_media_res()

    def create_cortes_tab(self, tab):
        # This is essentially the old StockView
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("id", "codigo", "nombre", "stock_actual", "precio_kg")
        self.cortes_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.cortes_tree.heading(col, text=col.replace("_", " ").title())
        self.cortes_tree.pack(fill="both", expand=True)
        self.load_cortes()

    def load_media_res(self):
        for i in self.media_res_tree.get_children():
            self.media_res_tree.delete(i)
        for mr in self.desposte_controller.obtener_todas_las_medias_res():
            self.media_res_tree.insert("", "end", values=(
                mr.id, mr.fecha_llegada.strftime("%Y-%m-%d"), mr.proveedor, f"{mr.peso_inicial:.2f} kg", f"${mr.costo:,.2f}", f"{mr.peso_despostado:.2f} kg", f"{mr.merma_calculada:.2f} kg"
            ))

    def load_cortes(self):
        for i in self.cortes_tree.get_children():
            self.cortes_tree.delete(i)
        for p in self.producto_controller.obtener_todos_los_productos():
            self.cortes_tree.insert("", "end", values=(
                p.id, p.codigo, p.nombre, f"{p.stock_actual:.3f} kg", f"${p.precio_kg:,.2f}"
            ))

    def open_new_arrival_dialog(self):
        dialog = RegistrarMediaResDialog(self)
        dialog.wait_window()
        self.load_media_res()

    def open_butcher_dialog(self):
        dialog = RealizarDesposteDialog(self, self.app_controller.current_user.id)
        dialog.wait_window()
        self.load_media_res()
        self.load_cortes()

class RegistrarMediaResDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Registrar Nueva Media Res")

        self.peso_var = tk.DoubleVar()
        self.costo_var = tk.DoubleVar()
        self.proveedor_var = tk.StringVar(value="Proveedor Único")

        ttk.Label(self, text="Peso Inicial (kg):").pack(padx=10, pady=5)
        ttk.Entry(self, textvariable=self.peso_var).pack(padx=10)
        ttk.Label(self, text="Costo Total:").pack(padx=10, pady=5)
        ttk.Entry(self, textvariable=self.costo_var).pack(padx=10)
        ttk.Label(self, text="Proveedor:").pack(padx=10, pady=5)
        ttk.Entry(self, textvariable=self.proveedor_var).pack(padx=10)

        ttk.Button(self, text="Guardar", command=self.save).pack(pady=20)

    def save(self):
        peso = self.peso_var.get()
        costo = self.costo_var.get()
        proveedor = self.proveedor_var.get()
        if peso > 0 and costo > 0 and proveedor:
            self.parent.desposte_controller.registrar_media_res(peso, costo, proveedor)
            self.destroy()
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")

class RealizarDesposteDialog(tk.Toplevel):
    def __init__(self, parent, empleado_id):
        super().__init__(parent)
        self.parent = parent
        self.empleado_id = empleado_id
        self.title("Realizar Desposte")

        self.entries = {}

        # Selección de Media Res
        top_frame = ttk.Frame(self)
        top_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(top_frame, text="Seleccionar Media Res a Despostar:").pack(side="left")
        self.media_res_var = tk.StringVar()
        medias_res_disponibles = self.parent.desposte_controller.obtener_medias_res_disponibles()
        media_res_options = [f"ID: {mr.id} - {mr.fecha_llegada.strftime('%Y-%m-%d')}" for mr in medias_res_disponibles]
        self.media_res_combo = ttk.Combobox(top_frame, textvariable=self.media_res_var, values=media_res_options, state="readonly")
        self.media_res_combo.pack(side="left", padx=5)

        # Canvas para la lista de cortes
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista de cortes
        productos = self.parent.producto_controller.obtener_todos_los_productos()
        for i, prod in enumerate(productos):
            ttk.Label(scrollable_frame, text=f"{prod.nombre}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            peso_var = tk.DoubleVar(value=0.0)
            ttk.Entry(scrollable_frame, textvariable=peso_var).grid(row=i, column=1, padx=5)
            self.entries[prod.id] = peso_var

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(self, text="Guardar Desposte", command=self.save).pack(pady=10)

    def save(self):
        selected_mr_str = self.media_res_var.get()
        if not selected_mr_str:
            messagebox.showerror("Error", "Debe seleccionar una media res.")
            return

        media_res_id = int(selected_mr_str.split("ID: ")[1].split(" -")[0])

        cortes = []
        for prod_id, peso_var in self.entries.items():
            peso = peso_var.get()
            if peso > 0:
                cortes.append({'producto_id': prod_id, 'peso': peso})

        if not cortes:
            messagebox.showwarning("Sin Datos", "No se ingresó peso para ningún corte.")
            return

        success = self.parent.desposte_controller.realizar_desposte(media_res_id, cortes, self.empleado_id)
        if success:
            messagebox.showinfo("Éxito", "El desposte se registró correctamente.")
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo registrar el desposte.")
