from functools import wraps

from flask import session

from exceptions.errores import NoAutenticadoError, NoAutorizadoError

CLAVE_USUARIO = "id_usuario"
CLAVE_PERFIL = "id_perfil"

def iniciar_sesion(usuario):
    session[CLAVE_USUARIO] = usuario.id_usuario
    session[CLAVE_PERFIL] = usuario.id_perfil

def cerrar_sesion():
    session.clear()

def hay_sesion():
    return CLAVE_USUARIO in session

def id_usuario_actual():
    return session.get(CLAVE_USUARIO)

def id_perfil_actual():
    return session.get(CLAVE_PERFIL)

def login_requerido(vista):

    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not hay_sesion():
            raise NoAutenticadoError("Debe iniciar sesión para continuar.")
        return vista(*args, **kwargs)

    return envoltura

def requiere_modulo(ruta):

    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not hay_sesion():
                raise NoAutenticadoError("Debe iniciar sesión para continuar.")

            from repositories.modulo_repository import ModuloRepository

            permitidas = ModuloRepository().rutas_de_perfil(id_perfil_actual())
            if ruta not in permitidas:
                raise NoAutorizadoError("No tienes permiso para acceder a este módulo.")
            return vista(*args, **kwargs)

        return envoltura

    return decorador
