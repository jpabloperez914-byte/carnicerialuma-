import sqlite3
import os

# La ruta a la base de datos se define de forma relativa al proyecto.
# Se asume que el script se ejecuta desde la raíz del proyecto.
DB_NAME = 'carniceria.db'
DB_FOLDER = 'carniceria_system/database'
DATABASE_PATH = os.path.join(DB_FOLDER, DB_NAME)

def create_connection():
    """
    Crea una conexión a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Objeto de conexión o None si ocurre un error.
    """
    conn = None
    try:
        # Asegurarse de que el directorio de la base de datos exista
        os.makedirs(DB_FOLDER, exist_ok=True)
        conn = sqlite3.connect(DATABASE_PATH)
        # Habilitar el soporte para claves foráneas
        conn.execute("PRAGMA foreign_keys = 1;")
        conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        # En una aplicación real, esto debería ser manejado con un logger.

    return conn

import shutil
from datetime import datetime

def backup_database():
    """
    Crea una copia de seguridad de la base de datos en una subcarpeta 'backups'.

    Returns:
        str: La ruta del archivo de backup si fue exitoso, None si falló.
    """
    if not os.path.exists(DATABASE_PATH):
        print("Error: La base de datos no existe, no se puede hacer backup.")
        return None

    backup_folder = os.path.join(DB_FOLDER, 'backups')
    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"carniceria_backup_{timestamp}.db"
    backup_path = os.path.join(backup_folder, backup_filename)

    try:
        shutil.copyfile(DATABASE_PATH, backup_path)
        print(f"Copia de seguridad creada exitosamente en: {backup_path}")
        return backup_path
    except IOError as e:
        print(f"Error al crear la copia de seguridad: {e}")
        return None
