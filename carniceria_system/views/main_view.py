import tkinter as tk
from .login_view import LoginView
from .main_app_view import MainAppView

class App(tk.Tk):
    """
    Clase principal de la aplicación que gestiona la ventana y las vistas.
    """
    def __init__(self):
        super().__init__()

        self.title("Sistema de Administración para Carnicería")
        self.geometry("1024x768")

        # Configurar el grid para que el frame principal ocupe toda la ventana
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_user = None
        self._current_frame = None

        # Iniciar mostrando la vista de login
        self.show_login_view()

    def show_frame(self, frame_class, *args, **kwargs):
        """
        Destruye el frame actual y muestra uno nuevo.

        Args:
            frame_class: La clase de la vista (frame) a mostrar.
        """
        if self._current_frame:
            self._current_frame.destroy()

        # Pasa 'self' como el padre del nuevo frame
        # y 'self' de nuevo como el controlador de la app
        self._current_frame = frame_class(self, self, *args, **kwargs)
        self._current_frame.grid(row=0, column=0, sticky="nsew")

    def show_login_view(self):
        """Muestra la vista de inicio de sesión."""
        # El primer 'self' es el parent (la ventana principal),
        # el segundo 'self' es el app_controller
        self.show_frame(LoginView)

    def on_login_success(self, usuario):
        """
        Se ejecuta cuando el login es exitoso.

        Args:
            usuario (Usuario): El objeto del usuario que ha iniciado sesión.
        """
        self.current_user = usuario
        print(f"Login exitoso. Bienvenido {self.current_user.nombre} ({self.current_user.nivel})")

        self.show_main_app_view()

    def show_main_app_view(self):
        """Muestra la vista principal de la aplicación."""
        self.show_frame(MainAppView, current_user=self.current_user)

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.mainloop()
