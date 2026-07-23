from models.proveedor import crear_proveedor
from repositories.proveedor_repository import ProveedorRepository
from exceptions.errores import ProveedorNoEncontradoError, DatosInvalidosError

class ProveedorService:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or ProveedorRepository()

    def listar_proveedores(self, solo_activos=False):
        return self.repositorio.listar(solo_activos)

    def obtener_proveedor(self, id_proveedor):
        proveedor = self.repositorio.obtener(id_proveedor)
        if proveedor is None:
            raise ProveedorNoEncontradoError(
                f"No existe el proveedor con id {id_proveedor}."
            )
        return proveedor

    def crear_proveedor(self, datos):
        proveedor = crear_proveedor(dict(datos))
        return self.repositorio.agregar(proveedor)

    def actualizar_proveedor(self, id_proveedor, datos):
        self.obtener_proveedor(id_proveedor)
        datos = dict(datos)
        datos["id_proveedor"] = id_proveedor
        proveedor = crear_proveedor(datos)
        return self.repositorio.actualizar(proveedor)

    def eliminar_proveedor(self, id_proveedor):
        self.obtener_proveedor(id_proveedor)
        self.repositorio.eliminar(id_proveedor)

    def cambiar_estado_proveedor(self, id_proveedor, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        self.obtener_proveedor(id_proveedor)
        self.repositorio.cambiar_estado(id_proveedor, estado)
