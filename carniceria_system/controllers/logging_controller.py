import sqlite3
from ..utils.db_manager import create_connection

class LoggingController:
    """
    Controlador para gestionar el registro de actividades críticas.
    """
    def log_activity(self, usuario_id, actividad):
        """
        Registra una nueva actividad en la tabla de logs.

        Args:
            usuario_id (int): El ID del usuario que realiza la acción. Puede ser None si es una acción del sistema.
            actividad (str): Una descripción de la actividad realizada.
        """
        query = "INSERT INTO logs (usuario_id, actividad) VALUES (?, ?)"

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (usuario_id, actividad))
                conn.commit()
            except sqlite3.Error as e:
                # En un sistema real, si el logging falla, debería registrarse
                # en un archivo de texto como último recurso.
                print(f"ERROR CRÍTICO: No se pudo registrar el log en la base de datos. Error: {e}")
                print(f"Log no registrado: Usuario ID {usuario_id}, Actividad: {actividad}")
            finally:
                conn.close()
