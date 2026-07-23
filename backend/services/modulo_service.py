from repositories.modulo_repository import ModuloRepository

class ModuloService:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or ModuloRepository()

    def menu_de_perfil(self, id_perfil):
        if not id_perfil:
            return []
        return self.repositorio.listar_por_perfil(id_perfil)

    def listar_todos(self):
        return self.repositorio.listar_todos()
