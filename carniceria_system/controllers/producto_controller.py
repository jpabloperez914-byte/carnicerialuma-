import sqlite3
from ..models.producto import Producto
from ..utils.db_manager import create_connection

class ProductoController:
    """
    Controlador para gestionar las operaciones de los productos (cortes de carne).
    """

    def crear_producto(self, nombre, codigo, precio_kg, stock_minimo, dias_frescura):
        """
        Crea un nuevo producto en la base de datos.
        """
        query = """
        INSERT INTO productos (nombre, codigo, precio_kg, stock_actual, stock_minimo, fecha_ingreso, dias_frescura)
        VALUES (?, ?, ?, 0.0, ?, date('now'), ?)
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (nombre, codigo, precio_kg, stock_minimo, dias_frescura))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                print(f"Error: El producto con nombre '{nombre}' o código '{codigo}' ya existe.")
                return None
            except sqlite3.Error as e:
                print(f"Error al crear producto: {e}")
                return None
            finally:
                conn.close()
        return None

    def buscar_producto(self, termino):
        """
        Busca un producto por su código o por su nombre.
        Prioriza la búsqueda por código.
        """
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()

            # 1. Intentar buscar por código exacto
            query_codigo = "SELECT * FROM productos WHERE codigo = ?"
            cursor.execute(query_codigo, (termino,))
            data = cursor.fetchone()
            if data:
                return Producto(**data)

            # 2. Si no se encuentra, buscar por nombre (coincidencia parcial, insensible a mayúsculas)
            query_nombre = "SELECT * FROM productos WHERE nombre LIKE ? COLLATE NOCASE"
            cursor.execute(query_nombre, (f'%{termino}%',))
            data = cursor.fetchone()
            if data:
                return Producto(**data)

        except sqlite3.Error as e:
            print(f"Error al buscar producto: {e}")
        finally:
            if conn:
                conn.close()

        return None

    def obtener_todos_los_productos(self):
        """
        Devuelve una lista de todos los productos.
        """
        query = "SELECT * FROM productos ORDER BY nombre"
        productos = []
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    productos.append(Producto(**row))
            except sqlite3.Error as e:
                print(f"Error al obtener todos los productos: {e}")
            finally:
                conn.close()
        return productos

    def actualizar_stock(self, producto_id, cantidad_kg, operacion='restar'):
        """
        Actualiza el stock de un producto. La operación puede ser 'sumar' o 'restar'.
        """
        if operacion not in ['sumar', 'restar']:
            raise ValueError("La operación debe ser 'sumar' or 'restar'")

        # Usamos una sola transacción para leer y actualizar, evitando race conditions.
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Obtenemos el stock actual de forma segura
                cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,))
                result = cursor.fetchone()
                if not result:
                    print(f"Error: Producto con ID {producto_id} no encontrado.")
                    return False

                stock_actual = result['stock_actual']

                if operacion == 'sumar':
                    nuevo_stock = stock_actual + cantidad_kg
                else: # restar
                    if stock_actual < cantidad_kg:
                        print(f"Error: Stock insuficiente para el producto ID {producto_id}.")
                        return False
                    nuevo_stock = stock_actual - cantidad_kg

                # Actualizamos el stock
                update_query = "UPDATE productos SET stock_actual = ? WHERE id = ?"
                cursor.execute(update_query, (nuevo_stock, producto_id))
                conn.commit()
                return True

            except sqlite3.Error as e:
                print(f"Error al actualizar stock: {e}")
                conn.rollback() # Revertir cambios en caso de error
                return False
            finally:
                conn.close()
        return False

    def obtener_productos_con_stock_bajo(self):
        """
        Devuelve productos cuyo stock actual es menor o igual al stock mínimo.
        """
        query = "SELECT * FROM productos WHERE stock_actual <= stock_minimo AND stock_actual > 0"
        productos = []
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    productos.append(Producto(**row))
            except sqlite3.Error as e:
                print(f"Error al obtener productos con stock bajo: {e}")
            finally:
                conn.close()
        return productos
