from flask import Blueprint, request

from controllers.producto_controller import ProductoController
from sesion import login_requerido, requiere_modulo

producto_bp = Blueprint("productos", __name__, url_prefix="/api/productos")
controller = ProductoController()

@producto_bp.route("/opciones", methods=["GET"])
@login_requerido
def opciones():
    return controller.opciones()

@producto_bp.route("", methods=["GET"])
@requiere_modulo("productos")
def listar():
    return controller.listar()

@producto_bp.route("", methods=["POST"])
@requiere_modulo("productos")
def crear():
    return controller.crear(request.get_json(silent=True) or {})

@producto_bp.route("/<int:id>", methods=["PUT"])
@requiere_modulo("productos")
def actualizar(id):
    return controller.actualizar(id, request.get_json(silent=True) or {})

@producto_bp.route("/<int:id>", methods=["DELETE"])
@requiere_modulo("productos")
def eliminar(id):
    return controller.eliminar(id)

@producto_bp.route("/<int:id>/estado", methods=["PUT"])
@requiere_modulo("productos")
def cambiar_estado(id):
    return controller.cambiar_estado(id, request.get_json(silent=True) or {})
