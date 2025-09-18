import sqlite3
from ..utils.db_manager import create_connection

class ReportesController:
    """
    Controlador para generar datos para estadísticas y reportes.
    """

    def _execute_query(self, query, params=()):
        """Ejecuta una consulta y devuelve todos los resultados."""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error al ejecutar consulta de reporte: {e}")
                return []
            finally:
                conn.close()
        return []

    def get_productos_mas_vendidos(self, start_date, end_date):
        """
        Devuelve los productos más vendidos por cantidad (kg) y valor monetario.

        Returns:
            (list, list): Tupla con dos listas: (por_cantidad, por_valor)
        """
        # Por cantidad (peso total vendido)
        query_cantidad = """
            SELECT p.nombre, SUM(dv.peso) as total_vendido
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY p.nombre
            ORDER BY total_vendido DESC
            LIMIT 10;
        """
        # Por valor (suma de subtotales)
        query_valor = """
            SELECT p.nombre, SUM(dv.subtotal) as total_valor
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY p.nombre
            ORDER BY total_valor DESC
            LIMIT 10;
        """
        params = (start_date, end_date)
        return (self._execute_query(query_cantidad, params),
                self._execute_query(query_valor, params))

    def get_rendimiento_empleados(self, start_date, end_date):
        """
        Devuelve el rendimiento de los empleados por total de ventas.
        """
        query = """
            SELECT u.nombre, COUNT(v.id) as num_ventas, SUM(v.total) as total_ventas
            FROM ventas v
            JOIN usuarios u ON v.empleado_id = u.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY u.nombre
            ORDER BY total_ventas DESC;
        """
        return self._execute_query(query, (start_date, end_date))

    def get_ventas_por_hora(self, start_date, end_date):
        """
        Devuelve el total de ventas agrupado por hora del día para identificar horas pico.
        """
        query = """
            SELECT STRFTIME('%H', fecha) as hora, SUM(total) as total_ventas
            FROM ventas
            WHERE DATE(fecha) BETWEEN ? AND ?
            GROUP BY hora
            ORDER BY hora ASC;
        """
        return self._execute_query(query, (start_date, end_date))

    def get_ganancias_totales(self, start_date, end_date):
        """
        Calcula las ganancias totales en un período.
        NOTA: Este es un cálculo simplificado. Un cálculo real necesitaría
        conocer el costo de los productos. Por ahora, es igual a las ventas totales.
        """
        query = "SELECT SUM(total) FROM ventas WHERE DATE(fecha) BETWEEN ? AND ?;"
        result = self._execute_query(query, (start_date, end_date))
        return result[0][0] if result and result[0][0] is not None else 0
