from models.movimiento import crear_movimiento, TIPO_ENTRADA, TIPO_SALIDA
from repositories.movimiento_repository import MovimientoRepository
from repositories.producto_repository import ProductoRepository
from repositories.proveedor_repository import ProveedorRepository
from exceptions.errores import ProductoNoEncontradoError, DatosInvalidosError

MOTIVO_VENTA = "VENTA"

class MovimientoService:
    def __init__(self, repositorio=None, producto_repo=None, proveedor_repo=None):
        self.repositorio = repositorio or MovimientoRepository()
        self.producto_repo = producto_repo or ProductoRepository()
        self.proveedor_repo = proveedor_repo or ProveedorRepository()

    def listar_movimientos(self, limite=100):
        return self.repositorio.listar(limite)

    def listar_filtrado(self, filtros):
        return self.repositorio.listar_filtrado(dict(filtros or {}))

    def registrar_movimiento(self, datos, id_usuario):
        movimiento = crear_movimiento(dict(datos))
        movimiento.id_usuario = id_usuario

        if self.producto_repo.obtener(movimiento.id_producto) is None:
            raise ProductoNoEncontradoError("El producto seleccionado no existe.")

        if movimiento.id_proveedor is not None:
            if self.proveedor_repo.obtener(movimiento.id_proveedor) is None:
                raise DatosInvalidosError("El proveedor seleccionado no existe.")

        if movimiento.tipo_movimiento == TIPO_ENTRADA:
            if movimiento.id_proveedor is None:
                raise DatosInvalidosError("Una entrada debe indicar el proveedor.")
            if not movimiento.numero_documento:
                raise DatosInvalidosError("El N° de documento es obligatorio en una entrada.")
            if movimiento.precio_compra is None:
                raise DatosInvalidosError("El precio de compra es obligatorio en una entrada.")

        if movimiento.tipo_movimiento == TIPO_SALIDA and movimiento.motivo == MOTIVO_VENTA:
            if not movimiento.numero_documento:
                raise DatosInvalidosError("El N° de documento de venta es obligatorio.")

        return self.repositorio.registrar(movimiento)
