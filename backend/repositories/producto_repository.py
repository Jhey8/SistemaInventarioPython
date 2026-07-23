from repositories.database import get_connection
from models.producto import crear_producto

SELECT_BASE = (
    "SELECT p.*, c.nombre AS categoria "
    "FROM productos p JOIN categorias c ON p.categoria_id = c.id"
)

class ProductoRepository:
    def _fila_a_producto(self, fila):
        datos = dict(fila)
        if datos.get("fecha_vencimiento"):
            datos["fecha_vencimiento"] = datos["fecha_vencimiento"].isoformat()
        return crear_producto(datos)

    def listar(self, solo_activos=False):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            filtro = " WHERE p.estado = 1" if solo_activos else " WHERE p.estado <> 2"
            cursor.execute(SELECT_BASE + filtro + " ORDER BY p.id")
            return [self._fila_a_producto(f) for f in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def obtener(self, id):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(SELECT_BASE + " WHERE p.id = %s", (id,))
            fila = cursor.fetchone()
            return self._fila_a_producto(fila) if fila else None
        finally:
            cursor.close()
            conn.close()

    def agregar(self, producto):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO productos
                   (nombre, categoria_id, cantidad, precio, stock_minimo, fecha_vencimiento)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    producto.nombre,
                    producto.categoria_id,
                    producto.cantidad,
                    producto.precio,
                    producto.stock_minimo,
                    getattr(producto, "fecha_vencimiento", None),
                ),
            )
            conn.commit()
            producto.id = cursor.lastrowid
            return producto
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, producto):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE productos SET
                   nombre = %s, categoria_id = %s, cantidad = %s, precio = %s,
                   stock_minimo = %s, fecha_vencimiento = %s
                   WHERE id = %s""",
                (
                    producto.nombre,
                    producto.categoria_id,
                    producto.cantidad,
                    producto.precio,
                    producto.stock_minimo,
                    getattr(producto, "fecha_vencimiento", None),
                    producto.id,
                ),
            )
            conn.commit()
            return producto
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, id):
        self.cambiar_estado(id, 2)

    def cambiar_estado(self, id, estado):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET estado = %s WHERE id = %s", (int(estado), id)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
