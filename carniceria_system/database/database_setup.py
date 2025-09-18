import sqlite3
import datetime
import sys
import os

# Añadir la raíz del proyecto al path para poder importar desde 'utils'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from carniceria_system.utils.security import hash_password

def setup_database():
    """
    Crea y configura la base de datos inicial del sistema.
    """
    try:
        # Conexión a la base de datos (se creará si no existe)
        conn = sqlite3.connect('carniceria_system/database/carniceria.db')
        cursor = conn.cursor()

        print("Creando tablas...")

        # --- Creación de Tablas ---

        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            nivel TEXT NOT NULL CHECK(nivel IN ('administrador', 'empleado')),
            activo INTEGER NOT NULL DEFAULT 1
        );
        ''')

        # Tabla de productos (cortes de carne)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            codigo TEXT UNIQUE,
            precio_kg REAL NOT NULL,
            stock_actual REAL NOT NULL DEFAULT 0.0,
            stock_minimo REAL NOT NULL DEFAULT 5.0,
            fecha_ingreso DATE NOT NULL,
            dias_frescura INTEGER NOT NULL DEFAULT 7
        );
        ''')

        # Tabla de registro de media res
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_res (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_llegada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            peso_inicial REAL NOT NULL,
            costo REAL NOT NULL DEFAULT 0.0,
            peso_despostado REAL DEFAULT 0.0,
            merma_calculada REAL DEFAULT 0.0,
            proveedor TEXT NOT NULL
        );
        ''')

        # Tabla de desposte
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS desposte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_res_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            peso REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            empleado_id INTEGER NOT NULL,
            FOREIGN KEY (media_res_id) REFERENCES media_res(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (empleado_id) REFERENCES usuarios(id)
        );
        ''')

        # Tabla de ventas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ticket INTEGER NOT NULL UNIQUE,
            empleado_id INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            turno TEXT NOT NULL,
            total REAL NOT NULL,
            forma_pago TEXT NOT NULL CHECK(forma_pago IN ('efectivo', 'transferencia', 'tarjeta'))
        );
        ''')

        # Tabla de detalle de ventas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            peso REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        );
        ''')

        # Tabla de promociones
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS promociones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'cantidad', 'corte_especifico'
            descuento REAL NOT NULL, -- Porcentaje o valor fijo
            activa INTEGER NOT NULL DEFAULT 1,
            fecha_inicio DATE,
            fecha_fin DATE
        );
        ''')

        # Tabla de turnos de empleados
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            turno TEXT NOT NULL, -- 'Mañana', 'Tarde'
            hora_inicio TIMESTAMP NOT NULL,
            hora_fin TIMESTAMP,
            caja_inicial REAL NOT NULL,
            caja_final REAL,
            diferencia REAL,
            FOREIGN KEY (empleado_id) REFERENCES usuarios(id)
        );
        ''')

        # Tabla de arqueos de caja
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS arqueos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turno_id INTEGER NOT NULL,
            efectivo_sistema REAL NOT NULL,
            efectivo_fisico REAL NOT NULL,
            transferencias REAL NOT NULL,
            tarjetas REAL NOT NULL,
            diferencia REAL NOT NULL,
            FOREIGN KEY (turno_id) REFERENCES turnos(id)
        );
        ''')

        # Tabla de logs de actividades críticas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            actividad TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        ''')

        print("Tablas creadas exitosamente.")

        # --- Inserción de Datos Iniciales ---

        print("Insertando y/o actualizando datos iniciales...")

        # --- Creación/Actualización del usuario admin ---
        admin_password = hash_password('admin123')
        cursor.execute("SELECT id FROM usuarios WHERE nombre = 'admin'")
        user_exists = cursor.fetchone()

        if user_exists:
            # Si existe, actualiza su contraseña para asegurar que es correcta
            cursor.execute("UPDATE usuarios SET password_hash = ?, nivel = 'administrador', activo = 1 WHERE nombre = 'admin'", (admin_password,))
            print("Usuario 'admin' actualizado con la contraseña correcta.")
        else:
            # Si no existe, lo crea
            cursor.execute("INSERT INTO usuarios (nombre, password_hash, nivel) VALUES (?, ?, ?)",
                           ('admin', admin_password, 'administrador'))
            print("Usuario 'admin' creado.")

        # Insertar cortes de carne básicos si no existen
        cortes_iniciales = [
            ('Costillas', 'C01', 1500.0, 10.0),
            ('Matambre', 'C02', 2200.0, 10.0),
            ('Vacío', 'C03', 2500.0, 10.0),
            ('Carne Molida', 'C04', 1800.0, 15.0),
            ('Puchero', 'C05', 800.0, 20.0)
        ]

        today = datetime.date.today().isoformat()

        for corte in cortes_iniciales:
            cursor.execute("SELECT id FROM productos WHERE nombre = ?", (corte[0],))
            if cursor.fetchone() is None:
                cursor.execute("""
                INSERT INTO productos (nombre, codigo, precio_kg, stock_minimo, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?)
                """, (corte[0], corte[1], corte[2], corte[3], today))

        print("Cortes de carne iniciales insertados/verificados.")

        # Guardar los cambios
        conn.commit()
        print("Datos iniciales guardados.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")

    finally:
        # Cerrar la conexión
        if conn:
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    setup_database()
