class Usuario:
    """
    Representa un usuario del sistema.

    Esta clase es un modelo de datos que contiene la información
    de un usuario, como su ID, nombre, nivel de acceso y estado.
    """
    def __init__(self, id, nombre, nivel, activo=1):
        """
        Inicializa un objeto Usuario.

        Args:
            id (int): El ID único del usuario.
            nombre (str): El nombre de usuario.
            nivel (str): El nivel de acceso ('administrador' or 'empleado').
            activo (int): 1 si el usuario está activo, 0 si no.
        """
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.activo = activo

    def __repr__(self):
        """
        Devuelve una representación en string del objeto Usuario.
        """
        return f"Usuario(id={self.id}, nombre='{self.nombre}', nivel='{self.nivel}', activo={self.activo})"
