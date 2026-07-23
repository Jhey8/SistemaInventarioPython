from models.categoria import crear_categoria
from repositories.categoria_repository import CategoriaRepository
from exceptions.errores import CategoriaNoEncontradaError, DatosInvalidosError

class CategoriaService:
    def __init__(self, repositorio=None):
        self.repo = repositorio or CategoriaRepository()

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
        self.repo.eliminar(id)

    def cambiar_estado_categoria(self, id, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        self.obtener_categoria(id)
        self.repo.cambiar_estado(id, estado)
