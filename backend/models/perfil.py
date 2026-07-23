import validadores

class Perfil:
    def __init__(self, id_perfil, nombre, descripcion=None, modulos=None, estado=1):
        self.id_perfil = id_perfil
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = int(estado)

        self.modulos = [int(m) for m in (modulos or [])]
        self.validar()

    def validar(self):
        self.nombre = validadores.texto_sin_simbolos(self.nombre, "Nombre del perfil", maximo=80)
        self.descripcion = validadores.texto_requerido(
            self.descripcion, "Descripción", maximo=200
        ) if (self.descripcion or "").strip() else None

    def to_dict(self):
        return {
            "id_perfil": self.id_perfil,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "modulos": self.modulos,
        }

def crear_perfil(datos):
    return Perfil(
        id_perfil=datos.get("id_perfil"),
        nombre=datos.get("nombre"),
        descripcion=datos.get("descripcion"),
        modulos=datos.get("modulos") or [],
        estado=int(datos.get("estado", 1)),
    )
