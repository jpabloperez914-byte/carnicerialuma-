import sqlite3
from ..utils.db_manager import create_connection
from ..models.turno import Turno
from .logging_controller import LoggingController

class TurnoController:
    """
    Controlador para gestionar los turnos y cierres de caja.
    """
    def __init__(self):
        self.logging_controller = LoggingController()

    def iniciar_turno(self, empleado_id, turno_nombre, caja_inicial):
        """Inicia un nuevo turno para un empleado."""
        query = """
        INSERT INTO turnos (empleado_id, fecha, turno, hora_inicio, caja_inicial)
        VALUES (?, date('now'), ?, datetime('now', 'localtime'), ?)
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (empleado_id, turno_nombre, caja_inicial))
                turno_id = cursor.lastrowid
                conn.commit()

                log_msg = f"Inicio de turno - ID de Turno: {turno_id}, Turno: {turno_nombre}, Caja Inicial: ${caja_inicial:,.2f}"
                self.logging_controller.log_activity(empleado_id, log_msg)

                return turno_id
            except sqlite3.Error as e:
                print(f"Error al iniciar turno: {e}")
                return None
            finally:
                conn.close()
        return None

    def obtener_turno_abierto(self, empleado_id):
        """
        Busca un turno abierto (sin hora_fin) para un empleado.
        Devuelve el objeto Turno si lo encuentra, si no, None.
        """
        query = "SELECT * FROM turnos WHERE empleado_id = ? AND hora_fin IS NULL ORDER BY hora_inicio DESC LIMIT 1"
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (empleado_id,))
                data = cursor.fetchone()
                if data:
                    return Turno(**data)
            except sqlite3.Error as e:
                print(f"Error al obtener turno abierto: {e}")
            finally:
                conn.close()
        return None

    def cerrar_turno(self, turno_id, efectivo_fisico):
        """
        Cierra un turno, calcula las ventas, y crea el arqueo.
        Se ejecuta como una transacción.
        """
        conn = create_connection()
        if not conn:
            return None, "No se pudo conectar a la base de datos."

        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # 1. Obtener datos del turno (hora_inicio, caja_inicial)
            cursor.execute("SELECT empleado_id, hora_inicio, caja_inicial FROM turnos WHERE id = ?", (turno_id,))
            turno_data = cursor.fetchone()
            if not turno_data:
                raise ValueError("El turno no existe.")
            empleado_id, hora_inicio, caja_inicial = turno_data

            # 2. Calcular ventas del turno por forma de pago
            query_ventas = """
            SELECT forma_pago, SUM(total)
            FROM ventas
            WHERE fecha BETWEEN ? AND datetime('now', 'localtime')
            GROUP BY forma_pago
            """
            cursor.execute(query_ventas, (hora_inicio,))

            ventas_por_pago = {
                'efectivo': 0.0,
                'transferencia': 0.0,
                'tarjeta': 0.0
            }
            for row in cursor.fetchall():
                ventas_por_pago[row['forma_pago']] = row['SUM(total)']

            efectivo_sistema = ventas_por_pago['efectivo']
            transferencias = ventas_por_pago['transferencia']
            tarjetas = ventas_por_pago['tarjeta']

            # 3. Calcular diferencias
            caja_final_sistema = caja_inicial + efectivo_sistema
            diferencia = efectivo_fisico - caja_final_sistema

            # 4. Actualizar el turno
            query_update_turno = """
            UPDATE turnos SET hora_fin = datetime('now', 'localtime'), caja_final = ?, diferencia = ?
            WHERE id = ?
            """
            cursor.execute(query_update_turno, (efectivo_fisico, diferencia, turno_id))

            # 5. Insertar el arqueo
            query_insert_arqueo = """
            INSERT INTO arqueos (turno_id, efectivo_sistema, efectivo_fisico, transferencias, tarjetas, diferencia)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_insert_arqueo, (turno_id, efectivo_sistema, efectivo_fisico, transferencias, tarjetas, diferencia))

            conn.commit()

            log_msg = f"Cierre de turno - ID de Turno: {turno_id}, Diferencia: ${diferencia:,.2f}"
            self.logging_controller.log_activity(empleado_id, log_msg)

            reporte = {
                "caja_inicial": caja_inicial,
                "ventas_efectivo": efectivo_sistema,
                "caja_final_sistema": caja_final_sistema,
                "caja_final_fisico": efectivo_fisico,
                "ventas_transferencia": transferencias,
                "ventas_tarjeta": tarjetas,
                "diferencia": diferencia
            }
            return reporte, None

        except (sqlite3.Error, ValueError) as e:
            conn.rollback()
            return None, f"Error al cerrar el turno: {e}"
        finally:
            conn.close()
