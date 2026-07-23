from flask import Blueprint, request

from controllers.proveedor_controller import ProveedorController
from sesion import login_requerido, requiere_modulo

proveedor_bp = Blueprint("proveedores", __name__, url_prefix="/api/proveedores")
controller = ProveedorController()

@proveedor_bp.route("/opciones", methods=["GET"])
@login_requerido
def opciones():
    return controller.opciones()

@proveedor_bp.route("", methods=["GET"])
@requiere_modulo("proveedores")
def listar():
    return controller.listar()

@proveedor_bp.route("", methods=["POST"])
@requiere_modulo("proveedores")
def crear():
    return controller.crear(request.get_json(silent=True) or {})

@proveedor_bp.route("/<int:id_proveedor>", methods=["PUT"])
@requiere_modulo("proveedores")
def actualizar(id_proveedor):
    return controller.actualizar(id_proveedor, request.get_json(silent=True) or {})

@proveedor_bp.route("/<int:id_proveedor>", methods=["DELETE"])
@requiere_modulo("proveedores")
def eliminar(id_proveedor):
    return controller.eliminar(id_proveedor)

@proveedor_bp.route("/<int:id_proveedor>/estado", methods=["PUT"])
@requiere_modulo("proveedores")
def cambiar_estado(id_proveedor):
    return controller.cambiar_estado(id_proveedor, request.get_json(silent=True) or {})
