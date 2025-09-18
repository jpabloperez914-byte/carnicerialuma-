import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.db_manager import backup_database

# Placeholder para las vistas que se crearán más adelante
from .stock_view import StockView
from .sales_view import SalesView
from .reports_view import ReportsView
from .users_view import UsersView

class MainAppView(ttk.Frame):
    """
    Vista principal de la aplicación que se muestra después del login.
    Contiene la navegación principal a los diferentes módulos.
    """
    def __init__(self, parent, app_controller, current_user):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.current_user = current_user

        self.grid(row=0, column=0, sticky="nsew")

        self.create_widgets()
        self.bind_shortcuts()

    def create_widgets(self):
        # --- Configuración del Layout Principal ---
        # Fila 0 para la navegación, Fila 1 para el contenido
        self.grid_rowconfigure(0, weight=0) # Barra de navegación
        self.grid_rowconfigure(1, weight=1) # Área de contenido
        self.grid_columnconfigure(0, weight=1)

        # --- Barra de Navegación (Superior) ---
        nav_frame = ttk.Frame(self, style="Header.TFrame", padding=(10, 5))
        nav_frame.grid(row=0, column=0, sticky="ew")

        # Estilo para los botones de navegación
        style = ttk.Style(self)
        style.configure("Header.TFrame", background="#333")
        style.configure("Nav.TButton", font=("Helvetica", 10), padding=5)
        style.configure("User.TLabel", font=("Helvetica", 10), background="#333", foreground="white")

        # --- Botones de Navegación (Izquierda) ---
        sales_button = ttk.Button(nav_frame, text="F1 Ventas", command=self.show_sales_view, style="Nav.TButton")
        sales_button.pack(side="left", padx=5)

        stock_button = ttk.Button(nav_frame, text="F2 Stock", command=self.show_stock_view, style="Nav.TButton")
        stock_button.pack(side="left", padx=5)

        # Botones solo para administradores
        if self.current_user.nivel == 'administrador':
            reports_button = ttk.Button(nav_frame, text="F3 Reportes de Ventas", command=self.show_reports_view, style="Nav.TButton")
            reports_button.pack(side="left", padx=5)

            users_button = ttk.Button(nav_frame, text="F4 Gestión de Usuarios", command=self.show_users_view, style="Nav.TButton")
            users_button.pack(side="left", padx=5)

            backup_button = ttk.Button(nav_frame, text="Crear Backup", command=self.create_backup, style="Nav.TButton")
            backup_button.pack(side="left", padx=5)

        # --- Info de Usuario y Logout (Derecha) ---
        logout_button = ttk.Button(nav_frame, text="Cerrar Sesión", command=self.logout, style="Nav.TButton")
        logout_button.pack(side="right", padx=5)

        user_info_label = ttk.Label(nav_frame, text=f"{self.current_user.nombre} ({self.current_user.nivel.title()})", style="User.TLabel")
        user_info_label.pack(side="right", padx=10)

        # --- Área de Contenido ---
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Mostrar la vista de bienvenida por defecto
        self.show_welcome_view()

    def bind_shortcuts(self):
        """Asigna los atajos de teclado a las funciones de navegación."""
        self.app_controller.bind("<F1>", lambda event: self.show_sales_view())
        self.app_controller.bind("<F2>", lambda event: self.show_stock_view())
        if self.current_user.nivel == 'administrador':
            self.app_controller.bind("<F3>", lambda event: self.show_reports_view())
            self.app_controller.bind("<F4>", lambda event: self.show_users_view())

    def set_content(self, view_class):
        """Limpia el frame de contenido y muestra una nueva vista."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Instancia la nueva vista en el content_frame
        content_view = view_class(self.content_frame, self.app_controller)
        content_view.grid(row=0, column=0, sticky="nsew")


    def show_welcome_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        welcome_label = ttk.Label(self.content_frame, text="Bienvenido al Sistema de Administración", font=("Helvetica", 24, "bold"), justify="center")
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")

    def show_stock_view(self):
        print("Navegando a Gestión de Stock...")
        self.set_content(StockView) # Se activará cuando StockView exista

    def show_sales_view(self):
        print("Navegando a Punto de Venta...")
        self.set_content(SalesView) # Se activará cuando SalesView exista

    def show_reports_view(self):
        print("Navegando a Reportes...")
        self.set_content(ReportsView)

    def show_users_view(self):
        print("Navegando a Gestión de Usuarios...")
        self.set_content(UsersView) # Se activará cuando UsersView exista

    def logout(self):
        """Notifica al controlador principal para volver a la pantalla de login."""
        # Desvincular atajos para que no funcionen en la pantalla de login
        self.app_controller.unbind("<F1>")
        self.app_controller.unbind("<F2>")
        self.app_controller.unbind("<F3>")
        self.app_controller.unbind("<F4>")
        self.app_controller.show_login_view()

    def create_backup(self):
        """Llama a la función de backup y muestra el resultado."""
        path = backup_database()
        if path:
            messagebox.showinfo("Backup Exitoso", f"Copia de seguridad creada en:\n{path}")
        else:
            messagebox.showerror("Error de Backup", "No se pudo crear la copia de seguridad. Revise la consola para más detalles.")
