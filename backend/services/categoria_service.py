from models.categoria import crear_categoria
from repositories.categoria_repository import CategoriaRepository
from repositories.producto_repository import ProductoRepository
from exceptions.errores import CategoriaNoEncontradaError, DatosInvalidosError

class CategoriaService:
    def __init__(self, repositorio=None, producto_repo=None):
        self.repo = repositorio or CategoriaRepository()
        self.producto_repo = producto_repo or ProductoRepository()

    def listar_categorias(self, solo_activos=False):
        return self.repo.listar(solo_activos)

    def obtener_categoria(self, id):
        categoria = self.repo.obtener(id)
        if categoria is None:
            raise CategoriaNoEncontradaError(f"No existe la categoría con id {id}.")
        return categoria

    def crear_categoria(self, datos):
        categoria = crear_categoria(dict(datos))
        if self.repo.buscar_por_nombre(categoria.nombre):
            raise DatosInvalidosError("Ya existe una categoría con ese nombre.")
        return self.repo.agregar(categoria)

    def actualizar_categoria(self, id, datos):
        self.obtener_categoria(id)
        datos = dict(datos)
        datos["id"] = id
        categoria = crear_categoria(datos)
        existente = self.repo.buscar_por_nombre(categoria.nombre)
        if existente and existente.id != id:
            raise DatosInvalidosError("Ya existe otra categoría con ese nombre.")
        return self.repo.actualizar(categoria)

    def eliminar_categoria(self, id):
        self.obtener_categoria(id)
        self._verificar_sin_productos(id, "eliminar")
        self.repo.eliminar(id)

    def cambiar_estado_categoria(self, id, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        self.obtener_categoria(id)
        if int(estado) == 0:
            self._verificar_sin_productos(id, "desactivar")
        self.repo.cambiar_estado(id, estado)

    def _verificar_sin_productos(self, id, accion):
        if self.producto_repo.contar_por_categoria(id) > 0:
            raise DatosInvalidosError(
                f"No puedes {accion} una categoría que tiene productos asignados."
            )
