import validadores
from models.proveedor import crear_proveedor
from repositories.proveedor_repository import ProveedorRepository
from repositories.movimiento_repository import MovimientoRepository
from exceptions.errores import ProveedorNoEncontradoError, DatosInvalidosError

class ProveedorService:
    def __init__(self, repositorio=None, movimiento_repo=None):
        self.repositorio = repositorio or ProveedorRepository()
        self.movimiento_repo = movimiento_repo or MovimientoRepository()

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
        datos = dict(datos)
        self._validar_documentos(datos)
        proveedor = crear_proveedor(datos)
        self._validar_ruc_unico(proveedor.ruc)
        return self.repositorio.agregar(proveedor)

    def actualizar_proveedor(self, id_proveedor, datos):
        self.obtener_proveedor(id_proveedor)
        datos = dict(datos)
        datos["id_proveedor"] = id_proveedor
        self._validar_documentos(datos)
        proveedor = crear_proveedor(datos)
        self._validar_ruc_unico(proveedor.ruc, id_proveedor)
        return self.repositorio.actualizar(proveedor)

    def _validar_documentos(self, datos):
        """RUC (digito verificador SUNAT) y telefono, solo sobre datos del usuario."""
        validadores.ruc_valido(datos.get("ruc"))
        validadores.telefono_valido(datos.get("telefono"))

    def eliminar_proveedor(self, id_proveedor):
        self.obtener_proveedor(id_proveedor)
        self._verificar_sin_movimientos(id_proveedor, "eliminar")
        self.repositorio.eliminar(id_proveedor)

    def cambiar_estado_proveedor(self, id_proveedor, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        self.obtener_proveedor(id_proveedor)
        if int(estado) == 0:
            self._verificar_sin_movimientos(id_proveedor, "desactivar")
        self.repositorio.cambiar_estado(id_proveedor, estado)

    def _validar_ruc_unico(self, ruc, id_proveedor=None):
        if not ruc:
            return
        existente = self.repositorio.buscar_por_ruc(ruc)
        if existente and existente.id_proveedor != id_proveedor:
            raise DatosInvalidosError("Ya existe otro proveedor con ese RUC.")

    def _verificar_sin_movimientos(self, id_proveedor, accion):
        if self.movimiento_repo.contar_por_proveedor(id_proveedor) > 0:
            raise DatosInvalidosError(
                f"No puedes {accion} un proveedor que tiene movimientos registrados."
            )
