import hashlib
import sqlite3
from ..models.usuario import Usuario
from ..utils.db_manager import create_connection
from .logging_controller import LoggingController

def _hash_password(password):
    """Función de ayuda para hashear contraseñas."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class UsuarioController:
    """
    Controlador para gestionar las operaciones de los usuarios.
    """
    def __init__(self):
        self.logging_controller = LoggingController()

    def verificar_credenciales(self, nombre_usuario, password):
        """
        Verifica el nombre de usuario y la contraseña.

        Args:
            nombre_usuario (str): El nombre del usuario.
            password (str): La contraseña en texto plano.

        Returns:
            Usuario: El objeto Usuario si las credenciales son correctas, None en caso contrario.
        """
        password_hash = _hash_password(password)

        query = "SELECT * FROM usuarios WHERE nombre = ? AND password_hash = ? AND activo = 1"

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (nombre_usuario, password_hash))
                user_data = cursor.fetchone()

                if user_data:
                    return Usuario(id=user_data['id'], nombre=user_data['nombre'], nivel=user_data['nivel'])
            except sqlite3.Error as e:
                print(f"Error al verificar credenciales: {e}")
            finally:
                conn.close()

        return None

    def crear_usuario(self, nombre, password, nivel, creador_id):
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            nombre (str): El nombre del nuevo usuario.
            password (str): La contraseña para el nuevo usuario.
            nivel (str): 'administrador' o 'empleado'.
            creador_id (int): El ID del admin que crea el usuario.

        Returns:
            int: El ID del nuevo usuario creado, o None si falla.
        """
        password_hash = _hash_password(password)
        query = "INSERT INTO usuarios (nombre, password_hash, nivel) VALUES (?, ?, ?)"

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (nombre, password_hash, nivel))
                nuevo_usuario_id = cursor.lastrowid
                conn.commit()

                log_msg = f"Creación de usuario - Nuevo usuario: '{nombre}' (ID: {nuevo_usuario_id}), Nivel: {nivel}"
                self.logging_controller.log_activity(creador_id, log_msg)

                return nuevo_usuario_id
            except sqlite3.IntegrityError:
                print(f"Error: El usuario '{nombre}' ya existe.")
                return None
            except sqlite3.Error as e:
                print(f"Error al crear usuario: {e}")
                return None
            finally:
                conn.close()
        return None

    def obtener_usuario_por_id(self, user_id):
        """
        Obtiene un usuario por su ID.

        Args:
            user_id (int): El ID del usuario a buscar.

        Returns:
            Usuario: El objeto Usuario si se encuentra, None en caso contrario.
        """
        query = "SELECT * FROM usuarios WHERE id = ?"
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(id=user_data['id'], nombre=user_data['nombre'], nivel=user_data['nivel'], activo=user_data['activo'])
            except sqlite3.Error as e:
                print(f"Error al obtener usuario: {e}")
            finally:
                conn.close()
        return None

    def obtener_todos_los_usuarios(self):
        """
        Devuelve una lista de todos los usuarios.

        Returns:
            list[Usuario]: Una lista de objetos Usuario.
        """
        query = "SELECT * FROM usuarios"
        usuarios = []
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    usuarios.append(Usuario(id=row['id'], nombre=row['nombre'], nivel=row['nivel'], activo=row['activo']))
            except sqlite3.Error as e:
                print(f"Error al obtener todos los usuarios: {e}")
            finally:
                conn.close()
        return usuarios
