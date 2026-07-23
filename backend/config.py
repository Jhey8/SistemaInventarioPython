import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(RAIZ, "frontend")

def _cargar_env():
    ruta = os.path.join(RAIZ, ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())

_cargar_env()

PUERTO = int(os.environ.get("PUERTO", 5000))

SECRET_KEY = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo-cambiar")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "inventario"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}
