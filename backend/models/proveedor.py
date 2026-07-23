import validadores

LONGITUD_RUC = 11

class Proveedor:
    def __init__(
        self,
        id_proveedor,
        nombre_proveedor,
        ruc=None,
        representante=None,
        telefono=None,
        correo=None,
        direccion=None,
        estado=1,
        fecha_registro=None,
    ):
        self.id_proveedor = id_proveedor
        self.nombre_proveedor = nombre_proveedor
        self.ruc = ruc
        self.representante = representante
        self.telefono = telefono
        self.correo = correo
        self.direccion = direccion
        self.estado = estado
        self.fecha_registro = fecha_registro
        self.validar()

    def validar(self):
        self.nombre_proveedor = validadores.texto_general(
            self.nombre_proveedor, "Nombre del proveedor", maximo=200
        )
        self.ruc = validadores.solo_digitos(self.ruc, "RUC", longitud=LONGITUD_RUC)
        self.representante = validadores.texto_sin_simbolos(
            self.representante, "Representante", obligatorio=False
        )
        self.telefono = validadores.solo_digitos(self.telefono, "Teléfono")
        self.correo = validadores.correo_valido(self.correo)

    def to_dict(self):
        return {
            "id_proveedor": self.id_proveedor,
            "nombre_proveedor": self.nombre_proveedor,
            "ruc": self.ruc,
            "representante": self.representante,
            "telefono": self.telefono,
            "correo": self.correo,
            "direccion": self.direccion,
            "estado": self.estado,
            "fecha_registro": (
                self.fecha_registro.isoformat()
                if hasattr(self.fecha_registro, "isoformat")
                else self.fecha_registro
            ),
        }

def crear_proveedor(datos):
    return Proveedor(
        id_proveedor=datos.get("id_proveedor"),
        nombre_proveedor=(datos.get("nombre_proveedor") or "").strip(),
        ruc=(datos.get("ruc") or "").strip() or None,
        representante=(datos.get("representante") or "").strip() or None,
        telefono=(datos.get("telefono") or "").strip() or None,
        correo=(datos.get("correo") or "").strip() or None,
        direccion=(datos.get("direccion") or "").strip() or None,
        estado=int(datos.get("estado", 1)),
        fecha_registro=datos.get("fecha_registro"),
    )
