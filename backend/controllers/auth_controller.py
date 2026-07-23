from flask import jsonify

from services.auth_service import AuthService
from services.usuario_service import UsuarioService
from exceptions.errores import NoAutenticadoError
from sesion import iniciar_sesion, cerrar_sesion, id_usuario_actual, hay_sesion

class AuthController:
    def __init__(self):
        self.service = AuthService()
        self.usuarios = UsuarioService()

    def login(self, datos):
        usuario = self.service.autenticar(datos.get("usuario"), datos.get("clave"))
        iniciar_sesion(usuario)
        return jsonify(usuario.to_dict())

    def logout(self):
        cerrar_sesion()
        return jsonify({"mensaje": "Sesión cerrada."})

    def usuario_actual(self):
        if not hay_sesion():
            raise NoAutenticadoError("No hay una sesión activa.")
        usuario = self.service.obtener(id_usuario_actual())
        if usuario is None:
            cerrar_sesion()
            raise NoAutenticadoError("La sesión ya no es válida.")
        return jsonify(usuario.to_dict())

    def actualizar_mis_datos(self, datos):
        usuario = self.usuarios.actualizar_datos_propios(id_usuario_actual(), datos)
        return jsonify(usuario.to_dict())

    def cambiar_mi_clave(self, datos):
        self.usuarios.cambiar_clave_propia(
            id_usuario_actual(), datos.get("clave_actual"), datos.get("clave_nueva")
        )
        return jsonify({"mensaje": "Contraseña actualizada."})
