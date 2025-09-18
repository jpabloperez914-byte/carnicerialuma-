import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.usuario_controller import UsuarioController

class UsersView(ttk.Frame):
    """
    Vista para la gestión de usuarios (solo accesible por administradores).
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.usuario_controller = UsuarioController()

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        """Crea los widgets principales de la vista de usuarios."""

        # --- Frame de Controles Superiores ---
        controls_frame = ttk.Frame(self, padding=(10, 10))
        controls_frame.grid(row=0, column=0, sticky="ew")

        add_user_button = ttk.Button(controls_frame, text="Añadir Nuevo Usuario", command=self.open_add_user_dialog)
        add_user_button.pack(side="left", padx=(0, 10))

        edit_user_button = ttk.Button(controls_frame, text="Editar Usuario Seleccionado", command=self.open_edit_user_dialog)
        edit_user_button.pack(side="left", padx=(0, 10))

        toggle_active_button = ttk.Button(controls_frame, text="Activar/Desactivar Usuario", command=self.toggle_user_status)
        toggle_active_button.pack(side="left", padx=(0, 10))

        refresh_button = ttk.Button(controls_frame, text="Refrescar Lista", command=self.load_users)
        refresh_button.pack(side="right")

        # --- Treeview para mostrar los usuarios ---
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "nombre", "nivel", "activo")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre de Usuario")
        self.tree.heading("nivel", text="Nivel de Acceso")
        self.tree.heading("activo", text="Estado")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nombre", width=250)
        self.tree.column("nivel", width=150, anchor=tk.CENTER)
        self.tree.column("activo", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def load_users(self):
        """Carga o recarga los usuarios en el Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        usuarios = self.usuario_controller.obtener_todos_los_usuarios()
        for u in usuarios:
            estado = "Activo" if u.activo == 1 else "Inactivo"
            self.tree.insert("", tk.END, values=(u.id, u.nombre, u.nivel.title(), estado), tags=(estado,))

        self.tree.tag_configure("Inactivo", foreground="gray")

    def get_selected_user_id(self):
        """Obtiene el ID del usuario seleccionado en el Treeview."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un usuario de la lista.")
            return None
        return self.tree.item(selected_item)['values'][0]

    def open_add_user_dialog(self):
        messagebox.showinfo("Función no implementada", "Aquí se abrirá la ventana para añadir un nuevo usuario.")

    def open_edit_user_dialog(self):
        user_id = self.get_selected_user_id()
        if user_id:
            messagebox.showinfo("Función no implementada", f"Aquí se abrirá la ventana para editar al usuario con ID: {user_id}.")

    def toggle_user_status(self):
        user_id = self.get_selected_user_id()
        if user_id:
            # Aquí iría la lógica para llamar al controlador y cambiar el estado
            messagebox.showinfo("Función no implementada", f"Aquí se cambiará el estado del usuario con ID: {user_id}.")
            # self.load_users() # Para refrescar la lista después de la operación
