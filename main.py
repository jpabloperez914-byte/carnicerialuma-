import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager
from StockManagerUI import StockManagerUI
from SalesUI import SalesUI

class CarniceriaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión para Carnicería")
        self.geometry("1200x800")
        self.db_manager = DatabaseManager()
        self.sales_ui_instance = None
        self.create_widgets()

    def create_widgets(self):
        # Crear estilos personalizados para los botones
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
        
        style.configure("Green.TButton", background="#4CAF50", foreground="white")
        style.map("Green.TButton", background=[("active", "#45a049")])

        style.configure("Red.TButton", background="#f44336", foreground="white")
        style.map("Red.TButton", background=[("active", "#d32f2f")])

        # Marco para los botones de navegación y acciones
        nav_frame = tk.Frame(self, bg="#333333")
        nav_frame.pack(side="top", fill="x")

        # Botones de navegación principales
        self.btn_sales = ttk.Button(nav_frame, text="Punto de Venta", command=self.show_sales_ui)
        self.btn_sales.pack(side="left", fill="x", expand=True, ipadx=5, ipady=5)

        self.btn_stock = ttk.Button(nav_frame, text="Gestión de Stock", command=self.show_stock_ui)
        self.btn_stock.pack(side="left", fill="x", expand=True, ipadx=5, ipady=5)

        self.btn_reports = ttk.Button(nav_frame, text="Reportes", command=self.show_reports_ui)
        self.btn_reports.pack(side="left", fill="x", expand=True, ipadx=5, ipady=5)
        
        # Botones para acciones de venta, siempre visibles
        self.btn_nueva_venta = ttk.Button(
            nav_frame,
            text="+",
            style="Green.TButton",
            width=3,
            command=self.agregar_nueva_venta
        )
        self.btn_nueva_venta.pack(side="left", padx=5)

        self.btn_cerrar_venta = ttk.Button(
            nav_frame,
            text="✖",
            style="Red.TButton",
            width=3,
            command=self.cerrar_venta_actual
        )
        self.btn_cerrar_venta.pack(side="left", padx=5)

        # Marco para el contenido de las pestañas
        self.content_frame = tk.Frame(self, bg="#f0f0f0")
        self.content_frame.pack(fill="both", expand=True)
        
        # Iniciar con la interfaz de ventas
        self.current_ui = None
        self.show_sales_ui()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
    def show_sales_ui(self):
        self.clear_content()
        self.sales_ui_instance = SalesUI(self.content_frame, self.db_manager)
        self.current_ui = self.sales_ui_instance
        self.set_sales_buttons_state("normal")

    def show_stock_ui(self):
        self.clear_content()
        self.current_ui = StockManagerUI(self.content_frame, self.db_manager)
        self.set_sales_buttons_state("disabled")

    def show_reports_ui(self):
        self.clear_content()
        self.mostrar_historial_ventas()
        self.set_sales_buttons_state("disabled")

    def set_sales_buttons_state(self, state):
        if state == "normal":
            self.btn_nueva_venta.state(["!disabled"])
            self.btn_cerrar_venta.state(["!disabled"])
        elif state == "disabled":
            self.btn_nueva_venta.state(["disabled"])
            self.btn_cerrar_venta.state(["disabled"])

    def agregar_nueva_venta(self):
        if self.sales_ui_instance:
            self.sales_ui_instance.agregar_nueva_venta()

    def cerrar_venta_actual(self):
        if self.sales_ui_instance:
            self.sales_ui_instance.cerrar_venta_actual()

    def mostrar_historial_ventas(self):
        main_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        titulo = tk.Label(main_frame, text="Historial de Ventas", font=("Arial", 18, "bold"), bg="#f0f0f0")
        titulo.pack(pady=(0, 20))
        
        frame_tabla_historial = tk.Frame(main_frame, bg="white", relief="sunken", bd=2)
        frame_tabla_historial.pack(fill="both", expand=True)
        
        columns_historial = ("numero", "fecha", "total", "items", "productos")
        tree_historial = ttk.Treeview(frame_tabla_historial, columns=columns_historial, show="headings", height=15)
        
        headers_historial = ["Número Venta", "Fecha", "Total", "Items", "Productos"]
        widths_historial = [120, 150, 100, 80, 300]
        
        for col, header, width in zip(columns_historial, headers_historial, widths_historial):
            tree_historial.heading(col, text=header, anchor="center")
            tree_historial.column(col, width=width, minwidth=width, anchor="center" if col != "productos" else "w")
            
        scrollbar_v_historial = ttk.Scrollbar(frame_tabla_historial, orient="vertical", command=tree_historial.yview)
        scrollbar_h_historial = ttk.Scrollbar(frame_tabla_historial, orient="horizontal", command=tree_historial.xview)
        
        tree_historial.configure(yscrollcommand=scrollbar_v_historial.set, xscrollcommand=scrollbar_h_historial.set)
        
        tree_historial.grid(row=0, column=0, sticky="nsew")
        scrollbar_v_historial.grid(row=0, column=1, sticky="ns")
        scrollbar_h_historial.grid(row=1, column=0, sticky="ew")
        
        frame_tabla_historial.grid_rowconfigure(0, weight=1)
        frame_tabla_historial.grid_columnconfigure(0, weight=1)
        
        try:
            ventas = self.db_manager.obtener_historial_ventas(limite=50)
            for venta in ventas:
                fecha_formateada = venta['fecha_venta'][:16] if venta['fecha_venta'] else ''
                productos_texto = venta['productos'] if venta['productos'] else 'Sin productos'
                
                tree_historial.insert("", "end", values=(
                    venta['numero_venta'],
                    fecha_formateada,
                    f"${venta['total']:.2f}",
                    venta['cantidad_items'] or 0,
                    productos_texto
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")

if __name__ == "__main__":
    app = CarniceriaApp()
    app.mainloop()