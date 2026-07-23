from flask import jsonify

from services.usuario_service import UsuarioService
from sesion import id_usuario_actual

class UsuarioController:
    def __init__(self):
        self.service = UsuarioService()

    def listar(self):
        return jsonify([u.to_dict() for u in self.service.listar_usuarios()])

    def crear(self, datos):
        return jsonify(self.service.crear_usuario(datos).to_dict()), 201

    def actualizar(self, id_usuario, datos):
        return jsonify(self.service.actualizar_usuario(id_usuario, datos).to_dict())

    def eliminar(self, id_usuario):
        self.service.eliminar_usuario(id_usuario, id_usuario_actual())
        return jsonify({"mensaje": "Usuario eliminado."})

    def cambiar_estado(self, id_usuario, datos):
        estado = int(datos.get("estado", 1))
        self.service.cambiar_estado_usuario(id_usuario, estado, id_usuario_actual())
        return jsonify({"mensaje": "Estado actualizado.", "estado": estado})
