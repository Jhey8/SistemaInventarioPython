from models.producto import crear_producto
from repositories.producto_repository import ProductoRepository
from repositories.categoria_repository import CategoriaRepository
from exceptions.errores import ProductoNoEncontradoError, DatosInvalidosError

class InventarioService:
    def __init__(self, repositorio=None, categoria_repo=None):
        self.repo = repositorio or ProductoRepository()
        self.categoria_repo = categoria_repo or CategoriaRepository()

    def _validar_categoria(self, categoria_id):
        if not categoria_id or self.categoria_repo.obtener(int(categoria_id)) is None:
            raise DatosInvalidosError("La categoría seleccionada no existe.")

    def listar_productos(self, solo_activos=False):
        return self.repo.listar(solo_activos)

    def obtener_producto(self, id):
        producto = self.repo.obtener(id)
        if producto is None:
            raise ProductoNoEncontradoError(f"No existe el producto con id {id}.")
        return producto

    def crear_producto(self, datos):
        producto = crear_producto(dict(datos))
        self._validar_categoria(producto.categoria_id)
        return self.repo.agregar(producto)

    def actualizar_producto(self, id, datos):
        self.obtener_producto(id)
        datos = dict(datos)
        datos["id"] = id
        producto = crear_producto(datos)
        self._validar_categoria(producto.categoria_id)
        return self.repo.actualizar(producto)

    def eliminar_producto(self, id):
        self.obtener_producto(id)
        self.repo.eliminar(id)

    def cambiar_estado_producto(self, id, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        self.obtener_producto(id)
        self.repo.cambiar_estado(id, estado)
