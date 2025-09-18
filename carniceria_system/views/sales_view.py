import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.producto_controller import ProductoController
from ..controllers.venta_controller import VentaController

class SalesView(ttk.Frame):
    """
    Vista para el Punto de Venta (POS).
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.producto_controller = ProductoController()
        self.venta_controller = VentaController()

        self.current_cart = []
        self.current_total = tk.DoubleVar(value=0.0)
        self.payment_method = tk.StringVar(value="efectivo")

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=2) # Columna del carrito
        self.grid_columnconfigure(1, weight=1) # Columna de controles
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # --- Panel Izquierdo: Carrito de Compras ---
        cart_frame = ttk.Frame(self, padding=10)
        cart_frame.grid(row=0, column=0, sticky="nsew")
        cart_frame.grid_rowconfigure(1, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(cart_frame, text="Carrito de Venta Actual", font=("Helvetica", 16, "bold")).grid(row=0, column=0, sticky="w")

        # Treeview para el carrito
        columns = ("nombre", "peso", "precio_kg", "subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings")
        self.cart_tree.heading("nombre", text="Producto")
        self.cart_tree.heading("peso", text="Peso (kg)")
        self.cart_tree.heading("precio_kg", text="Precio/kg")
        self.cart_tree.heading("subtotal", text="Subtotal")
        self.cart_tree.column("peso", width=100, anchor=tk.E)
        self.cart_tree.column("precio_kg", width=100, anchor=tk.E)
        self.cart_tree.column("subtotal", width=100, anchor=tk.E)
        self.cart_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Total
        total_frame = ttk.Frame(cart_frame)
        total_frame.grid(row=2, column=1, sticky="e", pady=10)
        ttk.Label(total_frame, text="TOTAL:", font=("Helvetica", 18, "bold")).pack(side="left")
        ttk.Label(total_frame, textvariable=self.current_total, font=("Helvetica", 18, "bold"), foreground="green").pack(side="left")

        # --- Panel Derecho: Controles ---
        controls_frame = ttk.Frame(self, padding=20)
        controls_frame.grid(row=0, column=1, sticky="nsew")

        # Entrada de producto
        entry_frame = ttk.LabelFrame(controls_frame, text="Añadir Producto", padding=15)
        entry_frame.pack(fill="x", pady=(0, 20))
        entry_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Código o Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        self.product_search_var = tk.StringVar()
        self.product_search_entry = ttk.Entry(entry_frame, textvariable=self.product_search_var)
        self.product_search_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.product_search_entry.bind("<Return>", lambda e: self.add_product_to_cart())

        ttk.Label(entry_frame, text="Peso (kg):").grid(row=1, column=0, sticky="w", pady=5)
        self.product_weight_var = tk.DoubleVar()
        self.product_weight_entry = ttk.Entry(entry_frame, textvariable=self.product_weight_var)
        self.product_weight_entry.grid(row=1, column=1, sticky="ew", padx=5)

        add_button = ttk.Button(entry_frame, text="Añadir al Carrito", command=self.add_product_to_cart)
        add_button.grid(row=2, column=1, sticky="e", pady=10)
        self.product_search_entry.focus()

        # Pago y finalización
        payment_frame = ttk.LabelFrame(controls_frame, text="Finalizar Venta", padding=15)
        payment_frame.pack(fill="x")

        ttk.Radiobutton(payment_frame, text="Efectivo", variable=self.payment_method, value="efectivo").pack(anchor="w")
        ttk.Radiobutton(payment_frame, text="Transferencia", variable=self.payment_method, value="transferencia").pack(anchor="w")
        ttk.Radiobutton(payment_frame, text="Tarjeta", variable=self.payment_method, value="tarjeta").pack(anchor="w")

        finish_button = ttk.Button(payment_frame, text="FINALIZAR VENTA", command=self.finalize_sale, style="Accent.TButton")
        finish_button.pack(fill="x", pady=20)

        cancel_button = ttk.Button(payment_frame, text="Cancelar Venta", command=self.clear_cart)
        cancel_button.pack(fill="x")

    def add_product_to_cart(self):
        search_term = self.product_search_var.get()
        weight = self.product_weight_var.get()

        if not search_term or not weight or weight <= 0:
            messagebox.showwarning("Datos incompletos", "Debe ingresar un término de búsqueda y un peso válido.")
            return

        producto = self.producto_controller.buscar_producto(search_term)
        if not producto:
            messagebox.showerror("Error", f"No se encontró ningún producto con el término '{search_term}'.")
            return

        if producto.stock_actual < weight:
            messagebox.showwarning("Stock Insuficiente", f"No hay suficiente stock para '{producto.nombre}'.\nStock actual: {producto.stock_actual} kg.")
            return

        subtotal = producto.precio_kg * weight
        cart_item = {'producto': producto, 'peso': weight, 'subtotal': subtotal}
        self.current_cart.append(cart_item)

        # Actualizar vista del carrito
        self.cart_tree.insert("", tk.END, values=(producto.nombre, f"{weight:.3f}", f"${producto.precio_kg:,.2f}", f"${subtotal:,.2f}"))

        # Actualizar total
        self.update_total()

        # Limpiar entradas
        self.product_search_var.set("")
        self.product_weight_var.set(0.0)
        self.product_search_entry.focus()

    def update_total(self):
        total = sum(item['subtotal'] for item in self.current_cart)
        self.current_total.set(f"${total:,.2f}")

    def clear_cart(self):
        self.current_cart.clear()
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        self.update_total()

    def finalize_sale(self):
        if not self.current_cart:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito para vender.")
            return

        # Asumimos que el turno se gestiona en un nivel superior. Por ahora, 'Mañana'.
        # El ID del empleado se obtiene del app_controller.
        empleado_id = self.app_controller.current_user.id
        forma_pago = self.payment_method.get()

        ticket_num = self.venta_controller.crear_nueva_venta(empleado_id, 'Mañana', forma_pago, self.current_cart)

        if ticket_num:
            messagebox.showinfo("Venta Exitosa", f"Venta registrada con éxito.\nTicket N°: {ticket_num}")
            self.clear_cart()
            # Aquí se podría implementar la impresión del ticket
        else:
            messagebox.showerror("Error en Venta", "Hubo un problema al registrar la venta. El stock no ha sido modificado.")

        # Refrescar la lista de productos en la vista de stock si está visible
        # (requiere una comunicación más avanzada entre vistas)
        print("Es necesario implementar un sistema de pub/sub para actualizar otras vistas.")
