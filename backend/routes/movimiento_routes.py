from flask import Blueprint, request

from controllers.movimiento_controller import MovimientoController
from sesion import requiere_modulo

movimiento_bp = Blueprint("movimientos", __name__, url_prefix="/api/movimientos")
controller = MovimientoController()

@movimiento_bp.route("", methods=["GET"])
@requiere_modulo("inventario")
def listar():
    filtros = {
        "id_producto": request.args.get("producto"),
        "tipo_movimiento": request.args.get("tipo"),
    }
    return controller.listar(filtros)

@movimiento_bp.route("", methods=["POST"])
@requiere_modulo("inventario")
def registrar():
    return controller.registrar(request.get_json(silent=True) or {})
