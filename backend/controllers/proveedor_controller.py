from flask import jsonify

from services.proveedor_service import ProveedorService

class ProveedorController:
    def __init__(self):
        self.service = ProveedorService()

    def listar(self):
        return jsonify([p.to_dict() for p in self.service.listar_proveedores()])

    def opciones(self):
        activos = self.service.listar_proveedores(solo_activos=True)
        return jsonify([p.to_dict() for p in activos])

    def crear(self, datos):
        return jsonify(self.service.crear_proveedor(datos).to_dict()), 201

    def actualizar(self, id_proveedor, datos):
        return jsonify(self.service.actualizar_proveedor(id_proveedor, datos).to_dict())

    def eliminar(self, id_proveedor):
        self.service.eliminar_proveedor(id_proveedor)
        return jsonify({"mensaje": "Proveedor eliminado."})

    def cambiar_estado(self, id_proveedor, datos):
        estado = int(datos.get("estado", 1))
        self.service.cambiar_estado_proveedor(id_proveedor, estado)
        return jsonify({"mensaje": "Estado actualizado.", "estado": estado})
