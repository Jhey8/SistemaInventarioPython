from flask import Blueprint, request

from controllers.perfil_controller import PerfilController
from sesion import login_requerido, requiere_modulo

perfil_bp = Blueprint("perfiles", __name__, url_prefix="/api/perfiles")
controller = PerfilController()

@perfil_bp.route("/opciones", methods=["GET"])
@login_requerido
def opciones():
    return controller.opciones()

@perfil_bp.route("", methods=["GET"])
@requiere_modulo("perfiles")
def listar():
    return controller.listar()

@perfil_bp.route("", methods=["POST"])
@requiere_modulo("perfiles")
def crear():
    return controller.crear(request.get_json(silent=True) or {})

@perfil_bp.route("/<int:id_perfil>", methods=["PUT"])
@requiere_modulo("perfiles")
def actualizar(id_perfil):
    return controller.actualizar(id_perfil, request.get_json(silent=True) or {})

@perfil_bp.route("/<int:id_perfil>", methods=["DELETE"])
@requiere_modulo("perfiles")
def eliminar(id_perfil):
    return controller.eliminar(id_perfil)

@perfil_bp.route("/<int:id_perfil>/estado", methods=["PUT"])
@requiere_modulo("perfiles")
def cambiar_estado(id_perfil):
    return controller.cambiar_estado(id_perfil, request.get_json(silent=True) or {})
