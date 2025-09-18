import sqlite3
from ..utils.db_manager import create_connection
from ..models.media_res import MediaRes
from .producto_controller import ProductoController

class DesposteController:
    """
    Controlador para gestionar el registro de media res y el proceso de desposte.
    """
    def __init__(self):
        self.producto_controller = ProductoController()

    def registrar_media_res(self, peso_inicial, costo, proveedor):
        """Registra una nueva media res en la base de datos."""
        query = "INSERT INTO media_res (peso_inicial, costo, proveedor) VALUES (?, ?, ?)"
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (peso_inicial, costo, proveedor))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Error al registrar media res: {e}")
            finally:
                conn.close()
        return None

    def obtener_medias_res_disponibles(self):
        """Devuelve una lista de medias res que no han sido completamente despostadas."""
        # Consideramos 'disponible' si el peso despostado es menor al inicial.
        query = "SELECT * FROM media_res WHERE peso_despostado < peso_inicial ORDER BY fecha_llegada DESC"
        conn = create_connection()
        disponibles = []
        if conn:
            try:
                cursor = conn.cursor()
                rows = cursor.execute(query).fetchall()
                for row in rows:
                    disponibles.append(MediaRes(**row))
            except sqlite3.Error as e:
                print(f"Error al obtener medias res disponibles: {e}")
            finally:
                conn.close()
        return disponibles

    def obtener_todas_las_medias_res(self):
        """Devuelve una lista de todas las medias res registradas."""
        query = "SELECT * FROM media_res ORDER BY fecha_llegada DESC"
        conn = create_connection()
        todas = []
        if conn:
            try:
                cursor = conn.cursor()
                rows = cursor.execute(query).fetchall()
                for row in rows:
                    todas.append(MediaRes(**row))
            except sqlite3.Error as e:
                print(f"Error al obtener todas las medias res: {e}")
            finally:
                conn.close()
        return todas

    def realizar_desposte(self, media_res_id, cortes, empleado_id):
        """
        Registra el desposte de una media res, actualizando el stock de los cortes.
        Se ejecuta como una transacción para garantizar la integridad de los datos.

        Args:
            media_res_id (int): El ID de la media res a despostar.
            cortes (list): Lista de dicts, ej: [{'producto_id': 1, 'peso': 10.5}, ...]
            empleado_id (int): El ID del empleado que realiza el desposte.

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            total_peso_despostado = 0
            for corte in cortes:
                producto_id = corte['producto_id']
                peso = corte['peso']
                total_peso_despostado += peso

                # 1. Insertar el registro del desposte
                query_desposte = "INSERT INTO desposte (media_res_id, producto_id, peso, empleado_id) VALUES (?, ?, ?, ?)"
                cursor.execute(query_desposte, (media_res_id, producto_id, peso, empleado_id))

                # 2. Actualizar el stock del producto (usando el método del otro controlador, pero dentro de la misma transacción)
                # Para mantener la atomicidad, realizamos la operación de stock aquí.
                update_stock_query = "UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?"
                cursor.execute(update_stock_query, (peso, producto_id))

            # 3. Actualizar la media res con el peso total despostado y la merma
            update_media_res_query = """
                UPDATE media_res
                SET peso_despostado = peso_despostado + ?,
                    merma_calculada = peso_inicial - (peso_despostado + ?)
                WHERE id = ?
            """
            cursor.execute(update_media_res_query, (total_peso_despostado, total_peso_despostado, media_res_id))

            conn.commit()
            return True

        except sqlite3.Error as e:
            print(f"Error al realizar el desposte: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
