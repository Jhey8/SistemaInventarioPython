from flask import Blueprint, request

from controllers.usuario_controller import UsuarioController
from sesion import requiere_modulo

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")
controller = UsuarioController()

@usuario_bp.route("", methods=["GET"])
@requiere_modulo("usuarios")
def listar():
    return controller.listar()

@usuario_bp.route("", methods=["POST"])
@requiere_modulo("usuarios")
def crear():
    return controller.crear(request.get_json(silent=True) or {})

@usuario_bp.route("/<int:id_usuario>", methods=["PUT"])
@requiere_modulo("usuarios")
def actualizar(id_usuario):
    return controller.actualizar(id_usuario, request.get_json(silent=True) or {})

@usuario_bp.route("/<int:id_usuario>", methods=["DELETE"])
@requiere_modulo("usuarios")
def eliminar(id_usuario):
    return controller.eliminar(id_usuario)

@usuario_bp.route("/<int:id_usuario>/estado", methods=["PUT"])
@requiere_modulo("usuarios")
def cambiar_estado(id_usuario):
    return controller.cambiar_estado(id_usuario, request.get_json(silent=True) or {})
