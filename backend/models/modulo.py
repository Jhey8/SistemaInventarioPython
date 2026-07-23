class Modulo:
    def __init__(self, id_modulo, nombre, icono, ruta, orden=0, estado=1):
        self.id_modulo = id_modulo
        self.nombre = nombre
        self.icono = icono
        self.ruta = ruta
        self.orden = orden
        self.estado = estado

    def to_dict(self):
        return {
            "id_modulo": self.id_modulo,
            "nombre": self.nombre,
            "icono": self.icono,
            "ruta": self.ruta,
            "orden": self.orden,
        }

def crear_modulo(datos):
    return Modulo(
        id_modulo=datos.get("id_modulo"),
        nombre=datos.get("nombre"),
        icono=datos.get("icono"),
        ruta=datos.get("ruta"),
        orden=int(datos.get("orden", 0)),
        estado=int(datos.get("estado", 1)),
    )
