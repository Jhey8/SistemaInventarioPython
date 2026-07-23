from datetime import date

import validadores
from exceptions.errores import DatosInvalidosError

class Producto:
    def __init__(
        self,
        id,
        nombre,
        categoria_id,
        cantidad,
        precio,
        stock_minimo=5,
        categoria_nombre=None,
        estado=1,
    ):
        self.id = id
        self.nombre = nombre
        self.categoria_id = categoria_id
        self.categoria_nombre = categoria_nombre
        self.cantidad = cantidad
        self.precio = precio
        self.stock_minimo = stock_minimo
        self.estado = int(estado)
        self.validar()

    def validar(self):
        if not self.nombre or not str(self.nombre).strip():
            raise DatosInvalidosError("El nombre del producto es obligatorio.")
        if not self.categoria_id:
            raise DatosInvalidosError("Debe seleccionar una categoría.")
        if self.cantidad < 0:
            raise DatosInvalidosError("La cantidad no puede ser negativa.")
        if self.precio < 0:
            raise DatosInvalidosError("El precio no puede ser negativo.")
        if self.stock_minimo < 0:
            raise DatosInvalidosError("El stock mínimo no puede ser negativo.")

    @property
    def tipo(self):
        return "General"

    @property
    def categoria(self):
        return self.categoria_nombre

    @property
    def valor_total(self):
        return round(self.cantidad * self.precio, 2)

    @property
    def necesita_reposicion(self):
        return self.cantidad <= self.stock_minimo

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "categoria": self.categoria_nombre,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "stock_minimo": self.stock_minimo,
            "tipo": self.tipo,
            "estado": self.estado,
            "valor_total": self.valor_total,
            "necesita_reposicion": self.necesita_reposicion,
        }

class ProductoPerecedero(Producto):
    def __init__(
        self,
        id,
        nombre,
        categoria_id,
        cantidad,
        precio,
        stock_minimo=5,
        categoria_nombre=None,
        estado=1,
        fecha_vencimiento=None,
    ):
        self.fecha_vencimiento = fecha_vencimiento
        super().__init__(
            id, nombre, categoria_id, cantidad, precio, stock_minimo,
            categoria_nombre, estado,
        )

    @property
    def tipo(self):
        return "Perecedero"

    @property
    def esta_vencido(self):
        if not self.fecha_vencimiento:
            return False
        try:
            return date.fromisoformat(self.fecha_vencimiento) < date.today()
        except ValueError:
            return False

    def to_dict(self):
        datos = super().to_dict()
        datos["fecha_vencimiento"] = self.fecha_vencimiento
        datos["esta_vencido"] = self.esta_vencido
        return datos

def crear_producto(datos):
    comunes = dict(
        id=datos.get("id"),
        nombre=datos.get("nombre"),
        categoria_id=int(datos["categoria_id"]) if datos.get("categoria_id") else None,
        categoria_nombre=datos.get("categoria") or datos.get("categoria_nombre"),
        cantidad=int(datos.get("cantidad", 0)),
        precio=float(datos.get("precio", 0)),
        stock_minimo=int(datos.get("stock_minimo", 5)),
        estado=int(datos.get("estado", 1)),
    )
    fecha = validadores.fecha_valida(datos.get("fecha_vencimiento"), "Fecha de vencimiento")
    if fecha:
        return ProductoPerecedero(fecha_vencimiento=fecha, **comunes)
    return Producto(**comunes)
