from flask import Blueprint, request

from controllers.categoria_controller import CategoriaController
from sesion import login_requerido, requiere_modulo

categoria_bp = Blueprint("categorias", __name__, url_prefix="/api/categorias")
controller = CategoriaController()

@categoria_bp.route("/opciones", methods=["GET"])
@login_requerido
def opciones():
    return controller.opciones()

@categoria_bp.route("", methods=["GET"])
@requiere_modulo("categorias")
def listar():
    return controller.listar()

@categoria_bp.route("", methods=["POST"])
@requiere_modulo("categorias")
def crear():
    return controller.crear(request.get_json(silent=True) or {})

@categoria_bp.route("/<int:id>", methods=["PUT"])
@requiere_modulo("categorias")
def actualizar(id):
    return controller.actualizar(id, request.get_json(silent=True) or {})

@categoria_bp.route("/<int:id>", methods=["DELETE"])
@requiere_modulo("categorias")
def eliminar(id):
    return controller.eliminar(id)

@categoria_bp.route("/<int:id>/estado", methods=["PUT"])
@requiere_modulo("categorias")
def cambiar_estado(id):
    return controller.cambiar_estado(id, request.get_json(silent=True) or {})
