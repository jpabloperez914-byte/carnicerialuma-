import datetime

class Turno:
    """
    Representa un turno de trabajo de un empleado.

    Contiene información sobre el inicio y fin del turno, el empleado asociado
    y los montos de caja al abrir y cerrar.
    """
    def __init__(self, id, empleado_id, fecha, turno, hora_inicio,
                 hora_fin=None, caja_inicial=0.0, caja_final=None, diferencia=None):
        """
        Inicializa un objeto Turno.

        Args:
            id (int): ID único del turno.
            empleado_id (int): ID del empleado.
            fecha (str or date): La fecha del turno.
            turno (str): 'Mañana' o 'Tarde'.
            hora_inicio (str or datetime): Marca de tiempo del inicio del turno.
            hora_fin (str or datetime, optional): Marca de tiempo del fin del turno.
            caja_inicial (float): Dinero en caja al iniciar.
            caja_final (float, optional): Dinero en caja al finalizar.
            diferencia (float, optional): Diferencia encontrada en el arqueo.
        """
        self.id = id
        self.empleado_id = empleado_id

        if isinstance(fecha, str):
            self.fecha = datetime.date.fromisoformat(fecha)
        else:
            self.fecha = fecha

        self.turno = turno

        if isinstance(hora_inicio, str):
            self.hora_inicio = datetime.datetime.fromisoformat(hora_inicio)
        else:
            self.hora_inicio = hora_inicio

        if hora_fin:
            if isinstance(hora_fin, str):
                self.hora_fin = datetime.datetime.fromisoformat(hora_fin)
            else:
                self.hora_fin = hora_fin
        else:
            self.hora_fin = None

        self.caja_inicial = caja_inicial
        self.caja_final = caja_final
        self.diferencia = diferencia

    def __repr__(self):
        return (f"Turno(id={self.id}, empleado_id={self.empleado_id}, "
                f"fecha='{self.fecha}', turno='{self.turno}')")
