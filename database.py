# database.py

import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name="carniceria.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.crear_tablas()
        self._insertar_datos_iniciales()

    def crear_tablas(self):
        # Tabla de productos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                codigo_barras TEXT UNIQUE,
                nombre TEXT,
                categoria_id INTEGER,
                precio_por_kg REAL,
                stock_actual REAL,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        ''')

        # Tabla de categorías
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY,
                nombre TEXT UNIQUE
            )
        ''')
        
        # Tabla de ventas para reportes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas_reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT,
                usuario TEXT,
                cantidad_articulos INTEGER,
                monto_total REAL,
                metodo_pago TEXT
            )
        ''')
        
        # Tabla para el historial de media res
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_media_res (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                peso REAL,
                costo_por_kg REAL,
                total_media_res REAL
            )
        ''')

        self.conn.commit()

    def _insertar_datos_iniciales(self):
        # Verificar si hay categorías
        self.cursor.execute("SELECT COUNT(*) FROM categorias")
        if self.cursor.fetchone()[0] == 0:
            # Insertar categorías de ejemplo
            categorias = [('Res',), ('Cerdo',), ('Pollo',), ('Achuras',)]
            self.cursor.executemany("INSERT INTO categorias (nombre) VALUES (?)", categorias)
            self.conn.commit()

        # Verificar si hay productos
        self.cursor.execute("SELECT COUNT(*) FROM productos")
        if self.cursor.fetchone()[0] == 0:
            # Obtener los IDs de las categorías insertadas
            self.cursor.execute("SELECT id, nombre FROM categorias")
            categorias_map = {nombre: id for id, nombre in self.cursor.fetchall()}

            # Insertar productos de ejemplo
            productos = [
                ('001', 'Lomo', categorias_map['Res'], 25.50, 10.0),
                ('002', 'Costilla', categorias_map['Res'], 18.75, 15.5),
                ('003', 'Matambre', categorias_map['Res'], 22.00, 8.2),
                ('004', 'Solomillo de Cerdo', categorias_map['Cerdo'], 20.00, 12.0),
                ('005', 'Pechuga de Pollo', categorias_map['Pollo'], 15.00, 20.0),
                ('006', 'Chorizo', categorias_map['Achuras'], 12.50, 30.0),
            ]
            self.cursor.executemany('''
                INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_por_kg, stock_actual)
                VALUES (?, ?, ?, ?, ?)
            ''', productos)
            self.conn.commit()

    def insertar_producto(self, codigo_barras, nombre, categoria_id, precio_por_kg, stock_actual):
        try:
            self.cursor.execute('''
                INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_por_kg, stock_actual)
                VALUES (?, ?, ?, ?, ?)
            ''', (codigo_barras, nombre, categoria_id, precio_por_kg, stock_actual))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def obtener_todos_productos(self):
        self.cursor.execute('''
            SELECT p.id, p.nombre, c.nombre, p.precio_por_kg, p.stock_actual
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
        ''')
        productos = self.cursor.fetchall()
        return [
            {
                'id': p[0],
                'nombre': p[1],
                'categoria_nombre': p[2],
                'precio_por_kg': p[3],
                'stock_actual': p[4]
            }
            for p in productos
        ]

    def buscar_producto_por_codigo(self, codigo):
        self.cursor.execute('''
            SELECT p.id, p.nombre, c.nombre, p.precio_por_kg, p.stock_actual
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.codigo_barras = ?
        ''', (codigo,))
        producto = self.cursor.fetchone()
        if producto:
            return {
                'id': producto[0],
                'nombre': producto[1],
                'categoria_nombre': producto[2],
                'precio_por_kg': producto[3],
                'stock_actual': producto[4]
            }
        return None

    def obtener_categorias(self):
        self.cursor.execute("SELECT id, nombre FROM categorias")
        return self.cursor.fetchall()

    def insertar_categoria(self, nombre):
        try:
            self.cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def actualizar_stock_producto(self, producto_id, cantidad_vendida):
        self.cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?", (cantidad_vendida, producto_id))
        self.conn.commit()

    def crear_venta(self, productos, metodo_pago):
        self.conn.begin()
        try:
            total_venta = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cantidad_articulos = len(productos)
            usuario_actual = "Usuario de Prueba" 
            
            self.cursor.execute('''
                INSERT INTO ventas_reportes (fecha_hora, usuario, cantidad_articulos, monto_total, metodo_pago)
                VALUES (?, ?, ?, ?, ?)
            ''', (fecha_hora, usuario_actual, cantidad_articulos, total_venta, metodo_pago))
            
            for producto in productos:
                self.actualizar_stock_producto(producto['producto_id'], producto['cantidad'])
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def crear_historial_media_res(self, peso, costo_por_kg):
        total = peso * costo_por_kg
        fecha = datetime.date.today().strftime("%Y-%m-%d")
        try:
            self.cursor.execute('''
                INSERT INTO historial_media_res (fecha, peso, costo_por_kg, total_media_res)
                VALUES (?, ?, ?, ?)
            ''', (fecha, peso, costo_por_kg, total))
            self.conn.commit()
            return True
        except Exception:
            return False

    def obtener_historial_media_res(self):
        self.cursor.execute("SELECT * FROM historial_media_res ORDER BY fecha DESC")
        historial = self.cursor.fetchall()
        return [
            {'id': h[0], 'fecha': h[1], 'peso': h[2], 'costo_por_kg': h[3], 'total_media_res': h[4]}
            for h in historial
        ]
        
    def __del__(self):
        self.conn.close()