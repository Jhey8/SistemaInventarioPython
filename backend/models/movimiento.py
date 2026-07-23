from exceptions.errores import DatosInvalidosError, StockInsuficienteError

TIPO_ENTRADA = "ENTRADA"
TIPO_SALIDA = "SALIDA"
TIPO_AJUSTE = "AJUSTE"
TIPOS_VALIDOS = (TIPO_ENTRADA, TIPO_SALIDA, TIPO_AJUSTE)

class Movimiento:
    def __init__(
        self,
        id,
        id_producto,
        cantidad,
        tipo_movimiento=TIPO_ENTRADA,
        motivo="COMPRA",
        id_proveedor=None,
        numero_documento=None,
        observacion=None,
        precio_compra=None,
        id_usuario=None,
        stock_anterior=None,
        stock_nuevo=None,
        subtotal=None,
        fecha=None,
        producto_nombre=None,
        proveedor_nombre=None,
        usuario_nombre=None,
    ):
        self.id = id
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.tipo_movimiento = (tipo_movimiento or TIPO_ENTRADA).upper()
        self.motivo = (motivo or "").strip().upper() or "COMPRA"
        self.id_proveedor = id_proveedor
        self.numero_documento = numero_documento
        self.observacion = observacion
        self.precio_compra = precio_compra
        self.id_usuario = id_usuario
        self.stock_anterior = stock_anterior
        self.stock_nuevo = stock_nuevo
        self.subtotal = subtotal
        self.fecha = fecha

        self.producto_nombre = producto_nombre
        self.proveedor_nombre = proveedor_nombre
        self.usuario_nombre = usuario_nombre
        self.validar()

    def validar(self):
        if not self.id_producto:
            raise DatosInvalidosError("Debe seleccionar un producto.")
        if self.tipo_movimiento not in TIPOS_VALIDOS:
            raise DatosInvalidosError(
                "Tipo de movimiento inválido (use ENTRADA, SALIDA o AJUSTE)."
            )
        if self.cantidad is None or int(self.cantidad) < 0:
            raise DatosInvalidosError("La cantidad no puede ser negativa.")
        if self.tipo_movimiento != TIPO_AJUSTE and int(self.cantidad) <= 0:
            raise DatosInvalidosError("La cantidad debe ser mayor que cero.")

    def aplicar_a_stock(self, stock_anterior):
        stock_anterior = int(stock_anterior)
        if self.tipo_movimiento == TIPO_ENTRADA:
            stock_nuevo = stock_anterior + int(self.cantidad)
        elif self.tipo_movimiento == TIPO_SALIDA:
            stock_nuevo = stock_anterior - int(self.cantidad)
            if stock_nuevo < 0:
                raise StockInsuficienteError(
                    f"No hay stock suficiente. Disponible: {stock_anterior}, "
                    f"solicitado: {self.cantidad}."
                )
        else:
            stock_nuevo = int(self.cantidad)

        self.stock_anterior = stock_anterior
        self.stock_nuevo = stock_nuevo
        self.subtotal = self._calcular_subtotal()
        return stock_nuevo

    def _calcular_subtotal(self):
        if self.precio_compra is None:
            return None
        return round(float(self.precio_compra) * int(self.cantidad), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "id_producto": self.id_producto,
            "producto": self.producto_nombre,
            "cantidad": self.cantidad,
            "tipo_movimiento": self.tipo_movimiento,
            "motivo": self.motivo,
            "id_proveedor": self.id_proveedor,
            "proveedor": self.proveedor_nombre,
            "numero_documento": self.numero_documento,
            "observacion": self.observacion,
            "precio_compra": (
                float(self.precio_compra) if self.precio_compra is not None else None
            ),
            "subtotal": float(self.subtotal) if self.subtotal is not None else None,
            "stock_anterior": self.stock_anterior,
            "stock_nuevo": self.stock_nuevo,
            "id_usuario": self.id_usuario,
            "usuario": self.usuario_nombre,
            "fecha": (
                self.fecha.isoformat()
                if hasattr(self.fecha, "isoformat")
                else self.fecha
            ),
        }

def crear_movimiento(datos):
    precio = datos.get("precio_compra")
    return Movimiento(
        id=datos.get("id"),
        id_producto=int(datos["id_producto"]) if datos.get("id_producto") else None,
        cantidad=int(datos.get("cantidad", 0)),
        tipo_movimiento=datos.get("tipo_movimiento"),
        motivo=datos.get("motivo"),
        id_proveedor=(
            int(datos["id_proveedor"]) if datos.get("id_proveedor") else None
        ),
        numero_documento=(datos.get("numero_documento") or "").strip() or None,
        observacion=(datos.get("observacion") or "").strip() or None,
        precio_compra=float(precio) if precio not in (None, "", "null") else None,
        id_usuario=datos.get("id_usuario"),
    )
