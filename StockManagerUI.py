import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
from datetime import datetime

class StockManagerUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.crear_interfaz_stock()

    def crear_interfaz_stock(self):
        main_frame = tk.Frame(self.parent_frame, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Pestaña para la gestión de productos
        frame_productos = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame_productos, text="Productos")
        self.crear_seccion_productos(frame_productos)

        # Pestaña para la gestión de media res
        frame_media_res = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame_media_res, text="Media Res")
        self.crear_seccion_media_res(frame_media_res)

        # Pestaña para la gestión de categorías
        frame_categorias = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame_categorias, text="Categorías")
        self.crear_seccion_categorias(frame_categorias)

    def crear_seccion_productos(self, parent_frame):
        # Sección de formulario para agregar/modificar productos
        frame_formulario = tk.LabelFrame(parent_frame, text="Gestión de Productos", padx=10, pady=10, bg="#ffffff")
        frame_formulario.pack(pady=10, padx=10, fill="x")

        # Campos del formulario
        lbl_nombre = tk.Label(frame_formulario, text="Nombre:", bg="#ffffff")
        lbl_nombre.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry_nombre = ttk.Entry(frame_formulario, width=30)
        entry_nombre.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        lbl_categoria = tk.Label(frame_formulario, text="Categoría:", bg="#ffffff")
        lbl_categoria.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        combo_categoria = ttk.Combobox(frame_formulario, state="readonly", width=20)
        combo_categoria.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        lbl_precio = tk.Label(frame_formulario, text="Precio/Kg:", bg="#ffffff")
        lbl_precio.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        entry_precio = ttk.Entry(frame_formulario, width=15)
        entry_precio.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        lbl_stock = tk.Label(frame_formulario, text="Stock (kg):", bg="#ffffff")
        lbl_stock.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        entry_stock = ttk.Entry(frame_formulario, width=15)
        entry_stock.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        lbl_codigo = tk.Label(frame_formulario, text="Código:", bg="#ffffff")
        lbl_codigo.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        entry_codigo = ttk.Entry(frame_formulario, width=30)
        entry_codigo.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Botones de acción
        frame_botones = tk.Frame(frame_formulario, bg="#ffffff")
        frame_botones.grid(row=3, column=0, columnspan=4, pady=10)
        btn_guardar = ttk.Button(frame_botones, text="Guardar Producto")
        btn_guardar.pack(side="left", padx=5)

        # Sección de tabla de productos
        frame_tabla = tk.Frame(parent_frame, bg="#ffffff", relief="sunken", bd=2)
        frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("id", "nombre", "categoria", "precio_por_kg", "stock_actual")
        tree_productos = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        tree_productos.heading("id", text="ID")
        tree_productos.heading("nombre", text="Nombre")
        tree_productos.heading("categoria", text="Categoría")
        tree_productos.heading("precio_por_kg", text="Precio/Kg")
        tree_productos.heading("stock_actual", text="Stock")
        tree_productos.pack(fill="both", expand=True)

        # Lógica de carga de datos
        self.cargar_productos_en_tabla(tree_productos)

    def crear_seccion_media_res(self, parent_frame):
        # Sección de entrada de datos para media res
        frame_formulario = tk.LabelFrame(parent_frame, text="Ingreso de Media Res", padx=10, pady=10, bg="#ffffff")
        frame_formulario.pack(pady=10, padx=10, fill="x")

        lbl_peso = tk.Label(frame_formulario, text="Peso (kg):", bg="#ffffff")
        lbl_peso.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry_peso = ttk.Entry(frame_formulario, width=20)
        entry_peso.grid(row=0, column=1, padx=5, pady=5)

        lbl_costo = tk.Label(frame_formulario, text="Costo/Kg:", bg="#ffffff")
        lbl_costo.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        entry_costo = ttk.Entry(frame_formulario, width=20)
        entry_costo.grid(row=0, column=3, padx=5, pady=5)
        
        def guardar_media_res():
            try:
                peso = float(entry_peso.get())
                costo = float(entry_costo.get())
                if self.db.crear_historial_media_res(peso, costo):
                    messagebox.showinfo("Éxito", "Media res registrada correctamente.")
                    entry_peso.delete(0, tk.END)
                    entry_costo.delete(0, tk.END)
                    self.cargar_historial_media_res(tree_historial_media_res)
                else:
                    messagebox.showerror("Error", "No se pudo registrar la media res.")
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos.")

        btn_guardar_media_res = ttk.Button(frame_formulario, text="Registrar Media Res", command=guardar_media_res)
        btn_guardar_media_res.grid(row=1, column=0, columnspan=4, pady=10)

        # Sección de tabla para el historial de media res
        frame_tabla = tk.LabelFrame(parent_frame, text="Historial de Media Res", padx=10, pady=10, bg="#ffffff")
        frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("id", "fecha", "peso", "costo_por_kg", "total")
        tree_historial_media_res = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        tree_historial_media_res.heading("id", text="ID")
        tree_historial_media_res.heading("fecha", text="Fecha")
        tree_historial_media_res.heading("peso", text="Peso (kg)")
        tree_historial_media_res.heading("costo_por_kg", text="Costo/Kg")
        tree_historial_media_res.heading("total", text="Total")
        tree_historial_media_res.pack(fill="both", expand=True)

        self.cargar_historial_media_res(tree_historial_media_res)

    def crear_seccion_categorias(self, parent_frame):
        # Lógica de gestión de categorías
        pass

    def cargar_productos_en_tabla(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)
        
        productos = self.db.obtener_todos_productos()
        for producto in productos:
            treeview.insert("", "end", values=(
                producto['id'],
                producto['nombre'],
                producto['categoria_nombre'],
                f"${producto['precio_por_kg']:.2f}",
                f"{producto['stock_actual']:.2f} kg"
            ))

    def cargar_historial_media_res(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)
        
        try:
            historial = self.db.obtener_historial_media_res()
            for registro in historial:
                treeview.insert("", "end", values=(
                    registro['id'],
                    registro['fecha'],
                    f"{registro['peso']:.2f}",
                    f"${registro['costo_por_kg']:.2f}",
                    f"${registro['total_media_res']:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el historial de media res: {str(e)}")