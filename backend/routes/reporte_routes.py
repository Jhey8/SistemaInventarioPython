from flask import Blueprint, request

from controllers.reporte_controller import ReporteController
from sesion import requiere_modulo

reporte_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")
controller = ReporteController()

def _filtros():
    return {
        "id_producto": request.args.get("producto"),
        "tipo_movimiento": request.args.get("tipo"),
        "id_proveedor": request.args.get("proveedor"),
        "motivo": request.args.get("motivo"),
        "fecha_desde": request.args.get("desde"),
        "fecha_hasta": request.args.get("hasta"),
        "dias": request.args.get("dias"),
        "cobertura": request.args.get("cobertura"),
    }

@reporte_bp.route("/resumen", methods=["GET"])
@requiere_modulo("dashboard")
def resumen():
    return controller.resumen()

@reporte_bp.route("/analisis", methods=["GET"])
@requiere_modulo("reportes")
def analisis():
    return controller.analisis()

@reporte_bp.route("/movimientos", methods=["GET"])
@requiere_modulo("reportes")
def movimientos():
    return controller.movimientos_reporte(_filtros())

@reporte_bp.route("/compras", methods=["GET"])
@requiere_modulo("reportes")
def compras():
    return controller.compras(_filtros())

@reporte_bp.route("/bajo-stock", methods=["GET"])
@requiere_modulo("reportes")
def bajo_stock():
    return controller.bajo_stock()

@reporte_bp.route("/reposicion", methods=["GET"])
@requiere_modulo("reportes")
def reposicion():
    return controller.reposicion(_filtros())

@reporte_bp.route("/vencimientos", methods=["GET"])
@requiere_modulo("reportes")
def vencimientos():
    return controller.vencimientos(_filtros())

@reporte_bp.route("/exportar/<reporte>", methods=["GET"])
@requiere_modulo("reportes")
def exportar(reporte):
    formato = request.args.get("formato", "excel")
    return controller.exportar(reporte, formato, _filtros())
