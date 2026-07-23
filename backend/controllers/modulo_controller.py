from flask import jsonify

from services.modulo_service import ModuloService
from sesion import id_perfil_actual

class ModuloController:
    def __init__(self):
        self.service = ModuloService()

    def menu(self):
        modulos = self.service.menu_de_perfil(id_perfil_actual())
        return jsonify([m.to_dict() for m in modulos])

    def listar_todos(self):
        return jsonify([m.to_dict() for m in self.service.listar_todos()])
