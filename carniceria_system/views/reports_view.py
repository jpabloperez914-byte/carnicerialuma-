import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from ..controllers.reportes_controller import ReportesController

# --- Dependencia de Matplotlib ---
# Se asume que matplotlib está instalado. Si no, se necesita: pip install matplotlib
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ReportsView(ttk.Frame):
    """
    Vista para mostrar estadísticas y reportes.
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.controller = ReportesController()

        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(self, text="Error: La librería Matplotlib es necesaria para los gráficos.\nPor favor, instálela con 'pip install matplotlib'").pack(expand=True)
            return

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()
        self.refresh_reports() # Cargar reportes con el rango por defecto

    def create_widgets(self):
        # --- Frame de Controles (Selector de Fecha) ---
        controls_frame = ttk.Frame(self, padding=10)
        controls_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(controls_frame, text="Seleccionar Período:").pack(side="left", padx=(0, 10))
        self.period_var = tk.StringVar(value="Últimos 7 días")
        period_selector = ttk.Combobox(controls_frame, textvariable=self.period_var,
                                       values=["Hoy", "Ayer", "Últimos 7 días", "Este mes"])
        period_selector.pack(side="left", padx=(0, 10))
        period_selector.bind("<<ComboboxSelected>>", lambda e: self.refresh_reports())

        # --- Notebook para las pestañas de reportes ---
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_productos = ttk.Frame(self.notebook)
        self.tab_empleados = ttk.Frame(self.notebook)
        self.tab_ventas = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_productos, text="Productos Más Vendidos")
        self.notebook.add(self.tab_empleados, text="Rendimiento de Empleados")
        self.notebook.add(self.tab_ventas, text="Ventas por Hora")

    def refresh_reports(self):
        start_date, end_date = self.get_date_range()
        self.plot_productos_mas_vendidos(start_date, end_date)
        # Aquí se llamarían las otras funciones de ploteo
        # self.plot_rendimiento_empleados(start_date, end_date)
        # self.plot_ventas_por_hora(start_date, end_date)

    def get_date_range(self):
        period = self.period_var.get()
        today = date.today()
        if period == "Hoy":
            return today, today
        elif period == "Ayer":
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif period == "Este mes":
            start_of_month = today.replace(day=1)
            return start_of_month, today
        else: # "Últimos 7 días"
            start_of_week = today - timedelta(days=6)
            return start_of_week, today

    def _clear_tab(self, tab):
        for widget in tab.winfo_children():
            widget.destroy()

    def plot_productos_mas_vendidos(self, start_date, end_date):
        self._clear_tab(self.tab_productos)

        data_cantidad, data_valor = self.controller.get_productos_mas_vendidos(start_date, end_date)

        if not data_cantidad:
            ttk.Label(self.tab_productos, text="No hay datos de ventas de productos en este período.").pack(expand=True)
            return

        # --- Gráfico por Cantidad ---
        fig_cantidad = Figure(figsize=(8, 4), dpi=100)
        ax_cantidad = fig_cantidad.add_subplot(111)

        nombres = [row['nombre'] for row in data_cantidad]
        cantidades = [row['total_vendido'] for row in data_cantidad]

        ax_cantidad.bar(nombres, cantidades, color='skyblue')
        ax_cantidad.set_title('Top Productos por Cantidad Vendida (kg)')
        ax_cantidad.set_ylabel('Kilogramos')
        ax_cantidad.tick_params(axis='x', rotation=45)
        fig_cantidad.tight_layout()

        canvas_cantidad = FigureCanvasTkAgg(fig_cantidad, master=self.tab_productos)
        canvas_cantidad.draw()
        canvas_cantidad.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # --- Gráfico por Valor ---
        # (Se podría añadir un segundo gráfico de forma similar para data_valor)
