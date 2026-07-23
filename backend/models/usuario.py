import validadores

class Usuario:
    def __init__(
        self,
        id_usuario,
        usuario,
        clave=None,
        nombre=None,
        correo=None,
        id_perfil=None,
        estado=1,
        perfil_nombre=None,
    ):
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.clave = clave
        self.nombre = nombre
        self.correo = correo
        self.id_perfil = id_perfil
        self.estado = estado
        self.perfil_nombre = perfil_nombre
        self.validar()

    def validar(self):
        self.usuario = validadores.usuario_valido(self.usuario)
        self.nombre = validadores.texto_sin_simbolos(
            self.nombre, "Nombre", obligatorio=False
        )
        self.correo = validadores.correo_valido(self.correo)

    @property
    def activo(self):
        return int(self.estado) == 1

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "usuario": self.usuario,
            "nombre": self.nombre,
            "correo": self.correo,
            "id_perfil": self.id_perfil,
            "perfil": self.perfil_nombre,
            "estado": self.estado,
        }

def crear_usuario(datos):
    return Usuario(
        id_usuario=datos.get("id_usuario"),
        usuario=(datos.get("usuario") or "").strip(),
        clave=datos.get("clave"),
        nombre=(datos.get("nombre") or None),
        correo=(datos.get("correo") or None),
        id_perfil=int(datos["id_perfil"]) if datos.get("id_perfil") else None,
        estado=int(datos.get("estado", 1)),
        perfil_nombre=datos.get("perfil") or datos.get("perfil_nombre"),
    )
