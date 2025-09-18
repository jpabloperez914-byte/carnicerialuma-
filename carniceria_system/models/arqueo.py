class Arqueo:
    """
    Representa el arqueo de caja realizado al final de un turno.

    Almacena los montos contados físicamente y los calculados por el sistema,
    así como la diferencia resultante.
    """
    def __init__(self, id, turno_id, efectivo_sistema, efectivo_fisico,
                 transferencias, tarjetas, diferencia):
        """
        Inicializa un objeto Arqueo.

        Args:
            id (int): ID único del arqueo.
            turno_id (int): ID del turno al que corresponde el arqueo.
            efectivo_sistema (float): Total de ventas en efectivo según el sistema.
            efectivo_fisico (float): Dinero en efectivo contado físicamente.
            transferencias (float): Total de ventas por transferencia.
            tarjetas (float): Total de ventas por tarjeta.
            diferencia (float): La diferencia calculada (efectivo_fisico - efectivo_sistema).
        """
        self.id = id
        self.turno_id = turno_id
        self.efectivo_sistema = efectivo_sistema
        self.efectivo_fisico = efectivo_fisico
        self.transferencias = transferencias
        self.tarjetas = tarjetas
        self.diferencia = diferencia

    def __repr__(self):
        return (f"Arqueo(id={self.id}, turno_id={self.turno_id}, "
                f"diferencia={self.diferencia})")
