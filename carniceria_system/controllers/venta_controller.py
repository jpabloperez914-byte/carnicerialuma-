import sqlite3
from ..utils.db_manager import create_connection
from .producto_controller import ProductoController
from .logging_controller import LoggingController

class VentaController:
    """
    Controlador para gestionar las operaciones de ventas.
    """
    def __init__(self):
        self.producto_controller = ProductoController()
        self.logging_controller = LoggingController()

    def obtener_siguiente_numero_ticket(self, cursor):
        """
        Obtiene el último número de ticket y devuelve el siguiente.
        Este método espera un cursor de una transacción existente.
        """
        cursor.execute("SELECT MAX(numero_ticket) FROM ventas")
        max_ticket = cursor.fetchone()[0]
        return (max_ticket or 0) + 1

    def crear_nueva_venta(self, empleado_id, turno, forma_pago, carrito):
        """
        Crea una nueva venta, sus detalles, y actualiza el stock.
        Todo se ejecuta dentro de una única transacción.

        Args:
            empleado_id (int): ID del empleado que realiza la venta.
            turno (str): Turno actual ('Mañana' o 'Tarde').
            forma_pago (str): Método de pago.
            carrito (list): Una lista de diccionarios, donde cada uno es un item:
                            {'producto': Producto, 'peso': float, 'subtotal': float}

        Returns:
            int: El número del ticket si la venta fue exitosa, None si falló.
        """
        conn = create_connection()
        if not conn:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        total_venta = sum(item['subtotal'] for item in carrito)

        try:
            cursor = conn.cursor()
            # Iniciar transacción
            cursor.execute("BEGIN TRANSACTION")

            # 1. Obtener el nuevo número de ticket
            nuevo_ticket = self.obtener_siguiente_numero_ticket(cursor)

            # 2. Insertar la venta principal
            query_venta = """
            INSERT INTO ventas (numero_ticket, empleado_id, fecha, turno, total, forma_pago)
            VALUES (?, ?, datetime('now', 'localtime'), ?, ?, ?)
            """
            cursor.execute(query_venta, (nuevo_ticket, empleado_id, turno, total_venta, forma_pago))
            venta_id = cursor.lastrowid

            # 3. Insertar los detalles de la venta y actualizar stock
            query_detalle = """
            INSERT INTO detalle_ventas (venta_id, producto_id, peso, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
            """
            for item in carrito:
                producto = item['producto']
                peso = item['peso']
                subtotal = item['subtotal']

                # Insertar detalle
                cursor.execute(query_detalle, (venta_id, producto.id, peso, producto.precio_kg, subtotal))

                # Actualizar stock (usando un método adaptado para transacciones)
                # NOTA: Esto requiere modificar ProductoController para aceptar un cursor externo
                # o realizar la operación de stock aquí directamente para mantener la atomicidad.
                # Por simplicidad y seguridad, la haremos aquí.

                cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto.id,))
                stock_actual = cursor.fetchone()[0]

                if stock_actual < peso:
                    # Si esto ocurre, la transacción se revertirá.
                    raise ValueError(f"Stock insuficiente para {producto.nombre}. Venta cancelada.")

                nuevo_stock = stock_actual - peso
                cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (nuevo_stock, producto.id))

            # Si todo fue bien, confirmar la transacción
            conn.commit()

            # Registrar actividad
            log_msg = f"Venta registrada - Ticket: {nuevo_ticket}, Total: ${total_venta:,.2f}"
            self.logging_controller.log_activity(empleado_id, log_msg)

            print(f"Venta #{nuevo_ticket} registrada exitosamente.")
            return nuevo_ticket

        except (sqlite3.Error, ValueError) as e:
            print(f"Error al registrar la venta. Reversando cambios. Error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
