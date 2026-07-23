from flask import jsonify

from services.movimiento_service import MovimientoService
from sesion import id_usuario_actual

class MovimientoController:
    def __init__(self):
        self.service = MovimientoService()

    def listar(self, filtros=None):
        movimientos = self.service.listar_filtrado(filtros or {})
        return jsonify([m.to_dict() for m in movimientos])

    def registrar(self, datos):
        movimiento = self.service.registrar_movimiento(datos, id_usuario_actual())
        return jsonify(movimiento.to_dict()), 201
