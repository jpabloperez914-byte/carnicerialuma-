import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.producto_controller import ProductoController

class StockView(ttk.Frame):
    """
    Vista para la gestión de stock de productos y el proceso de desposte.
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.producto_controller = ProductoController()

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        """Crea los widgets principales de la vista de stock."""

        # --- Frame de Controles Superiores ---
        controls_frame = ttk.Frame(self, padding=(10, 10))
        controls_frame.grid(row=0, column=0, sticky="ew")

        new_arrival_button = ttk.Button(controls_frame, text="Registrar Llegada de Media Res", command=self.open_new_arrival_dialog)
        new_arrival_button.pack(side="left", padx=(0, 10))

        butcher_button = ttk.Button(controls_frame, text="Realizar Desposte", command=self.open_butcher_dialog)
        butcher_button.pack(side="left", padx=(0, 10))

        refresh_button = ttk.Button(controls_frame, text="Refrescar Lista", command=self.load_products)
        refresh_button.pack(side="right")

        # --- Treeview para mostrar los productos ---
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "codigo", "nombre", "stock_actual", "precio_kg", "stock_minimo", "fecha_vencimiento")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Definir las cabeceras
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Corte")
        self.tree.heading("stock_actual", text="Stock Actual (kg)")
        self.tree.heading("precio_kg", text="Precio/kg")
        self.tree.heading("stock_minimo", text="Stock Mínimo (kg)")
        self.tree.heading("fecha_vencimiento", text="Fecha Vencimiento")

        # Definir el ancho de las columnas
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("codigo", width=80, anchor=tk.CENTER)
        self.tree.column("nombre", width=250)
        self.tree.column("stock_actual", width=120, anchor=tk.E)
        self.tree.column("precio_kg", width=100, anchor=tk.E)
        self.tree.column("stock_minimo", width=120, anchor=tk.E)
        self.tree.column("fecha_vencimiento", width=150, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def load_products(self):
        """Carga o recarga los productos en el Treeview."""
        # Limpiar vista anterior
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Cargar productos desde el controlador
        productos = self.producto_controller.obtener_todos_los_productos()
        for p in productos:
            stock_str = f"{p.stock_actual:.3f}"
            precio_str = f"${p.precio_kg:,.2f}"
            vencimiento_str = p.fecha_vencimiento.strftime('%Y-%m-%d')

            self.tree.insert("", tk.END, values=(
                p.id, p.codigo, p.nombre, stock_str, precio_str, p.stock_minimo, vencimiento_str
            ))

    def open_new_arrival_dialog(self):
        """Abre el diálogo para registrar una nueva media res."""
        messagebox.showinfo("Función no implementada", "Aquí se abrirá la ventana para registrar la llegada de una nueva media res.")

    def open_butcher_dialog(self):
        """Abre el diálogo para realizar el desposte."""
        messagebox.showinfo("Función no implementada", "Aquí se abrirá la ventana para realizar el desposte de una media res.")
