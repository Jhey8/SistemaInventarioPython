import re
from datetime import date

from exceptions.errores import DatosInvalidosError

PATRON_TEXTO = re.compile(r"^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ .,'\-]+$")

PATRON_USUARIO = re.compile(r"^[A-Za-z0-9._-]+$")
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_DIGITOS = re.compile(r"^\d+$")

def texto_requerido(valor, campo, maximo=150):
    valor = (valor or "").strip()
    if not valor:
        raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
    if len(valor) > maximo:
        raise DatosInvalidosError(f"El campo '{campo}' supera los {maximo} caracteres.")
    return valor

def texto_sin_simbolos(valor, campo, obligatorio=True, maximo=150):
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
        return None
    if len(valor) > maximo:
        raise DatosInvalidosError(f"El campo '{campo}' supera los {maximo} caracteres.")
    if not PATRON_TEXTO.match(valor):
        raise DatosInvalidosError(
            f"El campo '{campo}' solo admite letras y espacios."
        )
    return valor

def usuario_valido(valor):
    valor = (valor or "").strip()
    if len(valor) < 3:
        raise DatosInvalidosError("El usuario debe tener al menos 3 caracteres.")
    if not PATRON_USUARIO.match(valor):
        raise DatosInvalidosError(
            "El usuario solo admite letras, números, punto, guion y guion bajo."
        )
    return valor

def correo_valido(valor, obligatorio=False):
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise DatosInvalidosError("El correo es obligatorio.")
        return None
    if not PATRON_CORREO.match(valor):
        raise DatosInvalidosError("El correo no tiene un formato válido.")
    return valor

def solo_digitos(valor, campo, longitud=None, obligatorio=False):
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
        return None
    if not PATRON_DIGITOS.match(valor):
        raise DatosInvalidosError(f"El campo '{campo}' solo admite números.")
    if longitud and len(valor) != longitud:
        raise DatosInvalidosError(f"El campo '{campo}' debe tener {longitud} dígitos.")
    return valor

def fecha_valida(valor, campo="Fecha", obligatorio=False):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obligatorio:
            raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
        return None
    try:
        fecha = date.fromisoformat(str(valor).strip())
    except ValueError:
        raise DatosInvalidosError(
            f"El campo '{campo}' debe tener el formato AAAA-MM-DD."
        )
    if fecha.year < 2000 or fecha.year > 2100:
        raise DatosInvalidosError(f"El campo '{campo}' está fuera de un rango válido.")
    return fecha.isoformat()
