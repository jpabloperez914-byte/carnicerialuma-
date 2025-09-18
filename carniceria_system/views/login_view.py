import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.usuario_controller import UsuarioController

class LoginView(ttk.Frame):
    """
    Vista para el inicio de sesión de los usuarios.
    """
    def __init__(self, parent, app_controller):
        """
        Inicializa la vista de Login.

        Args:
            parent: El widget padre (la ventana principal de la app).
            app_controller: El controlador principal de la aplicación para notificar el éxito del login.
        """
        super().__init__(parent, padding="20")
        self.parent = parent
        self.app_controller = app_controller
        self.usuario_controller = UsuarioController()

        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """
        Crea y posiciona los widgets en la vista de login.
        """
        self.configure(style='TFrame')

        # Estilo
        style = ttk.Style(self)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12, 'bold'))
        style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'))

        # --- Contenedor Principal ---
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Contenedor del Formulario de Login ---
        login_container = ttk.Frame(main_frame, style='TFrame', padding="40")
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Título ---
        title_label = ttk.Label(login_container, text="Sistema de Carnicería", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # --- Usuario ---
        username_label = ttk.Label(login_container, text="Usuario:")
        username_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(login_container, textvariable=self.username_var, width=30, font=('Helvetica', 12))
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        self.username_entry.focus() # Poner el foco en el campo de usuario

        # --- Contraseña ---
        password_label = ttk.Label(login_container, text="Contraseña:")
        password_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_container, textvariable=self.password_var, show="*", width=30, font=('Helvetica', 12))
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Vincular la tecla Enter al botón de login
        self.password_entry.bind("<Return>", self.attempt_login)

        # --- Botón de Login ---
        login_button = ttk.Button(login_container, text="Iniciar Sesión", command=self.attempt_login, width=20)
        login_button.grid(row=3, column=0, columnspan=2, pady=(20, 0))

    def attempt_login(self, event=None):
        """
        Intenta realizar el login con las credenciales ingresadas.
        """
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error de Validación", "Por favor, ingrese usuario y contraseña.")
            return

        usuario = self.usuario_controller.verificar_credenciales(username, password)

        if usuario:
            # Notificar al controlador principal que el login fue exitoso
            self.app_controller.on_login_success(usuario)
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos.")
            # Limpiar el campo de contraseña
            self.password_var.set("")
