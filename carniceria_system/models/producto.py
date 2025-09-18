import datetime

class Producto:
    """
    Representa un producto (corte de carne) en el inventario.

    Este modelo de datos almacena toda la información relacionada con un corte de carne,
    incluyendo su nombre, precio, stock y fechas de frescura.
    """
    def __init__(self, id, nombre, codigo, precio_kg, stock_actual, stock_minimo, fecha_ingreso, dias_frescura):
        """
        Inicializa un objeto Producto.

        Args:
            id (int): El ID único del producto.
            nombre (str): El nombre del corte (e.g., 'Matambre').
            codigo (str): El código del producto, para la balanza.
            precio_kg (float): El precio por kilogramo.
            stock_actual (float): La cantidad de stock en kg.
            stock_minimo (float): El umbral de stock mínimo para alertas.
            fecha_ingreso (str or date): La fecha en que se ingresó el producto.
            dias_frescura (int): Los días de vida útil del producto.
        """
        self.id = id
        self.nombre = nombre
        self.codigo = codigo
        self.precio_kg = precio_kg
        self.stock_actual = stock_actual
        self.stock_minimo = stock_minimo

        if isinstance(fecha_ingreso, str):
            self.fecha_ingreso = datetime.date.fromisoformat(fecha_ingreso)
        else:
            self.fecha_ingreso = fecha_ingreso

        self.dias_frescura = dias_frescura

    @property
    def fecha_vencimiento(self):
        """
        Calcula la fecha de vencimiento del producto.
        """
        return self.fecha_ingreso + datetime.timedelta(days=self.dias_frescura)

    @property
    def proximo_a_vencer(self):
        """
        Verifica si el producto está a 2 días o menos de su fecha de vencimiento.
        """
        return (self.fecha_vencimiento - datetime.date.today()).days <= 2

    def __repr__(self):
        """
        Devuelve una representación en string del objeto Producto.
        """
        return (f"Producto(id={self.id}, nombre='{self.nombre}', "
                f"precio_kg={self.precio_kg}, stock_actual={self.stock_actual} kg)")
