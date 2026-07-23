from flask import jsonify

from services.categoria_service import CategoriaService

class CategoriaController:
    def __init__(self):
        self.service = CategoriaService()

    def listar(self):
        return jsonify([c.to_dict() for c in self.service.listar_categorias()])

    def opciones(self):
        activas = self.service.listar_categorias(solo_activos=True)
        return jsonify([c.to_dict() for c in activas])

    def crear(self, datos):
        return jsonify(self.service.crear_categoria(datos).to_dict()), 201

    def actualizar(self, id, datos):
        return jsonify(self.service.actualizar_categoria(id, datos).to_dict())

    def eliminar(self, id):
        self.service.eliminar_categoria(id)
        return jsonify({"mensaje": "Categoría eliminada."})

    def cambiar_estado(self, id, datos):
        estado = int(datos.get("estado", 1))
        self.service.cambiar_estado_categoria(id, estado)
        return jsonify({"mensaje": "Estado actualizado.", "estado": estado})
