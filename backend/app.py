import logging

from flask import Flask, jsonify, send_from_directory

from config import FRONTEND_DIR, PUERTO, SECRET_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("inventario")
from routes.auth_routes import auth_bp
from routes.modulo_routes import modulo_bp
from routes.perfil_routes import perfil_bp
from routes.usuario_routes import usuario_bp
from routes.producto_routes import producto_bp
from routes.reporte_routes import reporte_bp
from routes.categoria_routes import categoria_bp
from routes.proveedor_routes import proveedor_bp
from routes.movimiento_routes import movimiento_bp
from exceptions.errores import InventarioError
from seed_data import sembrar_datos_si_vacio

def crear_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.secret_key = SECRET_KEY

    try:
        sembrar_datos_si_vacio()
    except Exception:
        logger.error("No se pudieron sembrar los datos iniciales", exc_info=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(modulo_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(reporte_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(proveedor_bp)
    app.register_blueprint(movimiento_bp)

    @app.route("/")
    def inicio():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(InventarioError)
    def manejar_error_dominio(error):

        return jsonify({"error": str(error)}), error.codigo_http

    @app.errorhandler(Exception)
    def error_inesperado(error):

        logger.error("Error no controlado", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno. Inténtalo de nuevo más tarde."}), 500

    return app

if __name__ == "__main__":
    aplicacion = crear_app()
    print(f"Servidor en http://localhost:{PUERTO}")
    aplicacion.run(host="0.0.0.0", port=PUERTO, debug=True)
