from repositories.database import get_connection
from models.movimiento import crear_movimiento
from exceptions.errores import ProductoNoEncontradoError

SELECT_HISTORIAL = (
    "SELECT m.*, p.nombre AS producto, pr.nombre_proveedor AS proveedor, "
    "       u.nombre AS usuario_nombre "
    "FROM movimientos m "
    "JOIN productos p ON m.id_producto = p.id "
    "LEFT JOIN proveedores pr ON m.id_proveedor = pr.id_proveedor "
    "LEFT JOIN usuarios u ON m.id_usuario = u.id_usuario"
)

class MovimientoRepository:
    def _fila_a_movimiento(self, fila):
        datos = dict(fila)
        movimiento = crear_movimiento(datos)

        movimiento.id = datos.get("id")
        movimiento.stock_anterior = datos.get("stock_anterior")
        movimiento.stock_nuevo = datos.get("stock_nuevo")
        movimiento.subtotal = datos.get("subtotal")
        movimiento.id_usuario = datos.get("id_usuario")
        movimiento.fecha = datos.get("fecha")
        movimiento.producto_nombre = datos.get("producto")
        movimiento.proveedor_nombre = datos.get("proveedor")
        movimiento.usuario_nombre = datos.get("usuario_nombre")
        return movimiento

    def registrar(self, movimiento):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT cantidad FROM productos WHERE id = %s FOR UPDATE",
                (movimiento.id_producto,),
            )
            fila = cursor.fetchone()
            if fila is None:
                raise ProductoNoEncontradoError(
                    f"No existe el producto con id {movimiento.id_producto}."
                )

            stock_nuevo = movimiento.aplicar_a_stock(fila["cantidad"])

            cursor.execute(
                "UPDATE productos SET cantidad = %s WHERE id = %s",
                (stock_nuevo, movimiento.id_producto),
            )
            cursor.execute(
                """INSERT INTO movimientos
                   (id_producto, id_proveedor, tipo_movimiento, motivo, numero_documento,
                    observacion, cantidad, stock_anterior, stock_nuevo, id_usuario,
                    precio_compra, subtotal)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    movimiento.id_producto,
                    movimiento.id_proveedor,
                    movimiento.tipo_movimiento,
                    movimiento.motivo,
                    movimiento.numero_documento,
                    movimiento.observacion,
                    movimiento.cantidad,
                    movimiento.stock_anterior,
                    movimiento.stock_nuevo,
                    movimiento.id_usuario,
                    movimiento.precio_compra,
                    movimiento.subtotal,
                ),
            )
            conn.commit()
            movimiento.id = cursor.lastrowid
            return movimiento
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def contar_por_proveedor(self, id_proveedor):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM movimientos WHERE id_proveedor = %s", (id_proveedor,)
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def listar(self, limite=100):
        return self.listar_filtrado({}, limite)

    def listar_filtrado(self, filtros, limite=500):
        condiciones, parametros = [], []
        if filtros.get("id_producto"):
            condiciones.append("m.id_producto = %s")
            parametros.append(int(filtros["id_producto"]))
        if filtros.get("tipo_movimiento"):
            condiciones.append("m.tipo_movimiento = %s")
            parametros.append(filtros["tipo_movimiento"].upper())
        if filtros.get("id_proveedor"):
            condiciones.append("m.id_proveedor = %s")
            parametros.append(int(filtros["id_proveedor"]))
        if filtros.get("motivo"):
            condiciones.append("m.motivo = %s")
            parametros.append(filtros["motivo"].upper())
        if filtros.get("fecha_desde"):
            condiciones.append("m.fecha >= %s")
            parametros.append(filtros["fecha_desde"] + " 00:00:00")
        if filtros.get("fecha_hasta"):
            condiciones.append("m.fecha <= %s")
            parametros.append(filtros["fecha_hasta"] + " 23:59:59")

        sql = SELECT_HISTORIAL
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        sql += " ORDER BY m.fecha DESC, m.id DESC LIMIT %s"
        parametros.append(int(limite))

        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(parametros))
            return [self._fila_a_movimiento(f) for f in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
