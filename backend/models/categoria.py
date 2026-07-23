import validadores

class Categoria:
    def __init__(self, id, nombre, descripcion=None, estado=1):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = int(estado)
        self.validar()

    def validar(self):
        self.nombre = validadores.texto_general(self.nombre, "Nombre de la categoría", maximo=80)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
        }

def crear_categoria(datos):
    return Categoria(
        id=datos.get("id"),
        nombre=(datos.get("nombre") or "").strip(),
        descripcion=(datos.get("descripcion") or None),
        estado=int(datos.get("estado", 1)),
    )
