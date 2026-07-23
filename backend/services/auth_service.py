from werkzeug.security import check_password_hash

from repositories.usuario_repository import UsuarioRepository
from exceptions.errores import CredencialesInvalidasError

class AuthService:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or UsuarioRepository()

    def autenticar(self, nombre_usuario, clave):
        if not nombre_usuario or not clave:
            raise CredencialesInvalidasError("Usuario y clave son obligatorios.")

        usuario = self.repositorio.buscar_por_usuario(nombre_usuario.strip())
        clave_correcta = usuario and check_password_hash(usuario.clave or "", clave)
        if not clave_correcta:
            raise CredencialesInvalidasError("Usuario o clave incorrectos.")
        if not usuario.activo:
            raise CredencialesInvalidasError("El usuario está inactivo.")
        return usuario

    def obtener(self, id_usuario):
        return self.repositorio.obtener(id_usuario)
