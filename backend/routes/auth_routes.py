from flask import Blueprint, request

from controllers.auth_controller import AuthController
from sesion import login_requerido

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
controller = AuthController()

@auth_bp.route("/login", methods=["POST"])
def login():
    return controller.login(request.get_json(silent=True) or {})

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return controller.logout()

@auth_bp.route("/actual", methods=["GET"])
def actual():
    return controller.usuario_actual()

@auth_bp.route("/mis-datos", methods=["PUT"])
@login_requerido
def mis_datos():
    return controller.actualizar_mis_datos(request.get_json(silent=True) or {})

@auth_bp.route("/cambiar-clave", methods=["POST"])
@login_requerido
def cambiar_clave():
    return controller.cambiar_mi_clave(request.get_json(silent=True) or {})
