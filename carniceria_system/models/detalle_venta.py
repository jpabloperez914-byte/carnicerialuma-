class DetalleVenta:
    """
    Representa un artículo (un producto específico) dentro de una venta.

    Este modelo de datos contiene la información de cada línea en un ticket de venta.
    """
    def __init__(self, id, venta_id, producto_id, peso, precio_unitario, subtotal):
        """
        Inicializa un objeto DetalleVenta.

        Args:
            id (int): El ID único del detalle de la venta.
            venta_id (int): El ID de la venta a la que pertenece este detalle.
            producto_id (int): El ID del producto vendido.
            peso (float): El peso del producto vendido en kg.
            precio_unitario (float): El precio por kg del producto en el momento de la venta.
            subtotal (float): El subtotal para este artículo (peso * precio_unitario).
        """
        self.id = id
        self.venta_id = venta_id
        self.producto_id = producto_id
        self.peso = peso
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

    def __repr__(self):
        """
        Devuelve una representación en string del objeto DetalleVenta.
        """
        return (f"DetalleVenta(id={self.id}, venta_id={self.venta_id}, "
                f"producto_id={self.producto_id}, peso={self.peso}, subtotal={self.subtotal})")
