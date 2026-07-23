from models.perfil import crear_perfil
from repositories.perfil_repository import PerfilRepository
from repositories.modulo_repository import ModuloRepository
from exceptions.errores import PerfilNoEncontradoError, DatosInvalidosError

RUTA_GESTION = "perfiles"
# Un perfil es "administrador" si puede gestionar usuarios o perfiles.
RUTAS_ADMIN = ("usuarios", "perfiles")

class PerfilService:
    def __init__(self, repositorio=None, modulo_repo=None):
        self.repositorio = repositorio or PerfilRepository()
        self.modulo_repo = modulo_repo or ModuloRepository()

    def listar_perfiles(self, solo_activos=False):
        return self.repositorio.listar(solo_activos)

    def obtener_perfil(self, id_perfil):
        perfil = self.repositorio.obtener(id_perfil)
        if perfil is None:
            raise PerfilNoEncontradoError(f"No existe el perfil con id {id_perfil}.")
        return perfil

    def crear_perfil(self, datos):
        perfil = crear_perfil(dict(datos))
        if self.repositorio.buscar_por_nombre(perfil.nombre):
            raise DatosInvalidosError("Ya existe un perfil con ese nombre.")
        return self.repositorio.agregar(perfil)

    def actualizar_perfil(self, id_perfil, datos):
        self.obtener_perfil(id_perfil)
        datos = dict(datos)
        datos["id_perfil"] = id_perfil
        perfil = crear_perfil(datos)

        existente = self.repositorio.buscar_por_nombre(perfil.nombre)
        if existente and existente.id_perfil != id_perfil:
            raise DatosInvalidosError("Ya existe otro perfil con ese nombre.")

        id_gestion = self._id_modulo_gestion()
        if id_gestion is not None and id_gestion not in perfil.modulos:
            if not self._otros_gestionan(id_perfil, id_gestion):
                raise DatosInvalidosError(
                    "No puedes quitar el módulo 'Perfiles': debe quedar al menos "
                    "un perfil activo que pueda gestionar los módulos."
                )
        return self.repositorio.actualizar(perfil)

    def eliminar_perfil(self, id_perfil):
        perfil = self.obtener_perfil(id_perfil)
        if self._es_admin(perfil):
            raise DatosInvalidosError("No puedes eliminar un perfil administrador.")
        self.repositorio.eliminar(id_perfil)

    def cambiar_estado_perfil(self, id_perfil, estado):
        if int(estado) not in (0, 1):
            raise DatosInvalidosError("Estado inválido.")
        perfil = self.obtener_perfil(id_perfil)
        if int(estado) == 0 and self._es_admin(perfil):
            raise DatosInvalidosError("No puedes desactivar un perfil administrador.")
        self.repositorio.cambiar_estado(id_perfil, estado)

    def _id_modulo_gestion(self):
        for modulo in self.modulo_repo.listar_todos():
            if modulo.ruta == RUTA_GESTION:
                return modulo.id_modulo
        return None

    def _otros_gestionan(self, id_perfil, id_gestion):
        return any(
            p.id_perfil != id_perfil and id_gestion in p.modulos
            for p in self.repositorio.listar(solo_activos=True)
        )

    def _es_admin(self, perfil):
        ids_admin = {m.id_modulo for m in self.modulo_repo.listar_todos() if m.ruta in RUTAS_ADMIN}
        return any(mod in perfil.modulos for mod in ids_admin)
