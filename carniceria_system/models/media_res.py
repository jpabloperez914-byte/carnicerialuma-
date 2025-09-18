import datetime

class MediaRes:
    """
    Representa una media res que ingresa al local.

    Este modelo de datos se utiliza para registrar la llegada de una media res,
    su peso inicial y el proveedor.
    """
    def __init__(self, id, fecha_llegada, peso_inicial, proveedor, peso_despostado=0.0, merma_calculada=0.0):
        """
        Inicializa un objeto MediaRes.

        Args:
            id (int): El ID único del registro de la media res.
            fecha_llegada (str or datetime): La fecha y hora de llegada.
            peso_inicial (float): El peso total de la media res en kg.
            proveedor (str): El nombre del proveedor.
            peso_despostado (float): El peso total obtenido tras el desposte.
            merma_calculada (float): La merma calculada tras el desposte.
        """
        self.id = id

        if isinstance(fecha_llegada, str):
            # Asume formato 'YYYY-MM-DD HH:MM:SS.ssssss' o similar de SQLite
            try:
                self.fecha_llegada = datetime.datetime.fromisoformat(fecha_llegada)
            except ValueError:
                self.fecha_llegada = datetime.datetime.strptime(fecha_llegada, '%Y-%m-%d %H:%M:%S')

        else:
            self.fecha_llegada = fecha_llegada

        self.peso_inicial = peso_inicial
        self.proveedor = proveedor
        self.peso_despostado = peso_despostado
        self.merma_calculada = merma_calculada

    def calcular_merma(self):
        """
        Calcula la merma si el peso despostado es mayor que cero.
        """
        if self.peso_despostado > 0:
            self.merma_calculada = self.peso_inicial - self.peso_despostado
        return self.merma_calculada

    def __repr__(self):
        """
        Devuelve una representación en string del objeto MediaRes.
        """
        return (f"MediaRes(id={self.id}, fecha='{self.fecha_llegada}', "
                f"peso_inicial={self.peso_inicial} kg, proveedor='{self.proveedor}')")
