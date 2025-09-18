# SalesUI.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
from database import DatabaseManager

class SalesUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.ventas_data = {1: {'productos': [], 'total': 0.0}}
        self.venta_actual = 1
        self.num_ventas = 1
        self.crear_interfaz_ventas()

    def crear_interfaz_ventas(self):
        main_frame = tk.Frame(self.parent_frame, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Contenedor de pestañas ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=(0, 10), fill="x")
        self.notebook.bind("<<NotebookTabChanged>>", self.cambiar_pestana)

        # Crear la primera pestaña por defecto
        self.crear_pestana_venta(1)
        self.notebook.after(100, lambda: self.notebook.select(0))

        # Sección de búsqueda
        frame_busqueda = tk.Frame(main_frame, bg="#e0e0e0", padx=10, pady=10, relief="groove", bd=2)
        frame_busqueda.pack(fill="x", pady=10)
        
        lbl_codigo = tk.Label(frame_busqueda, text="Código:", font=("Arial", 12), bg="#e0e0e0")
        lbl_codigo.pack(side="left", padx=(0, 5))
        
        entry_codigo = tk.Entry(frame_busqueda, font=("Arial", 12), width=30)
        entry_codigo.pack(side="left", padx=(0, 10))
        entry_codigo.bind("<Return>", lambda e: self.buscar_y_agregar_producto(self.venta_actual, entry_codigo))
        
        btn_buscar = tk.Button(
            frame_busqueda,
            text="🔍",
            font=("Arial", 14),
            command=self.abrir_busqueda_stock
        )
        btn_buscar.pack(side="left")
        
        # --- Contenedor principal de la tabla ---
        frame_tabla = tk.Frame(main_frame, bg="white", relief="sunken", bd=2)
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))
        
        self.tree_carrito = ttk.Treeview(
            frame_tabla,
            columns=("id", "producto", "cantidad", "precio_unitario", "subtotal"),
            show="headings"
        )
        self.tree_carrito.heading("id", text="ID")
        self.tree_carrito.heading("producto", text="Producto")
        self.tree_carrito.heading("cantidad", text="Cantidad (kg)")
        self.tree_carrito.heading("precio_unitario", text="P. Unitario")
        self.tree_carrito.heading("subtotal", text="Subtotal")
        
        self.tree_carrito.column("id", width=50, stretch=tk.NO, anchor="center")
        self.tree_carrito.column("producto", width=250, anchor="w")
        self.tree_carrito.column("cantidad", width=100, anchor="center")
        self.tree_carrito.column("precio_unitario", width=100, anchor="e")
        self.tree_carrito.column("subtotal", width=120, anchor="e")
        
        self.tree_carrito.pack(fill="both", expand=True)

        # --- Contenedor inferior para el total y los botones de acción ---
        frame_inferior = tk.Frame(main_frame, bg="#f0f0f0")
        frame_inferior.pack(fill="x")
        
        lbl_total_text = tk.Label(frame_inferior, text="TOTAL:", font=("Arial", 16, "bold"), bg="#f0f0f0")
        lbl_total_text.pack(side="left", padx=10)
        
        self.lbl_total_value = tk.Label(frame_inferior, text="$0.00", font=("Arial", 16, "bold"), bg="#f0f0f0")
        self.lbl_total_value.pack(side="left", padx=10)

        # Botones de acción en la parte inferior
        btn_cobrar = tk.Button(
            frame_inferior,
            text="F12 Cobrar",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2,
            command=self.abrir_ventana_cobro
        )
        btn_cobrar.pack(side="right", padx=(0, 5))
        
        btn_cancelar = tk.Button(
            frame_inferior,
            text="Cancelar Venta",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            height=2,
            command=lambda: self.cancelar_venta(self.venta_actual)
        )
        btn_cancelar.pack(side="right", padx=(0, 5))
        
        # Vincular la tecla F12 a la función de cobro
        self.parent_frame.winfo_toplevel().bind("<F12>", lambda e: self.abrir_ventana_cobro())

    def crear_pestana_venta(self, num_venta):
        frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(frame, text=f"Venta {num_venta}")
    
    def cambiar_pestana(self, event=None):
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text")
        self.venta_actual = int(tab_text.split()[-1])
        self.actualizar_carrito(self.venta_actual)

    def agregar_nueva_venta(self):
        self.num_ventas += 1
        self.ventas_data[self.num_ventas] = {'productos': [], 'total': 0.0}
        self.crear_pestana_venta(self.num_ventas)
        self.notebook.select(self.num_ventas - 1)

    def cerrar_venta_actual(self):
        if len(self.ventas_data) <= 1:
            messagebox.showwarning("Atención", "Debe haber al menos una venta abierta.")
            return

        current_tab_id = self.notebook.select()
        current_tab_index = self.notebook.index(current_tab_id)
        current_tab_text = self.notebook.tab(current_tab_id, "text")
        num_venta_a_cerrar = int(current_tab_text.split()[-1])
        
        if self.ventas_data[num_venta_a_cerrar]['productos'] and not messagebox.askyesno(
            "Confirmar Cierre",
            f"La Venta {num_venta_a_cerrar} tiene productos. ¿Desea cerrarla de todas formas?"
        ):
            return
            
        del self.ventas_data[num_venta_a_cerrar]
        self.notebook.forget(current_tab_id)
        
        if self.notebook.tabs():
            self.notebook.select(0)
        else:
            self.agregar_nueva_venta()

    def buscar_y_agregar_producto(self, num_venta, entry_codigo):
        codigo = entry_codigo.get().strip()
        if not codigo:
            return
        
        producto = self.db.buscar_producto_por_codigo(codigo)
        if producto:
            entry_codigo.delete(0, tk.END)
            self.seleccionar_producto_para_venta(num_venta, producto)
        else:
            messagebox.showerror("Error", "Producto no encontrado.")

    def abrir_busqueda_stock(self):
        dialog = Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title("Buscar Producto en Stock")
        dialog.geometry("700x500")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()
        
        frame_busqueda = tk.Frame(dialog, bg="#e0e0e0", padx=10, pady=10)
        frame_busqueda.pack(fill="x")
        
        lbl_buscar = tk.Label(frame_busqueda, text="Buscar por nombre:", font=("Arial", 12), bg="#e0e0e0")
        lbl_buscar.pack(side="left", padx=(0, 5))
        
        entry_buscar = tk.Entry(frame_busqueda, font=("Arial", 12), width=40)
        entry_buscar.pack(side="left", fill="x", expand=True)
        entry_buscar.focus_set()
        
        frame_tabla = tk.Frame(dialog, bg="white")
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("id", "nombre", "categoria", "precio_por_kg", "stock_actual")
        tree_stock = ttk.Treeview(frame_tabla, columns=columns, show="headings", height=15)
        
        tree_stock.heading("id", text="ID")
        tree_stock.heading("nombre", text="Nombre")
        tree_stock.heading("categoria", text="Categoría")
        tree_stock.heading("precio_por_kg", text="Precio/Kg")
        tree_stock.heading("stock_actual", text="Stock")
        
        tree_stock.column("id", width=50, stretch=tk.NO, anchor="center")
        tree_stock.column("nombre", width=250, anchor="w")
        tree_stock.column("categoria", width=150, anchor="w")
        tree_stock.column("precio_por_kg", width=100, anchor="e")
        tree_stock.column("stock_actual", width=100, anchor="e")
        
        tree_stock.pack(fill="both", expand=True)
        
        def on_select_item(event):
            selected_item = tree_stock.focus()
            if selected_item:
                item_values = tree_stock.item(selected_item, "values")
                producto_id = int(item_values[0])
                producto_data = self.db.buscar_producto_por_id(producto_id)
                if producto_data:
                    dialog.destroy()
                    self.seleccionar_producto_para_venta(self.venta_actual, producto_data)
                else:
                    messagebox.showerror("Error", "No se encontraron los datos completos del producto.")
        
        tree_stock.bind("<Double-1>", on_select_item)
        tree_stock.bind("<Return>", on_select_item)
        entry_buscar.bind("<KeyRelease>", lambda event: self.filtrar_productos(entry_buscar.get(), tree_stock))
        
        self.cargar_productos_en_tabla(tree_stock, self.db.obtener_todos_productos())

    def filtrar_productos(self, texto_busqueda, treeview):
        productos_todos = self.db.obtener_todos_productos()
        productos_filtrados = [
            p for p in productos_todos
            if texto_busqueda.lower() in p['nombre'].lower()
        ]
        self.cargar_productos_en_tabla(treeview, productos_filtrados)

    def cargar_productos_en_tabla(self, treeview, productos):
        for item in treeview.get_children():
            treeview.delete(item)
        
        for producto in productos:
            treeview.insert("", "end", values=(
                producto['id'],
                producto['nombre'],
                producto['categoria_nombre'],
                f"${producto['precio_por_kg']:.2f}",
                f"{producto['stock_actual']:.2f} kg"
            ))

    def seleccionar_producto_para_venta(self, num_venta, producto):
        cantidad = simpledialog.askfloat(
            "Cantidad",
            f"Ingrese la cantidad de {producto['nombre']} (kg):",
            initialvalue=1.0,
            parent=self.parent_frame.winfo_toplevel()
        )
        
        if cantidad is not None and cantidad > 0:
            if cantidad > producto['stock_actual']:
                messagebox.showwarning("Stock Insuficiente", f"Stock disponible: {producto['stock_actual']:.2f} kg.")
                return
            
            producto_id = producto['id']
            encontrado = False
            for item in self.ventas_data[num_venta]['productos']:
                if item['producto_id'] == producto_id:
                    item['cantidad'] += cantidad
                    encontrado = True
                    break
            
            if not encontrado:
                self.ventas_data[num_venta]['productos'].append({
                    'producto_id': producto_id,
                    'nombre': producto['nombre'],
                    'cantidad': cantidad,
                    'precio_unitario': producto['precio_por_kg']
                })
            
            self.actualizar_carrito(num_venta)

    def actualizar_carrito(self, num_venta):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        total_venta = 0
        for item_data in self.ventas_data[num_venta]['productos']:
            subtotal = item_data['cantidad'] * item_data['precio_unitario']
            self.tree_carrito.insert("", "end", values=(
                item_data['producto_id'],
                item_data['nombre'],
                f"{item_data['cantidad']:.2f}",
                f"${item_data['precio_unitario']:.2f}",
                f"${subtotal:.2f}"
            ))
            total_venta += subtotal
        
        self.ventas_data[num_venta]['total'] = total_venta
        self.lbl_total_value.config(text=f"${total_venta:.2f}")

    def abrir_ventana_cobro(self):
        productos_venta = self.ventas_data[self.venta_actual]['productos']
        if not productos_venta:
            messagebox.showwarning("Venta Vacía", "No hay productos en el carrito para cobrar.")
            return
            
        total_a_cobrar = self.ventas_data[self.venta_actual]['total']
        num_items = len(productos_venta)
        
        # Crear la ventana emergente
        ventana_cobro = Toplevel(self.parent_frame.winfo_toplevel())
        ventana_cobro.title(f"Cobrar Venta {self.venta_actual}")
        ventana_cobro.geometry("800x600")
        ventana_cobro.grab_set()
        
        # Configurar la división vertical
        ventana_cobro.columnconfigure(0, weight=1)
        ventana_cobro.columnconfigure(1, weight=1)
        ventana_cobro.rowconfigure(0, weight=1)
        
        # Panel izquierdo (métodos de pago)
        frame_metodos_pago = tk.Frame(ventana_cobro, bg="#cccccc")
        frame_metodos_pago.grid(row=0, column=0, sticky="nsew")
        
        lbl_metodos_pago = tk.Label(frame_metodos_pago, text="Métodos de Pago", font=("Arial", 16, "bold"), bg="#cccccc")
        lbl_metodos_pago.pack(pady=(20, 10))
        
        # Crear botones y vincularlos a la función de selección de método de pago
        metodos = ["Efectivo", "Transferencia", "Crédito", "Tarjeta"]
        self.botones_pago = {}
        for metodo in metodos:
            btn_metodo = tk.Button(
                frame_metodos_pago,
                text=metodo,
                font=("Arial", 14),
                width=20,
                pady=10,
                bg="#f0f0f0",  # Color por defecto
                command=lambda m=metodo: self.seleccionar_metodo_pago(m)
            )
            btn_metodo.pack(pady=10, padx=20)
            self.botones_pago[metodo] = btn_metodo
            
        # Panel derecho (resumen de la venta)
        frame_resumen_venta = tk.Frame(ventana_cobro, bg="#ffffff")
        frame_resumen_venta.grid(row=0, column=1, sticky="nsew")

        lbl_resumen_venta = tk.Label(frame_resumen_venta, text="Resumen de la Venta", font=("Arial", 16, "bold"), bg="#ffffff")
        lbl_resumen_venta.pack(pady=(20, 10))
        
        lbl_articulos = tk.Label(
            frame_resumen_venta,
            text=f"Artículos: {num_items}",
            font=("Arial", 14),
            bg="#ffffff"
        )
        lbl_articulos.pack(pady=(0, 5))
        
        lbl_total_resumen = tk.Label(
            frame_resumen_venta,
            text=f"Total a pagar: ${total_a_cobrar:.2f}",
            font=("Arial", 24, "bold"),
            bg="#ffffff"
        )
        lbl_total_resumen.pack(pady=5)

        self.lbl_metodo_seleccionado = tk.Label(
            frame_resumen_venta,
            text="",
            font=("Arial", 12),
            bg="#ffffff",
            fg="blue"
        )
        self.lbl_metodo_seleccionado.pack(pady=10)

        # Contenedor para la entrada de monto y el vuelto
        self.frame_cambio = tk.Frame(frame_resumen_venta, bg="#ffffff")
        
        self.lbl_paga_con = tk.Label(self.frame_cambio, text="Paga con:", font=("Arial", 12), bg="#ffffff")
        self.lbl_paga_con.pack(side="left", padx=5)
        
        self.entry_pago = ttk.Entry(self.frame_cambio, font=("Arial", 12), width=15)
        self.entry_pago.pack(side="left", padx=5)
        self.entry_pago.bind("<KeyRelease>", lambda e: self.calcular_vuelto(total_a_cobrar))

        self.lbl_vuelto = tk.Label(self.frame_cambio, text="", font=("Arial", 12, "bold"), bg="#ffffff", fg="green")
        self.lbl_vuelto.pack(side="left", padx=5)

        # Contenedor para botones de registro al final
        frame_botones_registro = tk.Frame(frame_resumen_venta, bg="#ffffff")
        frame_botones_registro.pack(side="bottom", fill="x", pady=20)

        btn_registrar = tk.Button(
            frame_botones_registro,
            text="Registrar Venta",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            width=20,
            command=lambda: self.finalizar_venta_logica(self.venta_actual, self.metodo_pago_seleccionado, False, ventana_cobro)
        )
        btn_registrar.pack(side="left", padx=10, expand=True)

        btn_facturar_registrar = tk.Button(
            frame_botones_registro,
            text="Generar Factura y Registrar",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            width=25,
            command=lambda: self.finalizar_venta_logica(self.venta_actual, self.metodo_pago_seleccionado, True, ventana_cobro)
        )
        btn_facturar_registrar.pack(side="right", padx=10, expand=True)
        
        self.metodo_pago_seleccionado = None
        self.ventana_cobro = ventana_cobro

    def seleccionar_metodo_pago(self, metodo):
        # Reiniciar colores de todos los botones
        for btn in self.botones_pago.values():
            btn.config(bg="#f0f0f0")
        
        # Asignar el color al botón seleccionado y mostrar/ocultar el campo de vuelto
        if metodo == "Efectivo":
            self.botones_pago[metodo].config(bg="#a5d6a7")
            self.frame_cambio.pack(pady=10)
            self.calcular_vuelto(self.ventas_data[self.venta_actual]['total'])
            self.entry_pago.focus_set()
        else:
            self.frame_cambio.pack_forget()
            if metodo == "Transferencia":
                self.botones_pago[metodo].config(bg="#ffe082")
            elif metodo == "Crédito":
                self.botones_pago[metodo].config(bg="#90caf9")
            elif metodo == "Tarjeta":
                self.botones_pago[metodo].config(bg="#b39ddb")
        
        self.metodo_pago_seleccionado = metodo
        self.lbl_metodo_seleccionado.config(text=f"Método de pago seleccionado: {metodo}")

    def calcular_vuelto(self, total):
        try:
            pago = float(self.entry_pago.get())
            if pago >= total:
                vuelto = pago - total
                self.lbl_vuelto.config(text=f"Vuelto: ${vuelto:.2f}", fg="green")
            else:
                self.lbl_vuelto.config(text="Monto insuficiente", fg="red")
        except ValueError:
            self.lbl_vuelto.config(text="", fg="red")

    def finalizar_venta_logica(self, num_venta, metodo_pago, generar_factura, ventana_cobro):
        if not metodo_pago:
            messagebox.showwarning("Atención", "Por favor, seleccione un método de pago.")
            return

        if metodo_pago == "Efectivo":
            try:
                pago = float(self.entry_pago.get())
                if pago < self.ventas_data[num_venta]['total']:
                    messagebox.showwarning("Monto Insuficiente", "El monto de pago en efectivo es menor al total de la venta.")
                    return
            except (ValueError, IndexError):
                messagebox.showwarning("Monto Inválido", "Por favor, ingrese un monto de pago en efectivo válido.")
                return

        productos_venta = self.ventas_data[num_venta]['productos']
        
        try:
            self.db.crear_venta(productos_venta, metodo_pago)
            
            if generar_factura:
                messagebox.showinfo("Éxito", "Venta registrada y factura generada correctamente.")
            else:
                messagebox.showinfo("Éxito", "Venta registrada correctamente.")
            
            ventana_cobro.destroy()
            
            current_tab_id = self.notebook.select()
            self.notebook.forget(current_tab_id)
            del self.ventas_data[num_venta]
            
            if self.notebook.tabs():
                self.notebook.select(0)
            else:
                self.agregar_nueva_venta()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al registrar la venta: {str(e)}")

    def cancelar_venta(self, num_venta):
        if self.ventas_data[num_venta]['productos'] and not messagebox.askyesno(
            "Confirmar Cancelación",
            f"¿Desea cancelar la Venta {num_venta}? Se perderán todos los productos agregados."
        ):
            return

        self.ventas_data[num_venta]['productos'] = []
        self.ventas_data[num_venta]['total'] = 0.0
        self.actualizar_carrito(num_venta)