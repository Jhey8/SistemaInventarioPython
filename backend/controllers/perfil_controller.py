from flask import jsonify

from services.perfil_service import PerfilService

class PerfilController:
    def __init__(self):
        self.service = PerfilService()

    def listar(self):
        return jsonify([p.to_dict() for p in self.service.listar_perfiles()])

    def opciones(self):
        activos = self.service.listar_perfiles(solo_activos=True)
        return jsonify([p.to_dict() for p in activos])

    def crear(self, datos):
        return jsonify(self.service.crear_perfil(datos).to_dict()), 201

    def actualizar(self, id_perfil, datos):
        return jsonify(self.service.actualizar_perfil(id_perfil, datos).to_dict())

    def eliminar(self, id_perfil):
        self.service.eliminar_perfil(id_perfil)
        return jsonify({"mensaje": "Perfil eliminado."})

    def cambiar_estado(self, id_perfil, datos):
        estado = int(datos.get("estado", 1))
        self.service.cambiar_estado_perfil(id_perfil, estado)
        return jsonify({"mensaje": "Estado actualizado.", "estado": estado})
