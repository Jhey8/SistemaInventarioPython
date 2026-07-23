from flask import Blueprint

from controllers.modulo_controller import ModuloController
from sesion import login_requerido, requiere_modulo

modulo_bp = Blueprint("modulos", __name__, url_prefix="/api/modulos")
controller = ModuloController()

@modulo_bp.route("", methods=["GET"])
@login_requerido
def menu():
    return controller.menu()

@modulo_bp.route("/todos", methods=["GET"])
@requiere_modulo("perfiles")
def listar_todos():
    return controller.listar_todos()
