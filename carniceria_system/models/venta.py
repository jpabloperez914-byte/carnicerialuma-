import datetime

class Venta:
    """
    Representa una transacción de venta.

    Este modelo de datos contiene la información general de una venta,
    como el empleado que la realizó, la fecha, el total y la forma de pago.
    """
    def __init__(self, id, numero_ticket, empleado_id, fecha, turno, total, forma_pago):
        """
        Inicializa un objeto Venta.

        Args:
            id (int): El ID único de la venta.
            numero_ticket (int): El número de ticket correlativo.
            empleado_id (int): El ID del empleado que realizó la venta.
            fecha (str or datetime): La fecha y hora de la venta.
            turno (str): El turno en que se realizó la venta ('Mañana' o 'Tarde').
            total (float): El monto total de la venta.
            forma_pago (str): El método de pago ('efectivo', 'transferencia', 'tarjeta').
        """
        self.id = id
        self.numero_ticket = numero_ticket
        self.empleado_id = empleado_id

        if isinstance(fecha, str):
            try:
                self.fecha = datetime.datetime.fromisoformat(fecha)
            except ValueError:
                self.fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        else:
            self.fecha = fecha

        self.turno = turno
        self.total = total
        self.forma_pago = forma_pago

        # Esta lista contendrá los objetos DetalleVenta asociados
        self.detalles = []

    def __repr__(self):
        """
        Devuelve una representación en string del objeto Venta.
        """
        return (f"Venta(id={self.id}, ticket={self.numero_ticket}, "
                f"total={self.total}, fecha='{self.fecha.strftime('%Y-%m-%d %H:%M')}')")
