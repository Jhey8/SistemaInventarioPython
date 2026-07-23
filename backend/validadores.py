import re
from datetime import date

from exceptions.errores import DatosInvalidosError

PATRON_TEXTO = re.compile(r"^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ .,'\-]+$")

PATRON_USUARIO = re.compile(r"^[A-Za-z0-9._-]+$")
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_DIGITOS = re.compile(r"^\d+$")
CARACTERES_PROHIBIDOS = set("<>{}[]\\|^~`$%")
LONGITUD_MINIMA_TEXTO = 2

def texto_general(valor, campo, minimo=LONGITUD_MINIMA_TEXTO, maximo=150):
    """Nombres descriptivos: admite letras, numeros y signos comunes, pero
    rechaza caracteres peligrosos y nombres demasiado cortos."""
    valor = " ".join((valor or "").split())
    if not valor:
        raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
    if len(valor) < minimo:
        raise DatosInvalidosError(
            f"El campo '{campo}' debe tener al menos {minimo} caracteres."
        )
    if len(valor) > maximo:
        raise DatosInvalidosError(f"El campo '{campo}' supera los {maximo} caracteres.")
    if any(c in CARACTERES_PROHIBIDOS for c in valor):
        raise DatosInvalidosError(
            f"El campo '{campo}' contiene caracteres no permitidos."
        )
    return valor

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

PREFIJOS_RUC = ("10", "15", "16", "17", "20")
PESOS_RUC = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
LONGITUD_TELEFONO = 9

def ruc_valido(valor, obligatorio=False):
    """RUC peruano: 11 digitos, prefijo valido y digito verificador (modulo 11)."""
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise DatosInvalidosError("El RUC es obligatorio.")
        return None
    if not PATRON_DIGITOS.match(valor) or len(valor) != 11:
        raise DatosInvalidosError("El RUC debe tener 11 dígitos.")
    if valor[:2] not in PREFIJOS_RUC:
        raise DatosInvalidosError(
            "El RUC debe empezar con 10, 15, 16, 17 o 20."
        )
    suma = sum(int(d) * peso for d, peso in zip(valor[:10], PESOS_RUC))
    verificador = 11 - (suma % 11)
    if verificador == 10:
        verificador = 0
    elif verificador == 11:
        verificador = 1
    if verificador != int(valor[10]):
        raise DatosInvalidosError("El RUC no es válido (dígito verificador incorrecto).")
    return valor

def telefono_valido(valor, obligatorio=False):
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise DatosInvalidosError("El teléfono es obligatorio.")
        return None
    if not PATRON_DIGITOS.match(valor):
        raise DatosInvalidosError("El teléfono solo admite números.")
    if len(valor) != LONGITUD_TELEFONO:
        raise DatosInvalidosError(
            f"El teléfono debe tener {LONGITUD_TELEFONO} dígitos."
        )
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

def fecha_no_pasada(valor, campo="Fecha de vencimiento"):
    """Valida que la fecha no sea anterior a hoy (para datos que ingresa el usuario)."""
    fecha = fecha_valida(valor, campo)
    if fecha and date.fromisoformat(fecha) < date.today():
        raise DatosInvalidosError(f"El campo '{campo}' no puede ser una fecha pasada.")
    return fecha
